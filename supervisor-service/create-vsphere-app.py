#!/usr/bin/env python

#
# Construct the vsphere apps YAML that the VC API will expect by fetching raw YAML from the internet.
# It will also generate the corresponding dcli command script that you can run as-is on your VC.
#
# Example:
# $ create-vsphere-app.py -c https://raw.githubusercontent.com/jenkinsci/kubernetes-operator/master/deploy/crds/jenkins.io_jenkins_crd.yaml \
#      -p https://raw.githubusercontent.com/jenkinsci/kubernetes-operator/master/deploy/all-in-one-v1alpha2.yaml jenkins -o jenkins-vsphere-app.yaml
#
# $ create-vsphere-app.py service-id -c ~/sample-crd.yaml -p ~/sample-operator.yaml -e ~/sample-eula.txt -o ~/sample-def.yaml --display-name Sample --description "Sample description" -v "1.2.3"

__author__ = "VMware, Inc."
__copyright__ = """\
Copyright 2021 VMware, Inc.  All rights reserved. -- VMware Confidential\
"""

import argparse
import base64
import datetime
import gzip
import logging
import os
import sys
from sys import getsizeof

import requests
import yaml

FORMAT_GZIP = 'gzip'
FORMAT_PLAIN = 'plain'
YAML_MAX_PLAIN_SIZE_IN_KB = 500


def generate_dcli_command(ssd, output_file, accept_eula):
    """
    Generate the corresponding dcli command to create the service in VC.
    """
    dcli_cmd = "dcli +show-unreleased " \
               "com vmware vcenter namespacemanagement supervisorservices create " \
               "--vsphere-spec-version-spec-content=\"{}\" --vsphere-spec-version-spec-accept-eula={}".format(
        base64.b64encode(ssd.encode('UTF-8')).decode('UTF-8'), accept_eula)

    if output_file:
        # dcli command can be big, so output to a file based on the input one.
        dcli_cmd_file = os.path.splitext(output_file)[0] + "-dcli.sh"
        with open(dcli_cmd_file, 'w') as output:
            output.write(dcli_cmd)
        logging.info("dcli command generated in file {}".format(dcli_cmd_file))
    else:
        print(dcli_cmd)

    logging.info(
        "You can now use the above dcli command to create the vSphere application in your VC.")


def generate_govc_command(ssd, output_file, accept_eula):
    """
    Generate the corresponding govc command to create the service in VC from the user's computer.
    """
    govc_cmd = """#!/bin/bash
set -x

# First argument of this script is the VC IP
VC_IP=$1
if [ -z "${{VC_IP}}" ]; then
   echo "Please provide your vCenter IP: $0 <VC IP> <VC username> <VC password>"
   exit 1
fi
# Second argument of this script is the VC username
VC_USER=$2
if [ -z "${{VC_USER}}" ]; then
   echo "Please provide your vCenter username: $0 <VC IP> <VC username> <VC password>"
   exit 1
fi
# Third argument of this script is the VC password
VC_PASSWORD=$3
if [ -z "${{VC_PASSWORD}}" ]; then
   echo "Please provide your vCenter password: $0 <VC IP> <VC username> <VC password>"
   exit 1
fi

GOVC_URL="$VC_USER:$VC_PASSWORD@$VC_IP"

govc session.login -u ${{GOVC_URL}} -k -r -X POST /api/vcenter/namespace-management/supervisor-services <<< '{{\"vsphere_spec\": {{ \"version_spec\" : {{ \"content\" : \"{}\", \"accept_EULA\" : {}, \"trusted_provider\": false }}}}}}'
""".format(base64.b64encode(ssd.encode('UTF-8')).decode('UTF-8'), accept_eula)

    if output_file:
        cmd_file = os.path.splitext(output_file)[0] + "-govc.sh"
        with open(cmd_file, 'w') as output:
            output.write(govc_cmd)
        os.chmod(cmd_file, 0o755)
        logging.info("govc command generated in file {}".format(cmd_file))
    else:
        print(govc_cmd)

    logging.info(
        "You can now use the above govc >= 1.23 (https://github.com/vmware/govmomi/tree/master/govc) "
        "command to create the vSphere application in your VC.")


def update_yaml(operator_content):
    """
    Update the given YAML to add things like the namespace if it does not exist
    (TBD - should we replace if exists to make sure objects will all be created in
    the service's namespace?):

    namespace: '{{ .service.namespace }}'

    to make sure the objects are created in the service's dedicated namespace

    This method will try to read the YAML as a valid list of YAML objects.
    This will fail if the YAML already contains templated statements.
    :return The updated content or the original one on error.
    """
    updated_operator = []
    try:
        operator = yaml.safe_load_all(operator_content)
        for obj in operator:
            # Remove any null document
            if 'apiVersion' not in obj:
                continue
            updated_operator.append(obj)
            if 'namespace' in obj['metadata']:
                logging.warning(
                    "The object {}/{} already specifies a namespace, not overriding.".format(
                        obj['kind'], obj['metadata']['name']))
                continue
            # Skip cluster-wide resources
            if obj['kind'] in ['CustomResourceDefinition', 'ClusterRole', 'ClusterRoleBinding',
                               'Namespace']:
                continue

            logging.info(
                "   Updating namespace for {}/{}".format(obj['kind'], obj['metadata']['name']))
            obj['metadata']['namespace'] = "{{ .service.namespace }}"

    except yaml.YAMLError as e:
        logging.error("Could not update the operator YAML, will ignore: {}".format(e))
        return operator_content

    return yaml.safe_dump_all(updated_operator)

