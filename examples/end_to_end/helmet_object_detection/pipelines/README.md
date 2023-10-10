# Helmet Detection Model Deployment with Kubeflow Pipelines

## Instruction

Kubeflow Pipelines is a platform for building and deploying portable, scalable machine learning (ML) workflows based on Docker containers.
Each pipeline represents an ML workflow, and includes the specifications of all inputs needed to run the pipeline, as well the outputs of all components.
If you are not familar with the Kubeflow Pipeline, you can refer to [Kubeflow Pipelines](https://www.kubeflow.org/docs/components/pipelines/).

## Build Pipeline

In this tutorial, we will guide you through the Helmet Detection Example (as mentioned [here](https://github.com/vmware/vSphere-machine-learning-extension/tree/main/examples/end_to_end/helmet_object_detection/notebook)) to build up and run Kubeflow pipelines

We provide you a [helmet_detection_pipeline.yaml](https://github.com/vmware/vSphere-machine-learning-extension/blob/main/examples/end_to_end/helmet_object_detection/pipelines/helmet_detection_pipeline.yaml). For quick-test you can execute the pipeline using this yaml file. [here are the steps](https://github.com/vmware/vSphere-machine-learning-extension/blob/main/examples/end_to_end/helmet_object_detection/pipelines/README.md#upload-the-pipeline-in-freestone-kubeflow-dashboard)

If you prefer to build the pipeline by yourself, please follow the pipeline building steps in [helmet_detection_pipeline.ipynb](https://github.com/vmware/vSphere-machine-learning-extension/blob/main/examples/end_to_end/helmet_object_detection/pipelines/helmet_detection_pipeline.ipynb) in the Kubeflow Notebook.

### Here are the steps with explanation
### Step 1: Install Kubeflow Pipeline SDK and import the required kfp packages to run the pipeline

First, install the Pipeline SDK using the following command. If you run this command in a Jupyter notebook, restart the kernel after installing the SDK.

```bash
$ pip install kfp==1.6.3
$ pip show kfp
```

```python
import kfp
import kfp.components as comp
import kfp.dsl as dsl
from kfp.components import OutputPath
from typing import NamedTuple
from kubernetes import client
```

### Step 2: Design the pipeline components

Our Kubeflow pipeline is broken down into four pipeline components:

- Create Storage Component
- Data Ingesting Component
- Data Processing Component
- Model Training Component

In this example, we provide you the following Dockerfile for Data component and Train component. Please use the dockerfile in the notebook folder and run `docker build . -t helmet_detection_pipeline:v1` to build a image.

```bash
FROM ubuntu:20.04
# Downloads to user config dir
ADD https://ultralytics.com/assets/Arial.ttf https://ultralytics.com/assets/Arial.Unicode.ttf /root/.config/Ultralytics/
# Install linux packages
RUN apt update
RUN DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC apt install -y tzdata
RUN apt install --no-install-recommends -y python3-pip git zip curl htop libgl1-mesa-glx libglib2.0-0 libpython3.8-dev
# RUN alias python=python3
# Install pip packages
COPY requirements.txt .
RUN python3 -m pip install --upgrade pip wheel
RUN pip install -r requirements.txt -i https://pypi.douban.com/simple/
COPY . /
```

#### Compile Data Ingest Component
First, we need to create and specify the persistent volume (PVC) for data storage, creating a VolumeOP instance. You can change the VolumeOP name and resource_name to create your data storage.

```python
vop = dsl.VolumeOp(name="create_helmet_data_storage_volume",
                    resource_name="helmet_data_storage_volume", size='10Gi',
                    modes=dsl.VOLUME_MODE_RWO)
```
You then create a ContainerOp instance, which would be understood and used as "a step" in your pipeline, and return this "step".
```python
return dsl.ContainerOp(
        name = 'Download Data',
        image = 'harbor-repo.vmware.com/juanl/helmet_detection_pipeline:v1',
        command = ['python3', 'ingest_pipeline.py'],
        arguments=[
            '--dataurl', dataurl,
            '--datapath', datapath
        ],
        pvolumes={
            '/VOCdevkit': vop.volume
        }
    )
```

You need to specify the inputs `dataurl`, `datapath` in arguments, container image in image, and volume for data storage in pvolumes. Note that here in image, we provide you built images, containing both train folder and evaluate folder, stored on our projects.registry repo. If you want to use your own image, please remember to change this value.

You also need to specify command. In this provided case, as we containernize the image at root directory, in command you need python3 `ingest_pipeline.py`. (If you containernize Train component and Evaluate component one by one in each own folder, you may need to change this value to python3 ingest_pipeline.py.)

#### Declare Data Processing Component

```python
def data_process(comp1):
    return dsl.ContainerOp(
        name = 'Process Data',
        image = 'harbor-repo.vmware.com/juanl/helmet_detection_pipeline:v1',
        command = ['python3', 'prepare.py'],
        pvolumes={
            '/VOCdevkit': comp1.pvolumes['/VOCdevkit']
        }
    )
```

#### Declare Model Training Component

```python
def model_train(comp2, epoch, device, workers_num):
    return dsl.ContainerOp(
        name = 'Model Training',
        image = 'harbor-repo.vmware.com/juanl/helmet_detection_pipeline:v1',
        pvolumes={
            '/VOCdevkit': comp2.pvolumes['/VOCdevkit']
        },
        # command=['sh', '-c'],
        # arguments=['nvidia-smi'],
        command = ['python3', 'train_pipeline.py'],
        arguments=[
            '--epoch', epoch,
            '--device', device,
            '--workers', workers_num,
        ],
    ).set_gpu_limit(1).set_cpu_request('2').set_memory_request('8G')
```

### Compile pipeline

Execute below function to compile the YAML file:

```python
@dsl.pipeline(
    name = 'helmet detection pipeline',
    description = 'pipeline to detect helmet')
def generate_pipeline(dataurl, datapath, epoch, device, workers_num):
    comp1 = data_download_from_url(dataurl, datapath)
    comp2 = data_process(comp1)
    comp3 = model_train(comp2, epoch, device, workers_num)

if __name__ == '__main__':
  import kfp.compiler as compiler
  compiler.Compiler().compile(generate_pipeline, './generated_yaml_files/helmet_detection_pipeline' + '.yaml')
```

## Execute the Pipeline

Following the steps in your notebook, you should be able to see a file called `helmet_detection_pipeline.yaml` in folder `generated_yaml_files`.. So here we provide you a brief guide on how to execute a pipeline.

### Upload the pipeline in Kubeflow on vSphere Dashboard

Once you have the compiled YAML file, download it. In Kubeflow on vSphere Dashboard, go to pipelines dashaborad by clicking the “Pipelines” on the left-side toolbar. And then click the “Upload Pipeline” button.

![Image text](https://github.com/vmware/vSphere-machine-learning-extension/tree/main/examples/end_to_end/helmet_object_detection/pipelines/imgs/helmet-pipeline-01.png)
![Image text](https://github.com/vmware/vSphere-machine-learning-extension/tree/main/examples/end_to_end/helmet_object_detection/pipelines/imgs/helmet-pipeline-02.png)

### Create experiment and run

Create an experiment for this pipeline. This time, you need to provide two inputs, dataset and data_path, exactly the ones for our first step Data Download. If you do not intend to make any personalization on datasets and data path, enter following values

![Image text](https://github.com/vmware/vSphere-machine-learning-extension/blob/main/examples/end_to_end/helmet_object_detection/pipelines/imgs/helmet-pipeline-03.png)
![Image text](https://github.com/vmware/vSphere-machine-learning-extension/blob/main/examples/end_to_end/helmet_object_detection/pipelines/imgs/helmet-pipeline-04.png)

### Check logs and outputs
![Image text](https://github.com/vmware/vSphere-machine-learning-extension/blob/main/examples/end_to_end/helmet_object_detection/pipelines/imgs/helmet-pipeline-05.png)

### Delete pipeline

![Image text](https://github.com/vmware/vSphere-machine-learning-extension/tree/main/examples/end_to_end/helmet_object_detection/pipelines/imgs/helmet-pipeline-06.png)
