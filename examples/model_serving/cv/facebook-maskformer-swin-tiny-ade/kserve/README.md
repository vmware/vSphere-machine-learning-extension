# `facebook/maskformer-swin-tiny-ade` Model Serving on VMware Kubeflow Using KServe

This tutorial guides you to serve `facebook/maskformer-swin-tiny-ade` on VMware Kubeflow using `kserve`.

MaskFormer model trained on ADE20k semantic segmentation (tiny-sized version, Swin backbone). MaskFormer addresses instance, semantic and panoptic segmentation with the same paradigm: by predicting a set of masks and corresponding labels. Hence, all 3 tasks are treated as if they were instance segmentation. You can use this particular checkpoint for semantic segmentation. 

## Prerequisites

- `maskformer.mar` ready to be used. Refer to [this doc](../torchserve/README.md) on how to generate a `.mar` file of the model.

## Get Started

### 1. Create PVC

Login on your Kubeflow UI. On the left panel, click "Volumes". Click "+ New Volume" on the right top corner.

Create a volume with name `model-local-claim`, and size 30Gi (recommended).

### 2. Mount the model

Create a pod `model-store-pod` to mount the model. Remember to change `<your_namespace>`.

```bash

cat << EOF | kubectl create -n <your_namepsace> -f -
apiVersion: v1
kind: Pod
metadata:
  name: model-store-pod
spec:
  volumes:
    - name: pv-storage
      persistentVolumeClaim:
        claimName: model-local-claim
  containers:
    - name: pv-container
      image: ubuntu
      command: [ "sleep" ]
      args: [ "infinity" ]
      volumeMounts:
        - mountPath: "/pv"
          name: pv-storage
      resources:
        limits:
          memory: "4Gi"
          cpu: "2"
EOF

```

Create a `config.properties` file.

```text

inference_address=http://0.0.0.0:8085
management_address=http://0.0.0.0:8085
metrics_address=http://0.0.0.0:8082
grpc_inference_port=7070
grpc_management_port=7071
enable_metrics_api=true
metrics_format=prometheus
number_of_netty_threads=4
job_queue_size=10
enable_envvars_config=true
install_py_dep_per_model=true
model_store=/mnt/model-store
model_snapshot={"name":"startup.cfg","modelCount":1,"models":{"maskformer":{"1.0":{"defaultVersion":true,"marName":"maskformer.mar","minWorkers":1,"maxWorkers":5,"batchSize":1,"maxBatchDelay":5000,"responseTimeout":120}}}}

```

We then mount the model to the PVC.

First, `exec` into the pod. Remember to change `<your_namespace>`.

```bash

kubectl exec -it model-store-pod -n <your_namepsace> bash

```

In the pod, create two folders.

```bash

cd cd pv/
mkdir model-store
mkdir config

```

Then exit the pod.

```bash

exit

```

Copy the model file and configuration file to the PVC.

```bash

kubectl cp maskformer.mar model-store-pod:/pv/model-store/ -n <your_namepsace>
kubectl cp config.properties model-store-pod:/pv/config/ -n <your_namepsace>

```

Make sure the structure in pod `model-store-pod` looks like below:

```text

|_pv
  |_model-store
    |_maskformer.mar
  |_config
    |_config.properties

```

After this, delete pod `model-store-pod`.

### 3. Create inference service

Create an `inferenceservice` for our model. Remember to change `<your_namespace>`. Note that in this case we do NOT use GPU.

```bash

cat << EOF | kubectl create -n <your_namepsace> -f -
apiVersion: serving.kserve.io/v1beta1
kind: InferenceService
metadata:
  name: "torchserve-maskformer"
spec:
  predictor:
    pytorch:
      storageUri: pvc://model-local-claim
      resources:
          limits:
            cpu: 8
            memory: 16Gi
EOF

```

Check your inference service status until it is ready.

```bash

kubectl get inferenceservice torchserve-maskformer -n <your_namespace>

```

### 4. Model inference

After your inference service is ready, you can start to prepare your model serving testing.

First, get and set some required environment variables.

Get `SERVICE_HOSTNAME` use following command:

```bash

kubectl get inferenceservice torchserve-maskformer -n <your_namepsace> -o jsonpath='{.status.url}' | cut -d "/" -f 3

```

It would return something like `torchserve-maskformer.user.example.com`.

Make sure you login under the correct account in Kubeflow UI. Then in your browser, get the corresponding cookie. 

For example, in FireFox, right click the page and click "Inspect". Then go to "Storage" panel. Click on "Cookies" on the left side panel. And then select the correct page, and copy the corresponding cookie.

Then export.

```bash

export SERVICE_HOSTNAME='<your_service_hostname>'
export SESSION='<your_corresponding_cookie>'
export MODEL_NAME='maskformer'
export INGRESS_HOST=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
export INGRESS_PORT=$(kubectl -n istio-system get service istio-ingressgateway -o jsonpath='{.spec.ports[?(@.name=="http2")].port}')

```

You can then `curl` the model inference API. Note that a test file containing an image URL is needed. We provide you with a sample one in [`sample_url.json`](./sample_url.json).

```bash

curl -v -H "Host: $SERVICE_HOSTNAME" -H "Host: ${SERVICE_HOSTNAME}" http://${INGRESS_HOST}:${INGRESS_PORT}/v1/models/${MODEL_NAME}:predict -d @./sample_url.json

```

The output should be similar to following:

```text

*   Trying 10.105.150.44:80...
* TCP_NODELAY set
* Connected to 10.105.150.44 (10.105.150.44) port 80 (#0)
> POST /v1/models/maskformer:predict HTTP/1.1
> Host: torchserve-maskformer.user.example.com
> User-Agent: curl/7.68.0
> Accept: */*
> Cookie: authservice_session=*****
> Content-Length: 101
> Content-Type: application/x-www-form-urlencoded
>
* upload completely sent off: 61 out of 61 bytes
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< content-length: 612
< date: Mon, 08 May 2023 05:58:04 GMT
< server: envoy
< x-envoy-upstream-service-time: 2557
<
[
  {
    "id": 1,
    "label_id": 17,
    "was_fused": false,
    "score": 0.900921
  },
  {
    "id": 2,
    "label_id": 25,
    "was_fused": false,
    "score": 0.95619
  },
  {
    "id": 3,
    "label_id": 6,
    "was_fused": false,
    "score": 0.985853
  },
  {
    "id": 4,
    "label_id": 4,
    "was_fused": false,
    "score": 0.998232
  },
  {
    "id": 5,
    "label_id": 9,
    "was_fused": false,
    "score": 0.995336
  },
  {
    "id": 6,
    "label_id": 0,
    "was_fused": false,
    "score": 0.969291
  },
  {
    "id": 7,
    "label_id": 2,
    "was_fused": false,
    "score": 0.999394
  }
* Connection #0 to host 10.105.150.44 left intact
]

```