def update_yaml_with_psp(operator_content, service_id):
    pspContent = '''
---
apiVersion: psp.wcp.vmware.com/v1beta1
kind: PersistenceServiceConfiguration
metadata:
  name: {{ .service.prefix }}-psp-config
  namespace: {{ .service.namespace }}
spec:
  enableHostLocalStorage: true
  serviceID: '''
    operator_content += pspContent + service_id + "\n"
    return operator_content


def content_gzip(content):
    """
    Converts a content string into a raw content string(gzipped and base64 encoded)
    """
    content_bytes = gzip.compress(bytes(content, 'utf-8'))
    # we expect base64 encoded gzip data
    content_bytes_encoded = base64.b64encode(content_bytes)
    content = content_bytes_encoded.decode('utf-8')
    return content


def dump_yaml(content, fmt):
    """
    Return the YAML content in either plain or gzip format, depending on the size and
    the specified format
    We guess if this is likely to be too big or not and gzip it if yes.

    @return The tuple (format, YAML content)
    """
    if fmt == FORMAT_GZIP:
        return fmt, content_gzip(content)

    # let's gzip if too big ( >= 500 KB)
    size = getsizeof(content) / 1000
    if size >= YAML_MAX_PLAIN_SIZE_IN_KB:
        logging.info(
            "gzipping the YAML as size ({} KB) >= {} KB".format(size, YAML_MAX_PLAIN_SIZE_IN_KB))
        return FORMAT_GZIP, content_gzip(content)

    return fmt, content


def generate_vsphere_app(service_id, service_version, crd_url, operator_url, output, update, psp, fmt,
                         eula=None, display_name=None, description=None):
    """
    Generate the vsphere app YAML.

    :param service_id the ID of the service
    :param service_version the version of the service, defaults to "1.0.0"
    :param crd_url the path to the CRD YAML file
    :param operator_url the path to the operator YAML file
    :param output the optional  output file for the SupervisorServiceDefinition YAML file.
    If none given, the output will be on standard output
    :param update set to True if we want the operator YAML to be automatically updated
    (with the right {{service.namespace}} variable and so on)
    :param psp set to True if we want the operator YAML to be automatically updated
    (with the PersistenceServiceConfiguration CR for auto-creating hostlocal storageclasses)
    :param fmt the format of the generated sv service
    :param eula the EULA if specified. Default is empty
    :param display_name the display name of the service version, defaulted to the service ID
    :param description the description of the service version. Will create one if none provided
    """
    version = service_version if service_version else "1.0.0"
    label = display_name if display_name else service_id.capitalize()
    desc = description if description else "This service was generated on {date} by {script}".format(
        date=datetime.date.today(), script=os.path.basename(__file__))

    logging.info(
        "Generating service definition for: id={}, version={}".format(service_id, version))

    # Now construct the SupervisorServiceDefinition CR
    ssd_dict = {
        'apiVersion': 'appplatform.wcp.vmware.com/v1alpha2',
        'kind': 'SupervisorServiceDefinition',
        'metadata': {'name': 'placeholder'},
        'spec': {
            'serviceID': service_id,
            'version': version,
            'label': label,
            'description': desc
        }
    }
    if eula:
        ssd_dict['spec']['eula'] = eula

    if crd_url:
        crd = fetch_yaml(crd_url)
        try:
            fill_ssd_spec('crdYaml', crd, ssd_dict, fmt)
        except yaml.YAMLError as e:
            logging.error("Can not write CRD YAML from {}".format(crd_url), e)
            return 1

    if operator_url:
        operator = fetch_yaml(operator_url)
        if update:
            logging.debug("Updating the original YAML")
            operator = update_yaml(operator)
        if psp:
            logging.debug("Updating the original YAML with PersistenceServiceConfiguration")
            operator = update_yaml_with_psp(operator, service_id)
        try:
            fill_ssd_spec('operatorYaml', operator, ssd_dict, fmt)
        except yaml.YAMLError as e:
            logging.error("Can not write operator YAML from {}".format(operator_url), e)
            return 1

    # Use default_style='|' to have all fields using "|" to show content
    ssd = yaml.safe_dump(ssd_dict, default_style=None)
    if output:
        with open(output, 'w') as output_file:
            output_file.write(ssd)
        logging.info("Generated in file {}".format(output))
    else:
        print(ssd)

    accept_eula = str('eula' in ssd_dict['spec']).lower()

    generate_dcli_command(ssd, output, accept_eula)
    generate_govc_command(ssd, output, accept_eula)


