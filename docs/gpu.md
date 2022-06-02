# GPU Support

This part contains information on how to enable GPU for Kubeflow on vSphere platform.
There are several options to take advantage of GPU resources, for example, DirectPath I/O,
Nvidia MIG, Bitfusion, et al.

## Support for GPU DirectPath I/O

### vSphere Setup for Tanzu with NVIDIA virtual GPUs

* Setup the GPU host server with NVIDIA virtual GPU (passthrough model)
* Create a Namespace and Tanzu Kubernetes Grid (TKG) cluster
* Creating an Ubuntu VM for the GPU-enabled node
* Enabling Access to a TKG Cluster Node via the Supervisor Cluster
* Accessing a TKG Cluster ControlPlane Node to generate a token, used to join the VM to the cluster. Detailed step could be found [here](https://blogs.vmware.com/china/2020/05/02/vsphere-with-kubernetes-nodeaccess/)
* Join the new Ubuntu VM with GPU to the TKG Cluster
* CNI Setup for manually created worker node

### Access the GPU-enabled Tanzu Kubernetes Grid cluster and deploy NVIDIA GPU Operator

* Build GPU Operator 1.5.1 with GPU drivers
* Access the GPU-enabled TKG Cluster
* Deploy the NVIDIA GPU Operator with NVIDIA virtual GPU on the TKG cluster

### Deploy Sample AI and ML applications on the GPU-Enabled TKG Cluster

* Deploy the TF-Notebook Application
* Deploy the Intelligent Video Analytics (IVA) Application

## Support for Nvidia vGPU/MIG

For more information about Nvidia vGPU/MIG support, refer to [VMware vSphere with Tanzu and NVIDIA AI Enterprise](https://blogs.vmware.com/vsphere/2022/01/vmware-vsphere-with-tanzu-and-nvidia-ai-enterprise-1-1.html)

## Support for Bitfusion

We also provide a Kubernetes device plugin for Bitfusion used for GPU resouce
management under vSphere with Tanzu. It is an [open source project](https://github.com/vmware/bitfusion-with-kubernetes-integration) hosted at GitHub.
