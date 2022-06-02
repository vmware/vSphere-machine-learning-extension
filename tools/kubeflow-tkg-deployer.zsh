#!/bin/zsh
# Copyright 2022 VMware, Inc.
# SPDX-License-Identifier: Apache-2.0

# Change me
# TKG cluster index
number=02

# namespace
ns=xyz

# server and password
server=10.117.233.2
export KUBECTL_VSPHERE_PASSWORD="xxxyyyzzz"

kubectl vsphere login --server=$server --vsphere-username administrator@vsphere.local --insecure-skip-tls-verify
kubectl config use-context $ns

# create tkg cluster
cat << EOF | kubectl apply -f -
apiVersion: run.tanzu.vmware.com/v1alpha1  #TKGS API endpoint
kind: TanzuKubernetesCluster               #required parameter
metadata:
  name: tkgs-cluster-$number               #cluster name, user defined
  namespace: $ns                           #vsphere namespace
spec:
  distribution:
    version: v1.19                         #Resolves to latest TKR 1.19 version
  topology:
    controlPlane:
      count: 1                             #number of control plane nodes
      class: best-effort-medium            #vmclass for control plane nodes
      storageClass: pacific-storage-policy    #storageclass for control plane
    workers:
      count: 7                             #number of worker nodes
      class: best-effort-medium            #vmclass for worker nodes
      storageClass: pacific-storage-policy    #storageclass for worker nodes
  settings:
    storage:
      defaultClass: pacific-storage-policy
EOF

while true; do
  kubectl get tanzukubernetesclusters|grep tkgs-cluster-$number|grep "True    True"
  if [[ $? == 0 ]]; then
    break
  fi
  sleep 30
  echo "Wait tkg cluster provision finish..."
done

# get ssh password
kubectl config use-context $ns
ssh_password=`kubectl get secrets tkgs-cluster-$number-ssh-password -o jsonpath='{.data.ssh-passwordkey}' | base64 -d`
echo $ssh_password

control_vm_ip=`kubectl describe virtualmachines tkgs-cluster-$number-control-plane|grep "Vm Ip"|cut -d: -f2 -|sed 's/^[ \t]*//g' -`
echo "Control Plane Node IP is "$control_vm_ip
nodes_ip=`kubectl describe virtualmachines tkgs-cluster-$number-workers|grep "Vm Ip"|cut -d: -f2 -|sed 's/^[ \t]*//g' -`

# patch api-server (control node)
kubectl exec jumpbox -- bash -c "\
{
ssh_password=$ssh_password
for node in ${control_vm_ip}; do
  "'#use inner variable substitution
    sshpass -p $ssh_password ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o HashKnownHosts=no vmware-system-user@$node \
    '\''apiServerFile=/etc/kubernetes/manifests/kube-apiserver.yaml; \
    sudo sed -i "s,- --tls-private-key-file=/etc/kubernetes/pki/apiserver.key,- --tls-private-key-file=/etc/kubernetes/pki/apiserver.key\n\    - --service-account-issuer=kubernetes.default.svc\n\    - --service-account-signing-key-file=/etc/kubernetes/pki/sa.key," $apiServerFile '\''
  '"
done;
}"

echo "Control Plane Node is patched"

sleep 200

kubectl vsphere login --server=$server --vsphere-username administrator@vsphere.local --insecure-skip-tls-verify --tanzu-kubernetes-cluster-namespace=$ns --tanzu-kubernetes-cluster-name=tkgs-cluster-$number
kubectl get sc pacific-storage-policy -o yaml > tmp-sc.yaml
sed '/^parameters:.*/a\ \ csi.storage.k8s.io/fstype: "ext4"' -i tmp-sc.yaml
kubectl replace -f tmp-sc.yaml --force
kubectl get sc pacific-storage-policy -o yaml
echo "Update storage policy -- done"

exit
