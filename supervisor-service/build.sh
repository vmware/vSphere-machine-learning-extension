#!/bin/bash
dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd "$dir"

export VERSION=${VERSION:-0.0.1}
export WORKPOD_IMG="projects.registry.vmware.com/kubeflow/supervisor-service-worker-pod:${VERSION}" 
export OPERATOR_IMG="projects.registry.vmware.com/kubeflow/supervisor-service-operator:${VERSION}"

function worker_pod() {
	echo "1. Build to push worker_pod image: ${WORKPOD_IMG} based on ./kubeflow-worker-pod/Dockerfile"
	docker build -t ${WORKPOD_IMG} -f ./kubeflow-worker-pod/Dockerfile ./kubeflow-worker-pod &&
	docker push ${WORKPOD_IMG}
}

function operator() {
	echo "2. Build to push operator image: ${OPERATOR_IMG} based on ./kubeflow-operator/Dockerfile"
	WORKPOD_IMG_sed=${WORKPOD_IMG//'/'/'\/'} &&
	sed -i -E "s/(.Values.image \| default \").*(\")/\1${WORKPOD_IMG_sed}\2/g" ./kubeflow-operator/helm-charts/kubeflow/templates/kubeflow-worker.yaml
	docker build -t ${OPERATOR_IMG} -f ./kubeflow-operator/Dockerfile ./kubeflow-operator &&
	docker push ${OPERATOR_IMG}
}

function manifest() {
	echo "3. Create manifest files of Supervisor Service"
	OPERATOR_IMG_sed=${OPERATOR_IMG//'/'/'\/'}
	sed -i -E "s/(image: ).*?(kubeflow-operator:).*/image: ${OPERATOR_IMG_sed}/g" ./kubeflow_operator.yaml
	python3 create-vsphere-app.py \
		-c kubeflow-operator/config/crd/bases/peach.vmware.com_kubeflows.yaml \
		-p kubeflow_operator.yaml \
		-o kubeflow-service-def.yaml \
		-v ${VERSION} \
		kubeflow
}

worker_pod && \
operator && \
manifest && \
echo "Done! " && \
echo "Now you can upload kubeflow-service-def.yaml at vSphere vCenter: Workload Management -> Services -> Add New Service"