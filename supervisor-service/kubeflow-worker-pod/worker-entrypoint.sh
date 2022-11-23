#!/bin/bash

function get_server_port() {
  # Get server inside pod
  local APISERVER=https://kubernetes.default.svc
  local SERVICEACCOUNT=/var/run/secrets/kubernetes.io/serviceaccount
  local NAMESPACE=$(cat ${SERVICEACCOUNT}/namespace)
  local TOKEN=$(cat ${SERVICEACCOUNT}/token)
  local CACERT=${SERVICEACCOUNT}/ca.crt
  server_port=$( curl --cacert ${CACERT} --header "Authorization: Bearer ${TOKEN}" -X GET ${APISERVER}/api | jq -r '.serverAddressByClientCIDRs[0].serverAddress' )
}

function download_kubectl() {
  curl --insecure -L http://${VSPHERE_SUPERVISOR_CLUSTER_IP}/wcp/plugin/linux-amd64/vsphere-plugin.zip --output vsphere-plugin.zip
  unzip vsphere-plugin.zip
  mv ./bin/kubectl* /usr/local/bin/
}

function login_supervisor() {
  kubectl vsphere login --insecure-skip-tls-verify \
      --server=${VSPHERE_SUPERVISOR_CLUSTER_IP} \
      --vsphere-username ${VSPHERE_USERNAME}
  kubectl config use-context ${VSPHERE_NAMESPACE}
}

function login_guest() {
  kubectl vsphere login --insecure-skip-tls-verify \
      --server=${VSPHERE_SUPERVISOR_CLUSTER_IP} \
      --vsphere-username ${VSPHERE_USERNAME} \
      --tanzu-kubernetes-cluster-namespace=${VSPHERE_NAMESPACE} \
      --tanzu-kubernetes-cluster-name=${VSPHERE_TKGS}
  kubectl config use-context ${VSPHERE_TKGS}
}

function create_tkc() {
  cat << EOF | kapp deploy -y -a kubeflow-cluster -f -
apiVersion: run.tanzu.vmware.com/v1alpha3
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
      replicas: 3
      vmClass: ${VSPHERE_TKGS_VM_CLASS}
      storageClass: ${VSPHERE_TKGS_STORAGE_CLASS}
      volumes:
        - name: containerd
          mountPath: /var/lib/containerd
          capacity:
            storage: 100Gi
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
}

function deploy_kubeflow() {
  kubectl create namespace carvel-kubeflow-namespace --dry-run=client -o yaml | kubectl apply -f -
  kubectl config set-context --current --namespace=carvel-kubeflow-namespace
  kctrl package repository add \
    --repository kubeflow-carvel-repo \
    --url ${carvel_repo}
  while true; do
    kctrl package install \
      --wait-check-interval 5s \
      --wait-timeout 30m0s \
      --package-install kubeflow \
      --package kubeflow.community.tanzu.vmware.com \
      --version 1.6.0 \
      --values-file cfg/values.yaml
    if [[ $? == 0 ]]; then
      break
    fi
    sleep 10
  done
}

function delete_cr() {
  kubectl config use-context ${VSPHERE_NAMESPACE}
  local cr_name=$( kubectl get Kubeflow -A -o=jsonpath='{.items[?(@.spec.tkg.namespace=="'${VSPHERE_NAMESPACE}'")].metadata.name}' )
  local cr_namespace=$( kubectl get Kubeflow -A -o jsonpath='{.items[?(@.spec.tkg.namespace=="'${VSPHERE_NAMESPACE}'")].metadata.namespace}' )
  kubectl delete Kubeflow ${cr_name} -n ${cr_namespace}
}


env_list=("http_proxy" "https_proxy" "HTTP_PROXY" "HTTPS_PROXY")
for env_name in ${env_list[@]}; do 
  unset ${env_name}
done

## vSphere username / password
export VSPHERE_USERNAME=${vsphere_username}
export KUBECTL_VSPHERE_PASSWORD=${vsphere_password}

## Supervisor Cluster info
get_server_port
export VSPHERE_SUPERVISOR_CLUSTER_IP=${server_port%:*}
export VSPHERE_NAMESPACE=${vsphere_namespace}
export VSPHERE_TKGS=${vsphere_cluster_name}

## carvel
export carvel_repo=${carvel_repo}


kubectl-vsphere version 1>/dev/null 2>&1 || download_kubectl && \
login_supervisor && \
kubectl get tkc -o=jsonpath='{.items[?(@.metadata.name=="'${VSPHERE_TKGS}'")]}' | grep name
if [[ $? == '0' ]]; then
    tkc_status='exist'
else
    tkc_status='new'
    # create_tkc
    echo "Error: Tanzu Kubernetes Cluster ${VSPHERE_TKGS} does not exist in namespace ${VSPHERE_NAMESPACE}!"
    exit 1
fi

echo "Waiting for tkc/${VSPHERE_TKGS} to be Ready"
kubectl wait --for=condition=Ready tkc/${VSPHERE_TKGS} --timeout=3600s && \
login_guest && \
kubectl config set-context --current --namespace=default && \

# if [[ ${tkc_status} == 'new' ]]; then
    # kapp deploy -y -a imageswap -f imageswap_deploy.yaml && \
    # kubectl wait --for=condition=Available deploy/imageswap -n imageswap-system --timeout=600s
    # kapp deploy -y -a kapp-controller -f carvel-kapp-controller.yaml && \
# fi

deploy_kubeflow && \
login_supervisor && delete_cr
