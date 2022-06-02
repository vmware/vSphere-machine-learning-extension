# Model Serving Using KServe

KServe provides a Kubernetes Custom Resource Definition (CRD) for serving machine learning (ML) models on arbitrary frameworks. It encapsulates the complexity of autoscaling, networking, health checking, and server configuration. This section contains information on how to provide model serving features with Kubeflow, KServe and vSphere platform.

## Basic Usage

1. Check the deployment and status of KServe installed on vSphere

```shell
# login
kubectl vsphere login --server=xxx --vsphere-username administrator@vsphere.local --insecure-skip-tls-verify --tanzu-kubernetes-cluster-namespace=<Namespace> --tanzu-kubernetes-cluster-name=<TKG cluster name>

# check status
kubectl get pods -n kubeflow | grep kfserving
```

2. As an example, create TensorFlow KFServing InferenceService

```shell
# create InferenceService
cat <<EOF | kubectl apply -n kubeflow-user-example-com -f -
apiVersion: "serving.kubeflow.org/v1beta1"
kind: "InferenceService"
metadata:
  name: "flower-sample"
spec:
  default:
    predictor:
      tensorflow:
        storageUri: "gs://kfserving-samples/models/tensorflow/flowers"
EOF

# wait InferenceService to be ready
kubectl get isvc flower-sample -n kubeflow-user-example-com
```

3. Port forward to localhost and login Kubeflow central dashboard with default
username and password (user@example.com / 12341234)

```shell
kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80
```

4. Run a prediction as client

```shell
MODEL_NAME=flower-sample 
INPUT_PATH=@./flowers-sample-input.json 
# Log in kubeflow UI and get the cookie as $SESSION
SERVICE_HOSTNAME=$(kubectl get -n kubeflow-user-example-com inferenceservice ${MODEL_NAME} -o jsonpath='{.status.url}' | cut -d "/" -f 3)
curl -v -H "Host: ${SERVICE_HOSTNAME}" -H "Cookie: authservice_session=${SESSION}" http://127.0.0.1:8080/v1/models/${MODEL_NAME}:predict –d / ${INPUT_PATH}
```

5. Delete an inference model

```shell
kubectl delete inferenceservices flower-sample  -n kubeflow-user-example-com
```

## More Model Deployment Examples

| Sample | Link |
| ----------- | ----------- |
| TensorFlow | [link](https://github.com/harperjuanl/kubeflow/tree/main/docs/samples/tensorflow-flowers-sample) |
| PyTorch | [link](https://github.com/harperjuanl/kubeflow/tree/main/docs/samples/torchserve) |
| Scikit-learn | [link](https://github.com/harperjuanl/kubeflow/tree/main/docs/samples/sklearn-iris) |
| XGBoost | [link](https://github.com/harperjuanl/kubeflow/tree/main/docs/samples/xgboost) |
| PaddlePaddle | [link](https://github.com/harperjuanl/kubeflow/tree/main/docs/samples/paddle) |
| Nvidia Triton Inferenece Server | [link](https://github.com/harperjuanl/kubeflow/tree/main/docs/samples/triton/bert) |
| Canary | [link](https://github.com/harperjuanl/kubeflow/tree/main/docs/samples/canary-rollout) |

## Use KServe API with Python SDK

### KServe Server

KServe's python server libraries implement a standardized KFServing library that is extended by model serving frameworks such as Scikit Learn, XGBoost and PyTorch. It encapsulates data plane API definitions and storage retrieval for models

* Provide many functionalities: Registering a model and starting the server, Prediction Handler, Liveness Handler, Readiness Handlers

* Support the storage providers: Google Cloud Storage, S3 Compatible Object Storage, Azure Blob Storage, Persistent Volume Claim (PVC), Generic URI

### KServe Client

KServe's python client interacts with KServe control plane APIs for executing operations on a remote KServe cluster, such as creating, patching and deleting of a InferenceService instance 

## KServe API - Example

In this part, an example using KServe API is introduced. Related codes could be
found [here](https://github.com/harperjuanl/kubeflow/tree/main/docs/samples/python-sdk-samples).

1. Import library

```shell
pip install kfserving==0.6.1
```

2. Define define endpoint spec,  and then define the inferenceservice basic on the endpoint spec

```python
api_version = constants.KFSERVING_GROUP + '/' + kfserving_version
```

3. Create InferenceService

```python
isvc = V1beta1InferenceService(api_version=api_version,
                               kind=constants.KFSERVING_KIND,
                               metadata=client.V1ObjectMeta(
                               name='flower-sample', namespace=namespace),
                               spec=V1beta1InferenceServiceSpec(
                               predictor=V1beta1PredictorSpec(
                               tensorflow=(V1beta1TFServingSpec(
                               storage_uri='gs://kfserving-samples/models/tensorflow/flowers'))))
)
```

4. Check InferenceService and Run a prediction

```python
KFServing.get('flower-sample', namespace=namespace, watch=True, timeout_seconds=120)
```

## KServe API Reference

For more information and reference about KServe APIs, refer to [this page](https://github.com/kserve/website/blob/main/docs/reference/api.md).
