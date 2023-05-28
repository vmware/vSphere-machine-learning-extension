+++
title = "Bitfusion"
description = "vSphere Infrastructure resources integrate with Kubeflow components"
weight = 10
+++

This chapter is for Kubeflow integration with vSphere Infrastructure resources such as Bitfusion server or Nvidia GPU. 

## VMware Bitfusion

We will explain in this session the benefits of the Kubeflow integration with VMware vSphere Bitfusion. 

Since AI/ML is a new type of application, we should look at its requirements and make sure we can meet them. There are two requirements we are considering here. You will likely want to run your app in containers and You will likely want to use hardware acceleration (a GPU, typically) to run your AI/ML application.

However, GPUs have traditionally been difficult to share. As a piece of hardware sitting on a bus, only the software running local to that bus has been able to access it. If you move the software, you lose access. Even worse, two virtual machines, both running locally to a GPU, cannot share it. A GPU must be passed exclusively to one VM or the other. Compounding that, a single user, VM, or application seldom uses the GPU efficiently. It is not atypical for GPUs to sit idle 85% of the time. The industry average on this is hard to obtain, and it varies a lot from use-case to use-case. But if the price of a GPU seems high, it seems even higher when it is underutilized to this extent.

Enter VMware vSphere Bitfusion. It lets you share GPUs in two ways. Bitfusion sets up a pool of GPU servers, and gives GPU access, remotely, across the network, to applications or microservices running on client VMs or containers set up for each piece of software. GPUs, over the course of time, can “fly” from one application to another, being allocated and deallocated dynamically whenever an application needs hardware acceleration. Bitfusion also partitions GPUs into fractions of arbitrary size (it is the GPU memory that is partitioned), so the GPU can be used concurrently by multiple applications. All this raises the utilization and efficiency of the precious GPU resources.

An inteagrated [VMware vSphere](https://www.vmware.com/products/vsphere.html#resources), Bitfusion delivers the ability to share resources in addition to providing better utilization of existing or new hardware accelerator resources. Bitfusion can dynamically share hardware accelerator devices, such as GPUs, across a network. And this technology is for specific use with AI/ML software such as *TensorFlow* and *PyTorch*.

For more information about Bitfusion, please visit [vSphere Bitfusion document page](https://docs.vmware.com/cn/VMware-vSphere-Bitfusion/index.html).

## Installation & Use Case

The bulk of this session is a detailed example of how to run a TensorFlow application in a containerized Bitfusion environment with remote GPU access.

### Installation

![1](../1_arch.png)

There is the achitecture of the Kubeflow Jupyer Notebook integration with Bitfsion. You can follow the official guide to install bifusion server with the [Bifusion Device Plugin](https://github.com/vmware/bitfusion-with-kubernetes-integration). We also upload the package of kubeflow integration with bitfusion in the [Github Repo](https://github.com/harperjuanl/kubeflow-v1.6.0-rc.1)

How can we use the same image for both of Bitfusion and Nvidia. Let me show you the reason. Under the hood, when a Notebook created, we’ve modified the Kubeflow code to put bitfusion configuration info into the annotations based on your selection and record the GPU resource requests and limits.

Then the modified Notebook controller will transfer all these information related to the bitfusion to the “StatefulSet” resource objects.   

When “Bitfusion Device Plugin” sees that information in the Pod Resource, it will inject the bitfusion client library, server config, client certificate and all necessary information automatically  to make this notebook a valid bitfusion client. 


### Use Case

When we are creating Jupyter Notebook instance in the Notebook page of the Kubeflow dashboard, we pick the name and choose one of the Kubeflow official images. As you can see in the following figure, in the GPU resources settings, we choose th “BITFUSION” option. After launch the new notebook, we can easily run the bitfusion client applications in the Jupyter Notebook. 

![2](../2_notebook.png)

We plan to run a bitfusion benchmark applications in this use case. From the output of the benchmark, we will find information related to the Bitfusion server resource allocation. You can get the source code of the example from [here]().

```bash
%env PATH=$PATH:/bitfusion/bitfusion-client-ubuntu2004_4.5.0-4_amd64.deb/usr/bin:/opt/conda/bin

# test for occupy bitfusion 
!bitfusion run -n 1 -- bash

# TensorFlow benchmark assuming an imagenet dataset
!bitfusion run -n 1 -- python3 \
./benchmarks/scripts/tf_cnn_benchmarks/tf_cnn_benchmarks.py \
--data_format=NCHW \
--batch_size=64 \
--model=resnet50 \
--variable_update=replicated \
--local_parameter_device=gpu \
--nodistortions \
--num_gpus=1 \
--num_batches=100 \
--data_dir=../data \
--data_name=imagenet \
--use_fp16=False

# release bitfusion resource
bitfusion release_gpus -f /tmp/bitfuiosn...
```


When running the bitfusion notebook, we can monitor the GPU usage in the vCenter Server console. **Please refer to the following figure.**

![4](../4_bitfusion_console.png)


## Roadmap

In the above use case, you may find that we can only run python scripts with a bitfusion wrapper. But we will build a “Bitfusion Kernel” in the near feature as shown on the screen to let users to run every python code blocks into bitfusion environment.

![3](../3_bitfusion_kernel_roadmap.png)
