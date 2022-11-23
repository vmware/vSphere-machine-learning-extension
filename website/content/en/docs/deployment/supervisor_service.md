+++
title = "Kubeflow Supervisor Service"
description = "Deploy Kubeflow 1.6 with Supervisor Service"
weight = 50
+++

> For VI Admin to deploy Kubeflow on your clusters

## Preparation
---
#### A Tanzu Kubernetes Cluster
Please setup a Tanzu Kubernetes Cluster follow the guides:
- [Create and configure a vSphere Namespace](../namespace)
- [Create a Tanzu Kubernetes Cluster](../cluster)


#### Configure a Proxy
If your network have trouble accessing one of the following Docker registries:
- docker.io
- gcr.io
- quay.io

Please refer to [**Configure a Proxy**](../troubleshooting/proxy) to configure a proxy.


## Enable the Kubeflow Supervisor Service
---

1. Add Kubeflow Supervisor Service to allow-list on vCenter Server.
   ```bash
   # please replace it with your vCenter Server IP
   export VC_IP=<The_IP_address_of_vCenter_server>

   ssh root@${VC_IP}

   # List of SupervisorService IDs allowed to be created
   cat /etc/vmware/wcp/supervisor-services-allow-list.txt

   # Add kubeflow
   echo -e "\n# Kubeflow\nkubeflow" >> /etc/vmware/wcp/supervisor-services-allow-list.txt

   # Check again. The service would take a maximum of 10sec to reload the list into memory.
   cat /etc/vmware/wcp/supervisor-services-allow-list.txt
   ```
2. Download service YAML file at [kubeflow-service-def.yaml](https://github.com/vmware/ml-ops-platform-for-vsphere/blob/main/supervisor-service/kubeflow-service-def.yaml)
3. [Add a Supervisor Service to vCenter Server](https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-with-tanzu-services-workloads/GUID-A0A5F6D4-87A4-46CA-A50A-33664F43F299.html)
4. [Install a Supervisor Service on Supervisors](https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-with-tanzu-services-workloads/GUID-4843E6C6-747E-43B1-AC55-8F02299CC10E.html)


## Install Kubeflow
---

1. Set constants and login to the Supervisor Cluster.
    ```bash
    ## Supervisor Cluster info
    export VSPHERE_SUPERVISOR_CLUSTER_IP=<The_IP_address_of_Supervisor_Cluster>
    ## the namespace of the TKG you created
    export VSPHERE_NAMESPACE=namespace-kubeflow
    ## the name of the TKG you created
    export VSPHERE_TKGS=tkgs-kubeflow
    ## vSphere username / password
    export VSPHERE_USERNAME=administrator@vsphere.local
    export KUBECTL_VSPHERE_PASSWORD='Admin!23'
    ## the name of configmap, defines the Kubeflow specs
    export KUBEFLOW_CONFIGMAP=kubeflow

    kubectl vsphere login \
        --insecure-skip-tls-verify \
        --server=${VSPHERE_SUPERVISOR_CLUSTER_IP} \
        --vsphere-username ${VSPHERE_USERNAME} \

    kubectl config use-context ${VSPHERE_NAMESPACE}
   ```

2. Create a **values.yaml** follow the values schema at [link](../carvel/#install-kubeflow)

    ```yaml
    imageswap_labels: True

    service_type: "LoadBalancer"

    IP_address: ""

    CD_REGISTRATION_FLOW: True

    OIDC_Authservice:
      OIDC_AUTH_URL: /dex/auth
      OIDC_PROVIDER: http://dex.auth.svc.cluster.local:5556/dex
      OIDC_SCOPES: "profile email groups"
      REDIRECT_URL: /login/oidc
      SKIP_AUTH_URI: "/dex"
      USERID_CLAIM: email
      USERID_HEADER: kubeflow-userid
      USERID_PREFIX: ""
      OIDC_CLIENT_ID: kubeflow-oidc-authservice
      OIDC_CLIENT_SECRET: pUBnBOY80SnXgjibTYM9ZWNzY2xreNGQok

    Dex:
      use_external: False
      config: |
        issuer: http://dex.auth.svc.cluster.local:5556/dex
        storage:
          type: kubernetes
          config:
            inCluster: true
        web:
          http: 0.0.0.0:5556
        logger:
          level: "debug"
          format: text
        oauth2:
          skipApprovalScreen: true
        enablePasswordDB: true
        staticPasswords:
        - email: user@example.com
          hash: $2y$12$4K/VkmDd1q1Orb3xAt82zu8gk7Ad6ReFR4LCP9UeYE90NLiN9Df72
          # https://github.com/dexidp/dex/pull/1601/commits
          # FIXME: Use hashFromEnv instead
          username: user
          userID: "15841185641784"
        staticClients:
        # https://github.com/dexidp/dex/pull/1664
        - idEnv: OIDC_CLIENT_ID
          redirectURIs: ["/login/oidc"]
          name: 'Dex Login Application'
          secretEnv: OIDC_CLIENT_SECRET
    ```

1. Create a configmap from values.yaml
   ```bash
   kubectl create configmap ${KUBEFLOW_CONFIGMAP} --from-file=values.yaml=values.yaml -n ${VSPHERE_NAMESPACE}
   ```


4. Run the command to install Kubeflow on the Tanzu Kubernetes Cluster you specify.
    ```bash
    cat << EOF | kubectl apply -f -
    apiVersion: peach.vmware.com/v1alpha1
    kind: Kubeflow
    metadata:
      name: kubeflow-install
      namespace: ${VSPHERE_NAMESPACE}
    spec:
      auth:
        vsphere_username: ${VSPHERE_USERNAME}
        vsphere_password: ${KUBECTL_VSPHERE_PASSWORD}
      tkg:
        namespace: ${VSPHERE_NAMESPACE}
        cluster_name: ${VSPHERE_TKGS}
      carvel:
        configmap: ${KUBEFLOW_CONFIGMAP}
    EOF
    ```

5. Inspect installation process by running
   ```bash
   kubectl logs kubeflow-worker --follow -n ${VSPHERE_NAMESPACE}
   ```