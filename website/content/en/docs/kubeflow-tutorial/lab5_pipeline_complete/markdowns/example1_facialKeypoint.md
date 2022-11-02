# Lab 7: Kubeflow Pipeline

### Install Kubeflow Pipeline Package


```python
!pip install kfp --upgrade --user --quiet
```


```python
# confirm the kfp sdk
! pip show kfp
```

## Example 1: Facial Keypoint Detection

In this example, we would build pipeline components from ***docker images***.

### About this Model

This model comes from Kaggle Competition. The objective of this task is to predict keypoint positions on face images, which can be used as a building block in several applications, such as analysing facial expressions and biometrics recognition.

There are two main tasks: train and evaluation. Each would be build as a pipeline component later. 

Datasets for training can be found in [train/my_data](./train/my_data).

More details about this model itself can be found [here on Kaggle Competition page](https://www.kaggle.com/competitions/facial-keypoints-detection).

### Design Pipeline Components

When Kubeflow Pipelines executes a component, a container image is started in a Kubernetes Pod and your component’s inputs are passed in as command-line arguments.

Therefore, while designing pipeline components, we need to consider following issues:
* Which inputs can be passed to our component by value? And which inputs, which cannot be directly passed as a command-line argument, should be passed to your component by a reference to the input’s path?
* To return an output from our component, the output’s data must be stored as a file. We need to let Kubeflow Pipelines know what outputs our component produces, so that when our pipeline runs, Kubeflow Pipelines can pass the paths that we use to store our component’s outputs as inputs to our component.
* Since your inputs and output paths are passed in as command-line arguments, your component’s code must be able to read inputs from the command line. 

And in this example, specifically, a component specification should define:
* The component’s inputs and outputs
* The container image that your component’s code runs in, the command to use to run your component’s code, and the command-line arguments to pass to your component’s code
* The component’s metadata, such as the name and description

Note that here as we are going to build each component from docker images, ***<span style="color:blue">you do not need to run</span>*** following code blocks for train and evaluation in this notebook. We mainly guide you through the flow of each component design in this design section.

#### Design Train Component

We first design the component for training. Codes can be found in [train/train.py](./train/train.py). 

Train component takes three inputs: `trial`, `epoch`, and `patience`, and would export the trained model as output which would later be used as input of model evaluation.

Most codes follow the original workflow of the model itself.

**Import packages**
```python
import numpy as np
import os
from sklearn.utils import shuffle           
import matplotlib.pyplot as plt             
import tensorflow as tf                
import pandas as pd
from tensorflow.keras.models import load_model
import os
import shutil
import argparse
import autokeras as ak
```
Among above packages, `argparse` is specifically useful for our pipeline component design. This package would be used later to parse command-line arguments into component inputs.

**Declare input parameters**

Remember that when Kubeflow Pipelines executes a component, this component’s inputs are passed in as command-line arguments. So here we need to define and parse the command-line arguments, using `argparse`.
```python
parser = argparse.ArgumentParser()
parser.add_argument('--trial', type=int)
parser.add_argument('--epoch', type=int)
parser.add_argument('--patience', type=int)

args = vars(parser.parse_args())

trials = args['trial']
epochs = args['epoch']
patience = args['patience']
```
In this example, the Train component takes three inputs as parameters: `trial`, `epoch`, and `patience`. You would need to specify these three inputs before running this pipeline. We would discuss this more in details later in running pipeline section.

Some metadata of this model is declared and defined then, following the model design itself.
```python
project="Facial-keypoints"
run_id= "1.8"
resume_run = True

MAX_TRIALS=trials
EPOCHS=epochs
PATIENCE=patience
```

**Extract data**

The model then extracts data and saves the data to attached *extenal PVC* at location `/data`. We would later need to specifyc this PVC and let Kubeflow pipelines know what outputs this Train component would produce and where to store later in component specification.

Training dataset and test dataset, in this example, are stored in [train/my_data](./train/my_data). **Remember to change this part if you change the path of datasets storage.**
```python
base_dir='./train/my_data/'
train_dir_zip=base_dir+'training.zip'
test_dir_zip=base_dir+'test.zip'

from zipfile import ZipFile
with ZipFile(train_dir_zip,'r') as zipObj:
    zipObj.extractall('/data')
    print("Train Archive unzipped")
with ZipFile(test_dir_zip,'r') as zipObj:
    zipObj.extractall('/data')
    print("Test Archive unzipped")
```
Note that the overall flow of this data extraction part follows from the original model. The only things we need to change for pipeline component design is the path, i.e. location, for data storage.

**Process data**

This part, along with following data training part, follow from the model itself. No more changes needed for pipeline component design for this part.
```python
train_dir='/data/training.csv'
test_dir='/data/test.csv'
train=pd.read_csv(train_dir)
test=pd.read_csv(test_dir)

train=train.dropna()
train=train.reset_index(drop=True)

X_train=[]
Y_train=[]

for img in train['Image']:
    X_train.append(np.asarray(img.split(),dtype=float).reshape(96,96,1))
X_train=np.reshape(X_train,(-1,96,96,1))
X_train = np.asarray(X_train).astype('float32')
    
for i in range(len((train))): 
    Y_train.append(np.asarray(train.iloc[i][0:30].to_numpy()))
Y_train = np.asarray(Y_train).astype('float32')
```

**Train data**
```python
reg = ak.ImageRegressor(max_trials=MAX_TRIALS)
reg.fit(X_train, Y_train, validation_split=0.15, epochs=EPOCHS)
```

**Export trained model**

Finally, we need to export our trained model to our externally attached PVC, so that our Evaluate component can then take this trained model as input.
```python
my_model = reg.export_model()
my_model.save('/data/model_autokeras', save_format="tf")
```

#### Design Evaluation Component

We then design our Evaluation component. Codes can be found in [evaluation/eval.py](./evaluate/eval.py). 

This component takes the trained model as input. Some of the results, the submission file, would be directly printed out in log. The complete results, which is a pretty big file, would be saved as a `.csv` in PVC.

The overall logic follows from original model design.

**Import packages**
```python
from tensorflow.keras.models import load_model
import autokeras as ak
import pandas as pd
import numpy as np
```

**Load and view trained model**

First, we need to load our trained model, the output of our Train component.
```python
loaded_model = load_model("/data/model_autokeras", custom_objects=ak.CUSTOM_OBJECTS)
```
You may print the trained model summary, and you can see these printed contents in `main-logs` in `Output artifacts` on Kubeflow UI after the pipeline finishes running. More details on this would be discussed later in running pipeline section.
```python
### Pint model summary
print(loaded_model.summary())

test_dir='/data/test.csv'
test=pd.read_csv(test_dir)

X_test=[]
for img in test['Image']:
    X_test.append(np.asarray(img.split(),dtype=float).reshape(96,96,1))
X_test=np.reshape(X_test,(-1,96,96,1))
X_test = np.asarray(X_test).astype('float32')
```

**Predict**

```python
y_pred = loaded_model.predict(X_test)
```

**Create submission file**

As the submission file is pretty big, we store it under `/data` in our PVC container, the same place where we extract our training and testing data into. For you to have a quick look, we also directly print part of it, which would be displayed in `main-logs` after pipeline finishes running.
```python
y_pred= y_pred.reshape(-1,)
submission = pd.DataFrame({'Location': y_pred})
submission.to_csv('/data/submission.csv', index=True , index_label='RowId')

res = pd.read_csv('/data/submission.csv')
print()
print('***********************************************')
print(res)
```

### Containernize Pipeline Components

Now, we have gone through and understood the logic of pipeline component design. We then start to containernize our pipeline components.

#### Write Dockerfile
We use Docker to build images. Basically, Docker can build images automatically by reading the instructions from a Dockerfile. A Dockerfile is a text document that contains all the commands a user could call on the command line to assemble an image. 

Instructions and details of how to write a Dockerfile can be found on [Docker's official docs](https://docs.docker.com/engine/reference/builder/).

In this example, we provide you with following Dockerfile for Train component and Evaluate component.
```dockerfile
FROM "ubuntu"
RUN apt-get update && yes | apt-get upgrade
RUN mkdir -p /tensorflow/models
RUN apt-get install -y git python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install tensorflow
RUN pip3 install jupyter
RUN pip3 install matplotlib
RUN pip3 install kfp==1.1.2
RUN pip install opencv-python-headless
RUN pip3 install pandas keras 
RUN pip3 install sklearn
RUN pip3 install autokeras
COPY . /
```
Codes can be found in both `train/Dockerfile` and `evaluate/Dockerfile`.

#### Build Docker Images
Build docker images for Train component and Evaluate component using `docker run` command.

More details about `docker run` commands can be found on [here](https://docs.docker.com/engine/reference/commandline/run/)

***OPTION 1***

We have already prepared you built image. If you did not personalize the codes or change the paths of files, feel free to directly use them and skip this part. The location of the image is already in pipeline generation codes. 

You may also pull the image to your local if you want.


```python
!docker pull harbor-repo.vmware.com/zxintong/docker_images@sha256:48cb43365f65adffc16db98bc6a05e62c13ab5dff7579d381cf8ef8d2e1da489
```

If you are Mac with M1 chip, you may need to pull following image:


```python
!docker pull harbor-repo.vmware.com/zxintong/docker_images@sha256:3418cabc178b04a24e0f2b767ccaf4cc0e3fad68c3a6f407b4508ace433b5d83
```

***OPTION 2***

Or, you can also build Docker images on your own locally

**Install Docker**

Make sure Docker is [installed](https://docs.docker.com/engine/install/) in your environment. And login after install.


```python
!docker login
```

**Build images**

Use `docker build` command to build Docker images.


```python
!docker build -f <dockerfile_path> -t <docker_username>/<docker_imagename>:<tag> .
```

If you only have one Dockerfile where you run above command, you may not need to specify `-f <dockerfile_path>`. 

Feel free to directly run following command to build docker image in this notebook, if you did not change paths of files. 


```python
!docker build -t docker_images:facial .
```

Or, you can also build images for train and evaluate separately.


```python
!cd train
```


```python
!docker build -t docker_images:facial_train .
```


```python
!cd ../evaluate
```


```python
!docker build -t docker_images:facial_eval .
```

***Note: if you are Mac M1 chip user, you may need to add following flag to `docker run`***


```python
!docker build --platform linux/amd64 -f <dockerfile_path> -t <docker_username>/<docker_imagename>:<tag> .
```

### Build Pipeline

So far we have finished designing pipeline components and containernizing them. It is now time for our pipeline generation.

#### Create Component Specifications
As discussed at the beginning introduction part, we need to first define component specifications which include
* The component’s inputs and outputs
* The container image that your component’s code runs in, the command to use to run your component’s code, and the command-line arguments to pass to your component’s code
* The component’s metadata, such as the name and description

**Import Kubeflow Pipeline packages**


```python
import kfp
from kfp import dsl
```

**Login to Docker if necessary**

If you want to use your own docker images stored locally, you may need to first login to Docker.


```python
!docker login # is not needed if you use our images, or store your image somewhere else
```

**Train Component**


```python
# Train component takes three inputs: trial, epoch, and patience
# return a ContainerOp instance, representing Train step in pipeline

def Train(trial, epoch, patience):
    vop = dsl.VolumeOp(name="pvc",
                       resource_name="pvc", size='1Gi', 
                       modes=dsl.VOLUME_MODE_RWO)

    return dsl.ContainerOp(
        name = 'Train', 
        image = 'harbor-repo.vmware.com/zxintong/docker_images@sha256:48cb43365f65adffc16db98bc6a05e62c13ab5dff7579d381cf8ef8d2e1da489',
        # IF YOU ARE MAC M1 CHIP USER, USER FOLLOWING
        # image = 'harbor-repo.vmware.com/zxintong/docker_images@sha256:3418cabc178b04a24e0f2b767ccaf4cc0e3fad68c3a6f407b4508ace433b5d83'
        command = ['python3', '/train/train.py'],
        arguments=[
            '--trial', trial,
            '--epoch', epoch,
            '--patience', patience
        ],
        pvolumes={
            '/data': vop.volume
        }
    )
```

First, we need to create and specify the persistent volume (PVC) for data storage, creating a `VolumeOP` instance.
```python
vop = dsl.VolumeOp(name="pvc",
                       resource_name="pvc", size='1Gi', 
                       modes=dsl.VOLUME_MODE_RWO)
```
We then create a `ContainerOp` instance, which would be understood and used as "a step" in our pipeline, and return this "step".
```python
return dsl.ContainerOp(
        name = 'Train', 
        image = 'harbor-repo.vmware.com/zxintong/docker_images@sha256:48cb43365f65adffc16db98bc6a05e62c13ab5dff7579d381cf8ef8d2e1da489', 
        # IF YOU ARE MAC M1 CHIP USER, USER FOLLOWING
        # image = 'harbor-repo.vmware.com/zxintong/docker_images@sha256:3418cabc178b04a24e0f2b767ccaf4cc0e3fad68c3a6f407b4508ace433b5d83'
        command = ['python3', '/train/train.py'],
        arguments=[
            '--trial', trial,
            '--epoch', epoch,
            '--patience', patience
        ],
        pvolumes={
            '/data': vop.volume
        }
    )
```
We need to specify the inputs (`trial`, `epoch`, and `patience`) in `arguments`, container image in `image`, and volume for data storage in `pvolumes`. Note that here in `image`, we provide you with our built images, containing both `train` folder and `evaluate` folder, stored on our internal Harbor repo. If you want to use your own image, please remember to change this value.

We also need to specify `command`. In this provided case, as we containernize the image at root directory, in command we need `python3 /train/train.py`. (If you containernize Train component and Evaluate component one by one in each own folder, you may need to change this value to `python3 train.py`.)

**Evaluate Component**


```python
# Evaluate component takes Train ContainerOp as input, and access Train ContainerOp's pvolumes to get the trained model stored in it
# return a ContainerOp instance representing Evaluate step in pipeline

def Evaluate(comp1):
    return dsl.ContainerOp(
        name = 'Evaluate',
        image = 'harbor-repo.vmware.com/zxintong/docker_images@sha256:48cb43365f65adffc16db98bc6a05e62c13ab5dff7579d381cf8ef8d2e1da489',
        # IF YOU ARE MAC M1 CHIP USER, USER FOLLOWING
        # image = 'harbor-repo.vmware.com/zxintong/docker_images@sha256:3418cabc178b04a24e0f2b767ccaf4cc0e3fad68c3a6f407b4508ace433b5d83'
        pvolumes={
            '/data': comp1.pvolumes['/data']
        },
        command = ['python3', '/eval/eval.py']
    )
```

Again, we need to create a `ContainerOp` instance and return it, to be used as a step in our pipeline.

Here, we provide container image in `image`, and command to run the python file for evaluation in `command`. Similary, remember to change these two values if you want to use your own docker images or if you containernize the component under different directory.

For Evaluate component, it does not need explicit argument by value. Instead, it takes the trained model as input. This trained model is generated by Train component, and cannot be passed directly by value, so we need to "pass" it by reference. The way we do this here is to store the trained model in `/data`, our attached externally PVC, so that as long as we specify this PVC here in `pvolumes`, the Evaluate component would be able to access our trained model.

#### Generate Pipeline

We are now ready to define out `pipeline` instance.


```python
@dsl.pipeline(
    name = 'facial keypoints detection pipeline',
    description = 'pipeline to detect facial keypoints')
def generate_pipeline(trial, epoch, patience):
    comp1 = Train(trial, epoch, patience)
    comp2 = Evaluate(comp1)
```

Run above function to build our pipeline.


```python
if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(generate_pipeline, 'face_pipeline' + '.yaml')
```

You should now be able to see a file called `face_pipeline.yaml` in current directory, same as this notebook.

### Run Pipeline

In our last cell, we compile our pipeline as a YAML file. 

Note that for testing purpose, we also provide you with two already-compiled pipeline YAML files, `face_pipeline_test_default.yaml` and `face_pipeline_test_amd64.yaml`. Feel free to directly download and use them.

To run this pipeline, go to Kubeflow UI. Navigate to Pipelines Page. Upload this pipeline by choosing "upload a file" option. Choose the YAML file we created just now.

![face1](./img/face1.png)

![face2](./img/face2.png)

![face3](./img/face3.png)

After the pipeline uploading process finishes, you should be able to see the pipeline graph. Create a experiment for this pipeline, and then create a run.

![face4](./img/face4.png)

You need to enter values for the three required inputs for Train: trial, epoch, and patience.

![face5](./img/face5.png)

The pipeline would start to run then. You would be able to see the running process in Runs Page on Kubeflow UI.

![face6](./img/face6.png)

The pipeline running may take some time, especially when you input a large trial or epoch. There would be a green symbol appears next to each component after its completion. And you can always click on each component to see its details, such as its input/output, volumes, logs, and pod.

![face7](./img/face7.png)

After the whole pipeline finishes running, click on Train Component and Evaluate Component, you should be able to see `main-logs` under Input/Output, Output artifacts. Click into it, you should then be able to see the detailed logs, and part of the submission, i.e. output of Evaluate Component.

Example logs are provided in [logs](./logs) folders.

### Troubleshooting
