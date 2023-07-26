# Resnet Model Deployment

## Overview

This tutorial guides you deploy the Resnet models with Kubeflow on vSphere platform in 3 different ways.

The Resnet models are popular image classification Machine Learning models. They were first proposed in this paper: [“Deep Residual Learning for Image Recognition”]( https://arxiv.org/abs/1512.03385). Pytorch Hub has the 5 versions of resnet models pretrained, which contains 18, 34, 50, 101, 152 layers respectively. Visit the [Pytorch Hub web page](https://pytorch.org/hub/pytorch_vision_resnet/) to get more details on these models.

Here we describe 3 successive ways deploying the Resnet models, each as one task:
1. Run the Resnet models in a Notebook server
2. Provide inference service with torchserve in a Notebook server
3. Provide inference service with KServe

## Task 1: Run the models in a Notebook server

### Prerequisite

- The Kubeflow on vSphere environment is ready for use
 
### Step 1: Create a new Notebook server

On the Kubeflow UI, create a new Notebook server with 2 CPUs, 4Gi memory, 10Gi Workspace volume.

Check the 'Custom Image' box and use this Custom Image:
```
projects.registry.vmware.com/models/notebook/serve:pytorch-cpu-v1
```

### Step 2: Get the model deployment notebook 

Connect to the notebook server, open a Terminal window, run this command to get the Pytorch Hub resnet model deployment notebook file pytorch_vision_resnet.ipynb

```
 wget https://raw.githubusercontent.com/pytorch/pytorch.github.io/master/assets/hub/pytorch_vision_resnet.ipynb
```

Note: In case the command above doesn't work, manually download this file from the Pytorch Hub website and then upload it to this notebook server.

### Step 3: Run the model deployment notebook

Open pytorch_vision_resnet.ipynb in the Notebook server, read the instructions and code in this notebook to understand the resnet model versions, how to download each version of the models, and the sample execution. Finally, run the notebook cell by cell or run the whole notebook with one click.

Note: the following tasks assume that the resnet-18 model is used in the sample execution above.

## Task 2: Model inference with torchserve

### Prerequisite

- Make sure task 1 finished successfully and you can find the model check point file (resnet18-*.pth) in .cache/pytorch/hub/checkpoints/ under your home directory.

### Step 1: Clone the code of this project

In the Notebook server created with Task 1, open a Terminal window, get the code required for task 2 and 3.

```
git clone https://github.com/vmware/vSphere-machine-learning-extension.git
```
Change directory to vSphere-machine-learning-extension/examples/model_serving/cv/torchhub-resnet/

### Step 2: Prepare and start the torchserve service

Read the document and code in ```resnet_torchserve.sh```, understand that this script help download necessary files for resnet torchserve run, create the torchserve package .mar file, and then start the torchserve service. Then execute this script with this command:

```
sh resnet_torchserve.sh
```

### Step 3: Test the torchserve inference service

Let's test the inference with the sample picture we get in task 1.

```
curl http://127.0.0.1:8080/predictions/resnet-18 -T ./dog.jpg 
```

You should see similar prediction result with the sample execution in task 1.

## Task 3: Model inference with KServe

### Prerequisite

- Make sure task 2 finished successfully and the "resnet-18.mar" file is ready to use.

### Step 1: Create a PVC

On the left panel of your Kubeflow UI, click "Volumes". Click "+ New Volume" on the right top corner.

Create a volume with name `resnet-model-volume`, and size 3Gi. 

### Step 2: Copy model files to the PVC

In the Notebook server created with Task 1, open a Terminal window to execute the kubectl commands mentioned blow.

Change directory to vSphere-machine-learning-extension/examples/model_serving/cv/torchhub-resnet/kserve/

Create a pod named `model-store-pod` to copy model files to the volume created in step 1.

```bash
cat << EOF | kubectl create -f -
apiVersion: v1
kind: Pod
metadata:
  name: model-store-pod
spec:
  volumes:
    - name: pv-storage
      persistentVolumeClaim:
        claimName: resnet-model-volume
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

Check the status of this pod with the command below.
```
kubectl get pods

```
Wait until the status of 'model-store-pod' is "Running".

Connect to this pod, create two folders, and then exit from this pod with the following commands.


```bash
kubectl exec -it model-store-pod -- bash

cd pv/
mkdir model-store
mkdir config
exit

```

Copy the model file and configuration file to the PVC.

```
kubectl cp ../models/resnet-18.mar model-store-pod:/pv/model-store/ 
kubectl cp config.properties model-store-pod:/pv/config/ 

```

Now the model files are ready on the PV volume. We can delete model-store-pod.
```
kubectl delete pod model-store-pod
```


### Step 3: Start the KServe inference service

```
kubectl apply -f resnet-kserve.yaml
```

It might take minutes for the service to be ready. Check the service status with
```
kubectl get pod 
```
Wait until the status of the pod 'resnet-18-predictor-default-00001-*' is Running

### Step 4: Determine the parameters of the inference service

Run this command to get service hostname
```
kubectl get inferenceservice resnet-18 -o jsonpath='{.status.url}' | cut -d "/" -f 3

export SERVICE_HOSTNAME='<your_service_hostname>'
```

On the web browser that you login to Kubeflow on vSphere, get the Cookies of authservice_session. For example, on the Chrome browser, you can get the cookie following these menu items: Developer Tools -> Applications -> Cookies -> authservice_session

```
export SESSION='<your_authservice_session>'
export MODEL_NAME='resnet-18'
```

Ask your Kubeflow administrator to follow instructions on [this link](https://kserve.github.io/website/0.10/get_started/first_isvc/#4-determine-the-ingress-ip-and-ports) to determine the ingress host and port. You cannot do this within the Notebook server.

```
export INGRESS_HOST='<your_ingress_host>'
export INGRESS_PORT='<your_ingress_port>'
```

### Step 5: Test the inference service

Let's test the inference service with the 'dog.jpg' file we get in task 1. Before the test, use [image converter](https://github.com/kserve/kserve/tree/master/docs/samples/v1beta1/torchserve/v1/imgconv) to convert the image to base64 byte array, and rename the output as 'dog.json'.

Run this command to test the inference service:
```
curl -v -H "Host: $SERVICE_HOSTNAME" -H "Cookie: authservice_session=$SESSION" http://${INGRESS_HOST}:${INGRESS_PORT}/v1/models/${MODEL_NAME}:predict -d @./dog.json
```

You will get similar prediction result as task 1 and task 2.

### Clean up

Finally, you can delete this inference service to clean up the test environment

```
kubectl delete inferenceservice resnet-18
```
