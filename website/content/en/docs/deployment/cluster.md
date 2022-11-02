+++
title = "Create a Tanzu Kubernetes Cluster"
description = "Create a Tanzu Kubernetes Cluster"
weight = 30
+++

## Install the Kubernetes CLI Tools for vSphere
---
Option 1: Follow the docs [here](https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-with-tanzu-installation-configuration/GUID-0F6E45C4-3CB1-4562-9370-686668519FCA.html) to open the download page, download and install the Kubernetes CLI tools.

Option 2: Follow the docs [here](https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-with-tanzu-installation-configuration/GUID-0F6E45C4-3CB1-4562-9370-686668519FCA.html), select **Copy the link** beneath the **Link to CLI Tools** heading, set it to VSPHERE_SUPERVISOR_CLUSTER_IP. Then run the following shell commands to install the Kubernetes CLI Tools.

  ```bash
  # Note: Please Set the VSPHERE_SUPERVISOR_CLUSTER_IP to the "Link to CLI Tools", 
  # e.g. VSPHERE_SUPERVISOR_CLUSTER_IP=192.168.123.2
  VSPHERE_SUPERVISOR_CLUSTER_IP=<The_IP_address_of_Link_to_CLI_Tools>

  if [[ `uname` == Darwin ]]; then
      binary_type=darwin-amd64
  else
      binary_type=linux-amd64
  fi
  wget --no-check-certificate https://${VSPHERE_SUPERVISOR_CLUSTER_IP}/wcp/plugin/${binary_type}/vsphere-plugin.zip -O vsphere-plugin.zip
  unzip -o vsphere-plugin.zip
  sudo mv bin/* /usr/local/bin/
  ```

## Tanzu Kubernetes Cluster Creation
---
1. Set all the constants based on the configurations of namespace you performed in the previous step [**Create and configure a vSphere namespace**](../namespace).
```bash
## Supervisor Cluster info
export VSPHERE_SUPERVISOR_CLUSTER_IP=<The_IP_address_of_Link_to_CLI_Tools>
export VSPHERE_NAMESPACE=namespace-kubeflow
## TKG info
export VSPHERE_TKGS=tkgs-kubeflow
export VSPHERE_TKGS_VERSION=v1.22.11---vmware.2-tkg.2-zshippable
export VSPHERE_TKGS_VM_COUNT=2
export VSPHERE_TKGS_VM_CLASS=guaranteed-large
export VSPHERE_TKGS_STORAGE_CLASS=pacific-storage-policy
export VSPHERE_TKGS_STORAGE_SIZE=70
## vSphere username / password
export VSPHERE_USERNAME=administrator@vsphere.local
export KUBECTL_VSPHERE_PASSWORD='Admin!23'
```

2. Run the command to login to the Supervisor Cluster.
```bash
kubectl vsphere login \
    --insecure-skip-tls-verify \
    --server=${VSPHERE_SUPERVISOR_CLUSTER_IP} \
    --vsphere-username ${VSPHERE_USERNAME} \

kubectl config use-context ${VSPHERE_NAMESPACE}
```

3. Run the command to create a Tanzu Kubernetes Cluster.
```bash
### create TKC
cat << EOF | kubectl apply -f -
apiVersion: run.tanzu.vmware.com/v1alpha2
kind: TanzuKubernetesCluster                  
metadata:
  name: ${VSPHERE_TKGS}                      
  namespace: ${VSPHERE_NAMESPACE}    
  annotations:
    run.tanzu.vmware.com/resolve-os-image: os-name=ubuntu
spec:
  topology:
    controlPlane:
      tkr:
        reference:
          name: ${VSPHERE_TKGS_VERSION}
      replicas: 1                                
      vmClass: ${VSPHERE_TKGS_VM_CLASS}
      storageClass: ${VSPHERE_TKGS_STORAGE_CLASS}
      volumes:
        - name: etcd
          mountPath: /var/lib/etcd
          capacity:
            storage: 20Gi
    nodePools:
    - name: workers
      replicas: ${VSPHERE_TKGS_VM_COUNT}
      vmClass: ${VSPHERE_TKGS_VM_CLASS}
      storageClass: ${VSPHERE_TKGS_STORAGE_CLASS}
      volumes:
        - name: containerd
          mountPath: /var/lib/containerd
          capacity:
            storage: ${VSPHERE_TKGS_STORAGE_SIZE}Gi
  settings:
    storage:
      defaultClass: ${VSPHERE_TKGS_STORAGE_CLASS}
    network:
      cni:
        name: antrea
      services:
        cidrBlocks: ["198.51.100.0/12"]
      pods:
        cidrBlocks: ["192.0.2.0/16"]
EOF
```

## Tanzu Kubernetes Cluster Login

Wait until the Tanzu Kubernetes Cluster is `Ready`.

```bash
$ kubectl get tkc

NAME             CONTROL PLANE   WORKER   TKR NAME                               AGE   READY   TKR COMPATIBLE   UPDATES AVAILABLE
tkgs-kubeflow    1               2        v1.22.11---vmware.2-tkg.2-zshippable   28m  True    True             [v1.23.8+vmware.2-tkg.2-zshippable]   
```
Run the command to login to the Tanzu Kubernetes Cluster.

```bash
kubectl vsphere login \
    --insecure-skip-tls-verify \
    --server=${VSPHERE_SUPERVISOR_CLUSTER_IP} \
    --vsphere-username ${VSPHERE_USERNAME} \
    --tanzu-kubernetes-cluster-namespace=${VSPHERE_NAMESPACE} \
    --tanzu-kubernetes-cluster-name=${VSPHERE_TKGS}

kubectl config use-context ${VSPHERE_TKGS}
```

## Trouble shooting
---

- You see `ContentSourceBindingNotFound` error in `kubectl get tkc <tkc_name>`

![](../assets/troubleshooting_contentsource.png)

Please check if the `OVF Template` of content library you used is valid. Or it is duplicated with the existing `OVF Template`, which will cause the `Stored Locally` flag to be `No`.

![](../assets/troubleshooting_contentsource2.png)


## What's Next
---

Now you are ready to move to the next section [Deploy Kubeflow](../carvel)