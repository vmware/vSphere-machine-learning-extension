+++
title = "Prerequisites"
description = "Set up environment for deploying Kubeflow on vSphere"
weight = 10
+++

- **vSphere 8.0 with Tanzu Deployment**: For a greenfield deployment (no vSphere with Tanzu deployed yet), you will need to deploy vSphere with Tanzu first.
  - For the standard and regular setup, please refer to VMware official document [vSphere with Tanzu Configuration and Management](https://docs.vmware.com/en/VMware-vSphere/7.0/vmware-vsphere-with-tanzu/GUID-152BE7D2-E227-4DAA-B527-557B564D9718.html).
  - If you only have limited hardware resource, for example, one single server host, please refer to [this document](./single_host) of vSphere with Tanzu deployment for testing purpose, or use [this workaround](https://williamlam.com/2021/09/single-node-supervisor-control-plane-vm-for-vsphere-with-tanzu-now-possible-in-vsphere-7-0-update-3.html) for single host.
- **If you want to use Nvidia GPU resources on vSphere platform, setup vGPU TKG with following documents**
  - **vGPU**: [Deploy AI/ML Workloads on Tanzu Kubernetes Clusters](https://docs.vmware.com/en/VMware-vSphere/7.0/vmware-vsphere-with-tanzu/GUID-2B4CAE86-BAF4-4411-ABB1-D5F2E9EF0A3D.html)
