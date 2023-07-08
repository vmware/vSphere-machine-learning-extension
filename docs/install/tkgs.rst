.. _install-tkgs:

===================================
Install Kubeflow on vSphere
===================================

This section guides you to install Kubeflow on vSphere.

.. note::
	In this section, we install Kubeflow on vSphere 1.6.1. Configurations are slightly different for other versions.

Prerequisites
=============

Adhere to the following requirements before deploying Kubeflow on vSphere package on Tanzu Kubernetes Grid Service (TKG) clusters.

For the deployment on TKG clusters, Kubeflow on vSphere is installed on a Tanzu Kubernetes Cluster (TKC). So before the deployment of Kubeflow on vSphere, you need to get vSphere and TKC ready.

- For a greenfield deployment (no vSphere with Tanzu deployed on servers yet), you need to deploy vSphere with Tanzu first. Please refer to VMware official document `vSphere with Tanzu Configuration and Management <https://docs.vmware.com/en/VMware-vSphere/7.0/vmware-vsphere-with-tanzu/GUID-152BE7D2-E227-4DAA-B527-557B564D9718.html>`__.

- If you're running vSphere 7.x, to provision TKC, see `Workflow for Provisioning Tanzu Kubernetes Clusters Using the TKGS v1alpha2 API <https://docs.vmware.com/en/VMware-vSphere/7.0/vmware-vsphere-with-tanzu/GUID-3040E41B-8A54-4D23-8796-A123E7CAE3BA.html>`__.
- If you're running vSphere 8.x, to provision TKC, see `Workflow for Provisioning TKG 2 Clusters on Supervisor Using Kubectl <https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-with-tanzu-tkg/GUID-918803BD-123E-43A5-9843-250F3E20E6F2.html>`__.

- To use GPU resources on Kubeflow on vSphere, setup vGPU Tanzu Kubernetes Grid (TKG) by following `Deploy AI/ML Workloads on Tanzu Kubernetes Clusters <https://docs.vmware.com/en/VMware-vSphere/7.0/vmware-vsphere-with-tanzu/GUID-2B4CAE86-BAF4-4411-ABB1-D5F2E9EF0A3D.html>`__.

- To connect to the cluster from your client host, see `Connect to a Tanzu Kubernetes Cluster as a vCenter Single Sign-On User <https://docs.vmware.com/en/VMware-vSphere/7.0/vmware-vsphere-with-tanzu/GUID-AA3CA6DC-D4EE-47C3-94D9-53D680E43B60.html>`__.

- Install ``kapp-controller`` on the cluster. The Carvel package manager ``kapp-controller`` is preinstalled in latest TKG releases. Run command ``kubectl get pod -A | grep kapp-controller`` to double check if kapp-controller is running in your environment. (You should see a pod whose name starts with "kapp-controller".) Otherwise, if you do not have kapp-controller running in your environment, `install one release version <https://github.com/carvel-dev/kapp-controller/releases>`__ (see below for further details).

- Install ``kctrl``, a kapp-controller's native CLI on your client host. It is used to install  Kubeflow on vSphere Carvel Package. See `Installing kapp-controller CLI: kctrl <https://carvel.dev/kapp-controller/docs/v0.40.0/install/#installing-kapp-controller-cli-kctrl>`__.

Deploy Kubeflow on vSphere package on TKG clusters
===========================================================

Add package repository
----------------------

.. code-block:: shell

	kubectl create ns carvel-kubeflow
	kubectl config set-context --current --namespace=carvel-kubeflow

	kctrl package repository add --repository kubeflow-carvel-repo --url projects.registry.vmware.com/kubeflow/kubeflow-carvel-repo:1.6.1

If you get the error `kctrl: Error: the server could not find the requested resource (post packagerepositories.packaging.carvel.dev)`, this means the Carvel Custom Resource Definitions (CRD) have not been installed.
You can do so by running:

.. code-block:: shell

    kubectl apply -f https://github.com/vmware-tanzu/carvel-kapp-controller/releases/latest/download/release.yml

If kapp-controller fails to deploy, make sure the `PodSecurityPolicy <https://docs.vmware.com/en/VMware-vSphere/7.0/vmware-vsphere-with-tanzu/GUID-CD033D1D-BAD2-41C4-A46F-647A560BAEAB.html#GUID-CD033D1D-BAD2-41C4-A46F-647A560BAEAB>`__ is properly configured:

.. code-block:: shell

    kubectl create rolebinding psp:serviceaccounts --clusterrole=psp:vmware-system-restricted --group=system:serviceaccounts -n kapp-controller

