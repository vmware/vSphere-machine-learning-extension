# Notebook Service

## Use Notebooks

### Login Kubeflow central dashboard

Default username and password: user@example.com, 12341234

### Create notebook server

* Click on the link "Notebooks" on the left navigation bar
* Click on the link "NEW NOTEBOOK" in the right new page
* Fill the required information about notebook server name and namespace
* Fill the required information about custom image address. We provide ML framework images on harobor-vm repos, for example, harbor-repo.vmware.com/zyajing/tf-jupyter-260:1.0
* Set options on resources, such as CPU, memory, GPU, et al.
* Click finish and wait the deployment compelte
* Connect to the newly created notebook server

### Machine Learning framework supported

#### Frameworks

* TensorFlow 2.6
* PyTorch 1.6
* PaddlePaddle 2.2

#### Nvidia driver and CUDA support

* For TKG node with GPU support, Nvidia driver version 450 and CUDA 11.2 are tested and suppported
* In general, Nvidia drivers support current and previous CUDA version

#### GPU sharing options

* Bitfusion, which virtualizes hardware accelerators such as GPUs to provide a pool of shared for AI/ML workloads
* Project Thunder. vSphere with Tanzu version 7 update 3 monthly patch 1 support Nvidia vGPU technology for AI/ML workloads

#### ML framework registry and docker files

* Registry hosted at [harbor-repo](https://harbor-repo.vmware.com/harbor/projects/4717/repositories)
* Machine learning framework docker files

### Notebook Samples

#### An example based on TensorFlow [source](https://www.tensorflow.org/text/tutorials/text_generation)

1. Create a notebook server based on TensorFlow 2.6. Create a new notebook by click "NEW NOTEBOOK". The address
   of custom image is "harbor-repo.vmware.com/zyajing/tf-jupyter-260:1.0". Set CPU number to 1, memory to 2G, GPU
   to none and storage to 10G. Then click "CONNECT" when the status of the notebook server is running.
2. Train the text generation model. Download the text generation code from [here](https://github.com/AmyHoney/mlopsSync/blob/main/notebook-service/framework-example/tensorflow/text_generation.ipynb). Copy the text generation code to the notebook server
   using the following command.

```shell
kubectl cp text_generation.ipynb tf-text-generation-0:/home/jovyan/ -n kubeflow-user-example-com
```

#### More examples

* [Train text generation model on Tensorflow](https://www.tensorflow.org/text/tutorials/text_generation)
* [Optimizing neural network model using mnist dataset on Pytorch](https://pytorch.org/tutorials/beginner/basics/quickstart_tutorial.html)
* [Image classification using mnist dataset by LeNet on PaddlePaddle](https://www.paddlepaddle.org.cn/documentation/docs/zh/practices/cv/image_classification.html)
