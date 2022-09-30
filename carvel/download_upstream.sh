#!/bin/bash
cd $(dirname $0)

wget --quiet https://github.com/kubeflow/manifests/archive/refs/tags/v1.6.0.zip -O v1.6.0.zip
unzip -q v1.6.0.zip 

kubeflow_ytt=bundle/config/upstream/kubeflow
kubeflow_dir=./manifests-1.6.0

# $1: dir
# $2: order: 1, 2, 3, 4, ...
function generate_upstream() {
    dir=$1
    order=$2
    mkdir -p ${kubeflow_ytt}/${dir}
    kustomize build ${kubeflow_dir}/${dir} -o ${kubeflow_ytt}/${dir}/install.yaml
    cat > ${kubeflow_ytt}/${1}/orders.yaml << EOF
#@ load("@ytt:overlay", "overlay")

#@overlay/match by=overlay.all, expects="1+"
---
metadata:
  #@overlay/match missing_ok=True
  annotations:
    #@overlay/match missing_ok=True
    kapp.k14s.io/change-group: "apps.kubeflow.org/order-${order}"
#@ if ${order} >= 2:
    #@overlay/match missing_ok=True
    kapp.k14s.io/change-rule: "upsert after upserting apps.kubeflow.org/order-$((order-1))"
#@ end
EOF
ytt --file ${kubeflow_ytt}/${1} > ${kubeflow_ytt}/${1}/install_order.yaml
rm ${kubeflow_ytt}/${dir}/install.yaml ${kubeflow_ytt}/${1}/orders.yaml
}

# cert-manager
generate_upstream common/cert-manager/cert-manager/base 1
generate_upstream common/cert-manager/kubeflow-issuer/base 2

# istio
generate_upstream common/istio-1-14/istio-crds/base  3
generate_upstream common/istio-1-14/istio-namespace/base 3
generate_upstream common/istio-1-14/istio-install/base 3
# dex 
generate_upstream common/dex/overlays/istio 3
# OIDC AuthService
generate_upstream common/oidc-authservice/base 3

# Knative Serving
generate_upstream common/knative/knative-serving/overlays/gateways 4

# cluster-local-gateway
generate_upstream common/istio-1-14/cluster-local-gateway/base 5

# kubeflow namespace
generate_upstream common/kubeflow-namespace/base 6
# kubeflow roles
generate_upstream common/kubeflow-roles/base 6
# istio resources
generate_upstream common/istio-1-14/kubeflow-istio-resources/base 6

# kubeflow pipelines
generate_upstream apps/pipeline/upstream/env/platform-agnostic-multi-user-pns 7

# Kubeflow apps
generate_upstream contrib/kserve/kserve 8
generate_upstream contrib/kserve/models-web-app/overlays/kubeflow 8
generate_upstream apps/katib/upstream/installs/katib-with-kubeflow 8
generate_upstream apps/centraldashboard/upstream/overlays/kserve 8
generate_upstream apps/admission-webhook/upstream/overlays/cert-manager 8
generate_upstream apps/jupyter/notebook-controller/upstream/overlays/kubeflow 8
generate_upstream apps/jupyter/jupyter-web-app/upstream/overlays/istio 8

# profiles and KFAM
generate_upstream apps/profiles/upstream/overlays/kubeflow 9

# apps
generate_upstream apps/volumes-web-app/upstream/overlays/istio 10
generate_upstream apps/tensorboard/tensorboards-web-app/upstream/overlays/istio 10
generate_upstream apps/tensorboard/tensorboard-controller/upstream/overlays/kubeflow 10
generate_upstream apps/training-operator/upstream/overlays/kubeflow 10
generate_upstream common/user-namespace/base 10