You can check kapp-controller deployment by running:

.. code-block:: shell

    kubectl get deployment.apps/kapp-controller -n kapp-controller
    NAME              READY   UP-TO-DATE   AVAILABLE   AGE
    kapp-controller   0/1     0            0           2m11s

When `READY` shows `1/1`, kapp-controller is running successfully and you can add the package repository again.


Create ``config.yaml`` file
---------------------------

Create a ``config.yaml`` file which is used in Kubeflow on vSphere installation later.

.. note::
	This YAML file is created based on values schema of Kubeflow on vSphere package, i.e. the configurations. More details are found in :ref:`values schema table`.

.. code-block:: shell

    cat <<EOF > config.yaml

    service_type: "LoadBalancer"

    IP_address: ""
    CD_REGISTRATION_FLOW: True
    EOF

Install Kubeflow on vSphere package
-------------------------------------------

.. code-block:: shell
  
  kctrl package install \
      --wait-check-interval 5s \
      --wait-timeout 30m0s \
      --package-install kubeflow \
      --package kubeflow.community.tanzu.vmware.com \
      --version 1.6.1 \
      --values-file config.yaml

This takes a few minutes, so please wait patiently. You see a "Succeeded" message in the end if the installation is successful.

    .. image:: ../_static/install-tkgs-deploySucceed.png

To follow the installation process, you can use:

.. code-block:: shell

    kctrl package installed status -i kubeflow

Access Kubeflow on vSphere
----------------------------------

Now, access the deployed Kubeflow on vSphere in browser and start using it.

To access Kubeflow on vSphere, you need to get the IP address of the service. There are three options.

- When you set ``service_type`` to ``LoadBalancer``, run the following command and visit ``EXTERNAL-IP`` of ``istio-ingressgateway``.

  .. code-block:: shell

      kubectl get svc istio-ingressgateway -n istio-system

      # example output:
      # NAME                   TYPE           CLUSTER-IP       EXTERNAL-IP      PORT(S)                                                                      AGE
      # istio-ingressgateway   LoadBalancer   198.51.217.125   10.105.151.142   15021:31063/TCP,80:30926/TCP,443:31275/TCP,31400:30518/TCP,15443:31204/TCP   11d
      
      # In this example, visit http://10.105.151.142:80
- When you set ``service_type`` to ``NodePort``, run the following command and visit ``nodeIP:nodePort``.

  .. code-block:: shell

      kubectl get svc istio-ingressgateway -n istio-system

      # example output:
      # NAME                   TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)                                                                      AGE
      # istio-ingressgateway   NodePort   198.51.217.125   <none>        15021:31063/TCP,80:30926/TCP,443:31275/TCP,31400:30518/TCP,15443:31204/TCP   11d

      kubectl get nodes -o wide

      # example output:
      # NAME                                                      STATUS   ROLES                  AGE   VERSION            INTERNAL-IP     EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION      CONTAINER-RUNTIME
      # v1a2-v1-23-8-tkc-v100-8c-dcpvc-4zct9                      Ready    control-plane,master   26d   v1.23.8+vmware.2   10.105.151.73   <none>        Ubuntu 20.04.4 LTS   5.4.0-124-generic   containerd://1.6.6
      # v1a2-v1-23-8-tkc-v100-8c-workers-zwfx4-77b7df85f7-f7f6f   Ready    <none>                 26d   v1.23.8+vmware.2   10.105.151.74   <none>        Ubuntu 20.04.4 LTS   5.4.0-124-generic   containerd://1.6.6
      # v1a2-v1-23-8-tkc-v100-8c-workers-zwfx4-77b7df85f7-l5mp5   Ready    <none>                 26d   v1.23.8+vmware.2   10.105.151.75   <none>        Ubuntu 20.04.4 LTS   5.4.0-124-generic   containerd://1.6.6

      ## In this example, anyone of the following works:
      # http://10.105.151.73:30926
      # http://10.105.151.74:30926
      # http://10.105.151.75:30926
- Use ``port-forward``. Then visit the IP address of your client host.

  .. code-block:: shell

      kubectl port-forward -n istio-system svc/istio-ingressgateway --address 0.0.0.0 8080:80

      # if you run the command locally, visit http://localhost:8080

Then you use the IP to access Kubeflow on vSphere in browser.

    .. image:: ../_static/install-tkgs-login.png

If you did not make any change to the Kubeflow on vSphere configurations, the default login credentials are: ``user@example.com / 12341234``.

