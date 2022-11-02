+++
title = "Prerequisites"
description = "Set up environment for deploying Kubeflow on vSphere"
weight = 10
+++

- If you don't have any hardware resource or do not want to setup from the ground, reach out to us at the slack channel [#peach](https://vmware.slack.com/archives/C046YEZMWQK) to request an account for Kubeflow and JupyterLab extension trials.
- **vSphere 8.0 with Tanzu Deployment**: For a greenfield deployment (no vSphere with Tanzu deployed yet), you need to deploy vSphere with Tanzu first. 
  - For the standard and regular setup, please refer to VMware official document [vSphere with Tanzu Configuration and Management](https://docs.vmware.com/en/VMware-vSphere/7.0/vmware-vsphere-with-tanzu/GUID-152BE7D2-E227-4DAA-B527-557B564D9718.html).
  - If you only have limited hardware resource, for example, one server node, please refer to [this document](https://confluence.eng.vmware.com/display/VCP/TKG+demo+appliance+setup+guide) of vSphere with Tanzu deployment for testing purpose.
- **If you want to use Nvidia GPU resources on vSphere platform, setup vGPU or Bitfusion under TKG with following documents**
  - **vGPU**: [Deploy AI/ML Workloads on Tanzu Kubernetes Clusters](https://docs.vmware.com/en/VMware-vSphere/7.0/vmware-vsphere-with-tanzu/GUID-2B4CAE86-BAF4-4411-ABB1-D5F2E9EF0A3D.html) / [Internal Docs and Resources](https://wiki.eng.vmware.com/IDEsxGpu/2022/Drivers)
  - **Bitfusion**: [bitfusion_device_plugin deployment on TKG 1.2+](https://confluence.eng.vmware.com/pages/viewpage.action?pageId=1512830863)