def fill_ssd_spec(spec_entry, yaml_content, ssd_dict, fmt):
    """
    Fill in the spec for the given CRD or operator YAML entry.
    """
    (content_format, content) = dump_yaml(yaml_content, fmt)
    ssd_dict['spec'][spec_entry] = {}
    ssd_dict['spec'][spec_entry]['format'] = content_format

    # we have 2 different fields for content
    content_key = 'rawContent' if content_format == FORMAT_GZIP else 'content'
    ssd_dict['spec'][spec_entry][content_key] = content


def fetch_yaml(url):
    """
    Fetch the YAML from a given URL.
    @return The YAML content, not the object/dict as the YAML can contain templated info ( {{ if ...}})
    """
    content = None
    if not url.startswith('http'):
        # treat this as a file
        with open(url) as f:
            content = f.read()
    else:
        # URL
        r = requests.get(url)
        if r.status_code == requests.codes.ok:
            content = r.text
        else:
            logging.error(
                "Error fetching YAML from {}: {} ({})".format(url, r.status_code, r.text))

    return content


def extract_info_from_alpha1(v1alpha1_service):
    """
    Extract information from the given v1alpha1 SSD YAML.
    :param v1alpha1_service: the v1alpha1 service YAML
    :return: The list (service ID, version, label, description, eula)
    """
    alpha1 = yaml.safe_load(v1alpha1_service)
    spec = alpha1['spec']
    return [spec['serviceId'], spec['versions'][0], spec['label'], spec['description'],
            spec['eula']]


def main(argv):
    parser = argparse.ArgumentParser(
        description='Generate a vSphere Application YAML from a given set of YAML files')
    parser.add_argument('service_id', help='the unique service identifier')
    parser.add_argument('-c', '--crd-url', dest='crd_url',
                        help='URL to the YAML holding the operator\'s CRDs YAML. '
                             'Can be a local file or a http(s) resource.')
    parser.add_argument('-p', '--operator-url', dest='operator_url',
                        help='URL to the YAML holding the operator\'s deployment YAML. '
                             'Can be a local file or a http(s) resource.')
    parser.add_argument('-e', '--eula', dest='eula', type=argparse.FileType('r'),
                        help='EULA text file')
    parser.add_argument('-v', '--version', dest='version',
                        help='the service version')
    parser.add_argument('-o', '--output', dest='output',
                        help='the output file prefix for generating the YAML file '
                             'and the dcli command script. Will default to stdout.')
    parser.add_argument('-u', '--update', dest='update', action='store_true',
                        help='update the operator YAML file to add the namespace \'{{ '
                             '.service.namespace }}\'')
    parser.add_argument('-t', '--persistentservice', dest='psp', action='store_true',
                        help='update the operator YAML file with psp CR for auto-creation'
                             'of spbm policies and assigning the storageclass to namespace')
    parser.add_argument('-s', dest='alpha1_service', type=argparse.FileType('r'),
                        help='convert from the given v1alpha SupervisorService YAML file'
                             ' (extract label, eula and description). Information can still be '
                             'overridden using specific parameters')
    parser.add_argument('--display-name', dest='display_name',
                        help='human readable name that will be visible in the vCenter UI.'
                             ' Overriden by ALPHA1_SERVICE, if specified.')
    parser.add_argument('--format', dest='fmt', default=FORMAT_PLAIN, type=str, choices=[FORMAT_PLAIN, FORMAT_GZIP],
                        help='The format that will be used in the resulting supervisor service file.'
                            ' If the file is bigger than 500kb it gzip will be used regardless of this flag. '
                            'Default: %(default)s')
    parser.add_argument('--description', dest='description',
                        help='A human readable description of the supervisor service'
                             ' that will be visible in the vCenter UI. Overriden by ALPHA1_SERVICE, if specified.')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true',
                        help='enable debug mode')
    args = parser.parse_args(argv)

    logging.basicConfig(format='[%(levelname)s] %(message)s',
                        level='DEBUG' if args.debug else 'INFO')

    eula = None
    version = None
    description = None
    display_name = None

    if args.alpha1_service:
        (service_id, version, display_name, description, eula) = extract_info_from_alpha1(
            args.alpha1_service.read())
        # warns if service ID is not the same, we will always take the given one
        if args.service_id != service_id:
            logging.warning("service IDs do not match: specified {} instead of expected {}".format(
                args.service_id, service_id))

    eula = args.eula.read() if args.eula else eula
    version = args.version if args.version else version
    display_name = args.display_name if display_name is None else display_name
    description = args.description if description is None else description
    generate_vsphere_app(args.service_id, version, args.crd_url, args.operator_url,
                         args.output, args.update, args.psp, args.fmt, eula, display_name, description)



if __name__ == "__main__":
    main(sys.argv[1:])
