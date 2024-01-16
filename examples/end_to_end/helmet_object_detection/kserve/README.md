# Helmet Detection Model Serving on Freestone Kubeflow with KServe

## Introduction

The InferenceService custom resource is the primary interface that is used for deploying models on KServe. Inside an InferenceService, you can specify multiple components that are used for handling inference requests. These components are the predictor, transformer, and explainer.
For more detailed documentation on KServe, refer to [KServe](https://kserve.github.io/website/).

## Get Started
### Prepare model and configuration files

First, you can create a notebook refer to [Kubeflow Notebook](https://vmware.github.io/vSphere-machine-learning-extension/user-guide/notebooks.html#user-guide-notebooks). Then, unzip the kserve package we have prepared for this notebook server.

```bash
$ cd kubeflow-docs/examples/end_to_end/helmet_object_detection/kserve
$ unzip helmet_kserve.zip
```

You cloud also run  the `helmet_kserve.ipynb` in the notebook server to generate the above files with yourself.

### Upload to MinIO

If you already have the MinIO storage, you can directly skip the MinIO deployment step, and follow the next steps to upload data to MinIO. If not, we also provide a standalone MinIO deployment guide on the kubernetes clusters, you can refer to the YAML files from [MinIO deployment files](https://github.com/vmware/vSphere-machine-learning-extension/tree/main/examples/end_to_end/helmet_object_detection/kserve/minio).

```bash
# create pvc, replace storageClassName: pacific-storage-policy with storageClassName: k8s-storage-policy in minio-standalone-pvc.yml first
$ kubectl apply -f minio-standalone-pvc.yml

# create service
$ kubectl apply -f minio-standalone-service.yml

# create deployment
$ kubectl apply -f minio-standalone-deployment.yml
```

This step uploads `v1/torchserve/model-store`, `v1/torchserve/config` to MinIO buckets. You need to find the MinIO `endpoint_url`, `accesskey`, `secretkey` before upload using the following commands in your terminal.

```bash
# <your-namespace> is user, the default one created when login to Kubeflow on vSphere dashboard for the first time.

# get the endpoint url for MinIO
$ kubectl get svc minio-service -n <your-namespace> -o jsonpath='{.status.loadBalancer.ingress}'
# output is like: [{"ip":"10.105.150.41"}], this IP is used later in the Python script to set AWS_ENDPOINT_URL

# get the secret name for Minio.
$ kubectl get secret -n <your-namespace> | grep minio
# output is: mlpipeline-minio-artifact

# get the access key for MinIO
$ kubectl get secret <minio-secret-name> -n <your-namespace> -o jsonpath='{.data.accesskey}' | base64 -d
# output is: minio

# get the secret key for MinIO
$ kubectl get secret <minio-secret-name> -n <your-namespace> -o jsonpath='{.data.secretkey}' | base64 -d
# output is: minio123
```

You need to install `boto3` dependency package in the notebook server created before, and run the follow python code to upload model files.

```bash
!pip install boto3 -i https://pypi.tuna.tsinghua.edu.cn/simple
```

```python
import os
from urllib.parse import urlparse
import boto3

os.environ["AWS_ENDPOINT_URL"] = "http://10.117.233.16:9000"
os.environ["AWS_REGION"] = "us-east-1"
os.environ["AWS_ACCESS_KEY_ID"] = "minioadmin"
os.environ["AWS_SECRET_ACCESS_KEY"] = "minioadmin"

s3 = boto3.resource('s3',
                    endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
                    verify=True)

print("current buckets in s3:")
print(list(s3.buckets.all()))

bucket_name='helmet-bucket'
s3.create_bucket(Bucket=bucket_name)

curr_path = os.getcwd()
base_path = os.path.join(curr_path, "torchserve")


bucket_path = "helmet_detection"

bucket = s3.Bucket(bucket_name)

# upload
bucket.upload_file(os.path.join(base_path, "model-store", "helmet_detection.mar"),
                os.path.join(bucket_path, "model-store/helmet_detection.mar"))
bucket.upload_file(os.path.join(base_path, "config", "config.properties"),
                os.path.join(bucket_path, "config/config.properties"))

# check files
for obj in bucket.objects.filter(Prefix=bucket_path):
    print(obj.key)
```

### Create Minio Service Account and Secret

When you create an `InferenceService` to start model, you need to be authorized to access MinIO to get model. Thus, you need to create MinIO service account and secret according to the follow yaml file in the terminal.

```bash
cat << EOF | kubectl apply -f -
    apiVersion: v1
    kind: Secret
    metadata:
    name: minio-s3-secret-user
    annotations:
        serving.kserve.io/s3-endpoint: "10.105.150.41:9000" # replace with your s3 endpoint e.g minio-service.kubeflow:9000
        serving.kserve.io/s3-usehttps: "0" # by default 1, if testing with minio you can set to 0
        serving.kserve.io/s3-region: "us-east-2"
        serving.kserve.io/s3-useanoncredential: "false" # omitting this is the same as false, if true will ignore provided credential and use anonymous credentials
    type: Opaque
    stringData: # use "stringData" for raw credential string or "data" for base64 encoded string
    AWS_ACCESS_KEY_ID: minioadmin
    AWS_SECRET_ACCESS_KEY: minioadmin
    ---
    apiVersion: v1
    kind: ServiceAccount
    metadata:
    name: minio-service-account-user
    secrets:
    - name: minio-s3-secret-user
    EOF
secret/minio-s3-secret-user created
serviceaccount/minio-service-account-user created
```

### Run your InferenceService using KServe¶
Let’s define a new InferenceService YAML for the model and apply it to the cluster in the terminal. Meanwhile, you need to notice that Set `storageUri` to your `bucket_name/bucket_path` You may also need to change `metadata: name` and `serviceAccountName`.

```bash
cat << EOF | kubectl apply -f -
    apiVersion: "serving.kserve.io/v1beta1"
    kind: "InferenceService"
    metadata:
    name: "helmet-detection-serving"
    spec:
    predictor:
        serviceAccountName: minio-service-account-user
        model:
        modelFormat:
            name: pytorch
        storageUri: "s3://helmet-bucket/helmet_detection"
        resources:
            requests:
                cpu: 50m
                memory: 200Mi
            limits:
                cpu: 100m
                memory: 500Mi
            # limits:
            #   nvidia.com/gpu: "1"   # for inference service on GPU
    EOF
inferenceservice.serving.kserve.io/helmet-detection-serving created
```

### Run your InferenceService using KServe¶

Run the following command to check status in the terminal. If the status of `InferenceService` is True, that meaning is your model server is running well.

```bash
$ kubectl get inferenceservice helmet-detection-serving -n <your-namespace> # <your-namespace> is user>
helmet-detection-serving.user.example.com
```

### Test Perform Inference
#### Define a Test_bot for convenience¶

```shell
$ pip install multiprocess -i https://pypi.tuna.tsinghua.edu.cn/simple
```

Run the following cells to define a test_bot to do model prediction in the notebook server.


```python
import requests
import json
import multiprocess as mp
import io
import base64
import PIL.Image as Image
# from PIL import Image


class Test_bot():
    def __init__(self, uri, model, host, session):
        self.uri = uri
        self.model = model
        self.host = host
        self.session = session
        self.headers = {'Host': self.host, 'Content-Type': "image/jpeg", 'Cookie': "authservice_session=" + self.session}
        self.img = './2.jpg'

    def update_uri(self, uri):
        self.uri = uri

    def update_model(self, model):
        self.model = model

    def update_host(self, host):
        self.host = host
        self.update_headers()

    def update_session(self, session):
        self.session = session
        self.update_headers()

    def update_headers(self):
        self.headers = {'Host': self.host, 'Content-Type': "image/jpeg", 'Cookie': "authservice_session=" + self.session}

    def get_data(self, x):
        if x:
            payload = x
        else:
            payload = self.img
        with open(payload, "rb") as image:
            f = image.read()
            image_data = base64.b64encode(f).decode('utf-8')

        return json.dumps({'instances': [image_data]})


    def predict(self, x=None):
        uri = self.uri + '/v1/models/' + self.model + ':predict'
        response = requests.request("POST", uri, headers=self.headers, data=self.get_data(x))
        return response.text


    def readiness(self):
        # uri = self.uri + '/v1/models/' + self.model
        uri = self.uri + '/v1/models/' + self.model
        response = requests.get(uri, headers = self.headers, timeout=5)
        return response.text


    def explain(self, x=None):
        uri = self.uri + '/v1/models/' + self.model + ':explain'
        response = requests.post(uri, data=self.get_data(x), headers = self.headers, timeout=10)
        return response.text

    def concurrent_predict(self, num=10):
        print("fire " + str(num) + " requests to " + self.host)
        with mp.Pool() as pool:
            responses = pool.map(self.predict, range(num))
        return responses
```


#### Determine host and session¶

Run the following command to get host, which will be set to the headers in our request in the terminal.

```bash
$ kubectl get inferenceservice helmet-detection-serving -o jsonpath='{.status.url}' | cut -d "/" -f 3

```

Use your web browser to login to Kubeflow on vSphere, and get Cookies: authservice_session (Chrome: Developer Tools -> Applications -> Cookies)


#### Test model prediction¶

Run the following cell to do model prediction in the notebook server.

```bash
 # replace it with the url you used to access Kubeflow on vSphere
    bot = Test_bot(uri='http://10.117.233.8',
                model='helmet_detection',
                # replace it with what is printed above
                host='helmet-detection-serving.kubeflow-user-example-com.example.com',
                # replace it
                session='MTY3MDM5OTkzNnxOd3dBTkZZeU5GSkhUVE5NVGtaRk1rMVpXVVpJVlV4SFFUWkpSRFpIVmxaQ05WaERTRlpRV2xoUFRWZEpXa2hTTjB4SVFrMDNSRkU9fFWl635XpDECJSOEnzFJLOugFqIiGbIniTh0uPs0BCW1')

    print(bot.readiness())
    print(bot.predict('./2.jpg'))

    detections = json.loads(bot.predict('./2.jpg'))

```

The output is like as follow:

```bash
{"name": "helmet_detection", "ready": true}
{'predictions': [[{'x1': 0.6902239322662354, 'y1': 0.24169841408729553, 'x2': 0.7481994032859802, 'y2': 0.3332946300506592, 'confidence': 0.8919700980186462, 'class': 'person'}, {'x1': 0.0010159790981560946, 'y1': 0.20112593472003937, 'x2': 0.06262165307998657, 'y2': 0.3038643002510071, 'confidence': 0.8917641043663025, 'class': 'person'}, {'x1': 0.7416869401931763, 'y1': 0.24357035756111145, 'x2': 0.7910981178283691, 'y2': 0.32219842076301575, 'confidence': 0.8897435665130615, 'class': 'person'}, {'x1': 0.6465808153152466, 'y1': 0.30016350746154785, 'x2': 0.6944388151168823, 'y2': 0.37477272748947144, 'confidence': 0.8708840012550354, 'class': 'person'}, {'x1': 0.8362932205200195, 'y1': 0.24196597933769226, 'x2': 0.8901769518852234, 'y2': 0.32216331362724304, 'confidence': 0.8658970594406128, 'class': 'hat'}, {'x1': 0.11715660244226456, 'y1': 0.2785477340221405, 'x2': 0.17345492541790009, 'y2': 0.35548269748687744, 'confidence': 0.8567688465118408, 'class': 'hat'}, {'x1': 0.3243858218193054, 'y1': 0.25397413969039917, 'x2': 0.3961048126220703, 'y2': 0.3512100577354431, 'confidence': 0.8429261445999146, 'class': 'person'}, {'x1': 0.8793138265609741, 'y1': 0.2569176256656647, 'x2': 0.9308530688285828, 'y2': 0.32830461859703064, 'confidence': 0.8314318060874939, 'class': 'hat'}, {'x1': 0.2581776976585388, 'y1': 0.2187282294034958, 'x2': 0.3340612053871155, 'y2': 0.32766249775886536, 'confidence': 0.7706097364425659, 'class': 'person'}, {'x1': 0.23304757475852966, 'y1': 0.255989670753479, 'x2': 0.27176254987716675, 'y2': 0.317762553691864, 'confidence': 0.76960289478302, 'class': 'hat'}, {'x1': 0.5913112163543701, 'y1': 0.29803234338760376, 'x2': 0.6493061780929565, 'y2': 0.3777821362018585, 'confidence': 0.7675313353538513, 'class': 'hat'}, {'x1': 0.596840500831604, 'y1': 0.25816941261291504, 'x2': 0.63739413022995, 'y2': 0.30656352639198303, 'confidence': 0.7505931258201599, 'class': 'hat'}, {'x1': 0.26180964708328247, 'y1': 0.21736088395118713, 'x2': 0.31703171133995056, 'y2': 0.272555410861969, 'confidence': 0.4925423860549927, 'class': 'person'}]]}

```

If it prints something like:

```shell
{"name": "helmet_detection", "ready": true}
<html><title>500: Internal Server Error</title><body>500: Internal Server Error</body><html>
```

and aborts with error message:

```shell
JASONDecoderError: Expecting value: line 1 column 1 (char 0)
```

Then increase the value of responseTimeout in file torchserve/config/config.properties and rerun the script.

#### Display model predictions as bounding boxes on the input image

Run the following cell to display model prediction image in the notebook server.

```python
import matplotlib.pyplot as plt
import numpy as np

def visualize_detections(image_path, detections, figsize=(8, 8)):

    img = Image.open(image_path)
    plt.figure(figsize=figsize)
    plt.axis("off")
    plt.imshow(img)

    scoreArr, nameArr, boxArr = [], [], []

    for detection in detections:
        score = detection['confidence']
        name = detection['class']  #class_names
        box = [detection['x1'], detection['y1'], detection['x2'], detection['y2']]      #boxes
        scoreArr.append(score)
        nameArr.append(name)
        boxArr.append(box)

    scoreArr, nameArr, boxArr = np.array(scoreArr), np.array(nameArr), np.array(boxArr)

    boxes, class_names, scores = boxArr, nameArr, scoreArr
    max_boxes, min_score = 18, 0.1
    score_split_w = 0.1  # 0.95~1.00
    score_split_r = 0.1  #0.90~0.95


    for i in range(min(boxes.shape[0], max_boxes)):
        if scores[i] >= min_score:
            xmin, ymin, xmax, ymax = tuple(boxes[i])

            ax = plt.gca()
            text = "{}: {:.2f}".format(class_names[i], (scores[i]))
            w, h = xmax - xmin, ymax - ymin
            xmin *= 800
            ymin *= 500
            w *= 800
            h *= 500

            if class_names[i] == 'person':
                patch = plt.Rectangle(
                [xmin, ymin], w, h, fill=False, edgecolor='w', linewidth=3
            )
            else:
                patch = plt.Rectangle(
                [xmin, ymin], w, h, fill=False, edgecolor='c', linewidth=3
            )

        ax.add_patch(patch)

        if class_names[i] == 'person':
            ax.text(
                xmin,
                ymin,
                text,
                bbox={"facecolor": 'w', "alpha": 1.0},
                clip_box=ax.clipbox,
                clip_on=True,
            )
        else:
            ax.text(
                xmin,
                ymin,
                text,
                bbox={"facecolor": 'c', "alpha": 0.8},
                clip_box=ax.clipbox,
                clip_on=True,
            )

    plt.show()

image_path = './2.jpg'
visualize_detections(image_path, detections['predictions'][0])
```

![Image text](https://github.com/harperjuanl/kubeflow-examples/blob/main/helmet_detection/kserve/img/helmet-kserve-02.png)


#### Delete InferenceService¶

When you are done with your InferenceService, you can delete it by running the following.

```bash
$ kubectl delete inferenceservice <your-inferenceservice> -n <your-namespace>
```