For the first time you login after deployment, you are guided to namespace creation page.

    .. image:: ../_static/install-tkgs-createNS.png

Then, the Kubeflow on vSphere web UI looks like below:

    .. image:: ../_static/install-tkgs-home.png

.. _configure pod security policy:

Configure pod permission and security policy
--------------------------------------------

For your first time deployment, you need to configure pod permission and security policy in order to create and configure new pods. 
This is important because pod creation is needed for many Kubeflow on vSphere functions, such as Notebook Server creation.

To check your own user profile:

.. code-block:: shell

    kubectl get profile
    kubectl get serviceaccount,authorizationpolicies,rolebinding -n <namespace_name>

And to configure ``pod-security-policy``, run the following command on your client host:

.. code-block:: shell

    cat << EOF | kubectl apply -f -
    kind: RoleBinding
    apiVersion: rbac.authorization.k8s.io/v1
    metadata:
      name: rb-all-sa_ns-<namespace_name>
      namespace: <namespace_name>
    roleRef:
      kind: ClusterRole
      name: psp:vmware-system-privileged
      apiGroup: rbac.authorization.k8s.io
    subjects:
    - kind: Group
      apiGroup: rbac.authorization.k8s.io
      name: system:serviceaccounts:<namespace_name>
    EOF

.. note::
        Remember to replace ``namespace_name`` to the namespace that you work in.

Troubleshooting
===============

More ``kctrl`` commands are found in `kapp-controller's native CLI documentation <https://carvel.dev/kapp-controller/docs/v0.43.2/management-command/>`__.

Delete the Kubeflow on vSphere package
----------------------------------------------

To uninstall the Kubeflow on vSphere package:

   .. code-block:: shell

      kctrl package installed delete --package-install kubeflow

When deleting the Kubeflow on vSphere package, some resources may get stuck at ``deleting`` status. To solve this problem:

   .. code-block:: shell

      # take namespace knative-serving as an example
      kubectl patch ns knative-serving -p '{"spec":{"finalizers":null}}'
      kubectl delete ns knative-serving --grace-period=0 --force

Reconciliation issue
--------------------

Kapp-controller keeps reconciling Kubeflow on vSphere, which prevents you from editing a Kubeflow on vSphere resource. In this case, you may pause and then trigger the reconciliation of Kubeflow on vSphere to solve this issue.


- To pause the reconciliation of a package installation:

   .. code-block:: shell

      kctrl package installed pause --package-install kubeflow

- To trigger the reconciliation of a package installation:

   .. code-block:: shell

      kctrl package installed kick --package-install kubeflow --wait --wait-check-interval 5s --wait-timeout 30m0s

Inspect package installation
----------------------------

- To check the status of package installation:

   .. code-block:: shell

      kubectl get PackageInstall kubeflow -o yaml

- To print the status of App created by package installation:

   .. code-block:: shell

     kctrl package installed status --package-install kubeflow

Update package configurations
-----------------------------

To update the configuration of Kubeflow on vSphere package using an updated configuration file (i.e., ``config.yaml``):

.. code-block:: shell

    kctrl package installed update --package-install kubeflow --values-file config.yaml

.. _values schema table:

Values schema
-------------

To inspect values schema (configurations) of the Kubeflow on vSphere package, run the following command:

.. code-block:: shell

	kctrl package available get -p kubeflow.community.tanzu.vmware.com/1.6.1 --values-schema

We summarize some important values schema in below table.

====================  ============ ======= =======================================================================================================================================
Key                   Default      Type    Description
====================  ============ ======= =======================================================================================================================================
CD_REGISTRATION_FLOW  true         boolean Turn on Registration Flow, so that the Kubeflow on vSphere Central Dashboard prompts new users to create a namespace (profile).
IP_address            ""           string  ``EXTERNAL_IP`` address of ``istio-ingressgateway``, valid only if ``service_type`` is ``LoadBalancer``.
service_type          LoadBalancer string  Service type of ``istio-ingressgateway``. Available options: ``LoadBalancer`` or ``NodePort``.
====================  ============ ======= =======================================================================================================================================

Notebook Server creation failure
--------------------------------

When you try to create a Notebook Server, you may meet the following error:

.. code-block:: text

    FailedCreate 1s (x2 over 1s) statefulset-controller create Pod test-01-0 in StatefulSet test-01 failed error: pods “test-01-0” is forbidden: PodSecurityPolicy: unable to admit pod: []

This error occurs because Notebook Server creation needs pod creation, and you did not configure the pod security policy correctly. To solve this error, you need to configure pod security policy based on :ref:`configure pod security policy`.
