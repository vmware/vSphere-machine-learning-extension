## Installation

This section provides detailed information about Kubeflow deployment on vSphere with
Tanzu.

### Setup TKG cluster

#### Install vSphere with Tanzu

If vSphere with Tanzu is not installed and configured yet, see [vSphere with Tanzu Configuration and Management](https://docs.vmware.com/en/VMware-vSphere/7.0/vmware-vsphere-with-tanzu/GUID-152BE7D2-E227-4DAA-B527-557B564D9718.html)

#### Create namespace

Refer to [Create and Configure a vSphere Namespace](https://docs.vmware.com/en/VMware-vSphere/7.0/vmware-vsphere-with-tanzu/GUID-177C23C4-ED81-4ADD-89A2-61654C18201B.html) to create a namespace.

#### Setup content library for Tanzu Kubernetes Cluster OVF and OVA templates

OVF and OVA templates [address](https://wp-content.vmware.com/v2/latest/).

#### Download and install Kubernetes CLI tools for vSphere

#### Create a jumpbox VM for later use

```shell
# Create jumpbox for later config usage
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: jumpbox
  namespace: xyz                              # REPLACE
spec:
  containers:
  - image: "photon:3.0"
    name: jumpbox
    command: [ "/bin/bash", "-c", "--" ]
    args: [ "yum install -y openssh-server; mkdir /root/.ssh; cp /root/ssh/ssh-privatekey /root/.ssh/id_rsa; chmod 600 /root/.ssh/id_rsa; while true; do sleep 30; done;" ]
    volumeMounts:
      - mountPath: "/root/ssh"
        name: ssh-key
        readOnly: true
    resources:
      requests:
        memory: 2Gi
  volumes:
    - name: ssh-key
      secret:
        secretName: tkgs-cluster-01-ssh       # REPLACE
EOF
```

#### Deploy and configure TKG cluster for Kubeflow

Use the script provided by this project to provision and configure TKG cluster.

#### Verification

```shell
# login supervisor cluster
kubectl vsphere login --server=$server --vsphere-username administrator@vsphere.local --insecure-skip-tls-verify
# check cluster status
kubectl get tkc <cluster-name>

# login tkg cluster
kubectl vsphere login --server=$server --vsphere-username administrator@vsphere.local --insecure-skip-tls-verify --tanzu-kubernetes-cluster-namespace=<namespace> --tanzu-kubernetes-cluster-name=<cluster-name>
# check node status
kubectl get nodes -owide
```

### Deploy Kubeflow

#### Install Kubeflow 1.4 on TKG cluster

```shell
# download script and manifest for deployment
git clone https://github.com/liuqi/kubeflow-on-vsphere.git
# update the parameters and run the script
sh ./kubeflow-deployer-individual.sh
```

#### Verification
```
# check pods status
# login TKG cluster
kubectl vsphere login --server=$server --vsphere-username administrator@vsphere.local --insecure-skip-tls-verify --tanzu-kubernetes-cluster-namespace=<namespace> --tanzu-kubernetes-cluster-name=<cluster-name>

# ensure pod status is running
kubectl get pods -A
```

#### Access Kubeflow dashboard via port-forward

```
# port forward istio ingress gateway to local port 8080
kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80
```

Access Kubeflow central dashboard via browser (http://localhost:8080). Login with the default user's credential 
(user@example.com / 12341234).


