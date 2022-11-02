+++
title = "Create and configure a vSphere Namespace"
description = "Create and configure a vSphere Namespace"
weight = 20
+++

## Create a Content Library
---
Follow the docs [here](https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-with-tanzu-installation-configuration/GUID-6519328C-E4B7-46DE-BE2D-FC9CA0994C39.html) to create a Subscribed Content Library.

#### Examples Configurations:
| Settings         | Values                                                                             |
| ---------------- | ---------------------------------------------------------------------------------- |
| Name             | content-library-kubeflow                                                           |
| Subscription URL | http://build-squid.eng.vmware.com/build/mts/release/bora-20532714/publish/lib.json |
| Authentication   | Not enabled                                                                        |
| Library content  | Download all library content immediately                                           |
| Security policy  | Not enabled                                                                        |

You are free to select one of the following Tanzu Kubernetes Release as `Subscription URL`:
| Tanzu Kubernetes Release Supported   | Subscription URL                                                                   |
| ------------------------------------ | ---------------------------------------------------------------------------------- |
| v1.21.6---vmware.1-tkg.1             | https://wp-content.vmware.com/v2/latest/lib.json                                   |
| v1.22.11---vmware.2-tkg.2-zshippable | http://build-squid.eng.vmware.com/build/mts/release/bora-20532714/publish/lib.json |
| v1.23.8---vmware.2-tkg.2-zshippable  | https://wp-content.vmware.com/v2/latest/lib.json                                   |

> Note: If the link expires, please find a new build of **ubuntu-ova** with **Tanzu Kubernetes Release versions supported** here: https://buildweb.eng.vmware.com/ob/?product=cayman_tkg_ova_signer&branch=All+Branches&duration=alltime&only_ondisk=true

## Create VM Classes and Storage Policies [optional]
---

> Note: you can skip the step if there are existing VM classes and storage policies that meet the needs.

Please follow the docs to create or use existing VM classes and storage policies. Make sure the specification meets the computing resources listed in the table below.

1. Create a VM class: https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-with-tanzu-services-workloads/GUID-18C7B2E3-BCF5-488C-9C50-937E29BB0C48.html
   
2. Create a storage policy: https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-storage/GUID-8D51CECC-ED3B-424E-BFE2-43379729A653.html

##### Kubernetes Cluster Resources (Recommended)
| VM            | VM Count | CPU Cores | Memory (GB) | Disk (GB) | Nvidia GPU |
| ------------- | -------- | --------- | ----------- | --------- | ---------- |
| Control Plane | 1        | 4         | 16          | 20        | 0          |
| Worker        | 2        | 8         | 12          | 70        | 1+          |

## Create a vSphere namespace
---
Follow the docs [here](https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-with-tanzu-installation-configuration/GUID-177C23C4-ED81-4ADD-89A2-61654C18201B.html) to create and configure a vSphere namespace, including the storage policies, Content Library and Associated VM Classes you would like to use later when creating the Tanzu Kubernetes Cluster.

#### Examples Configurations:
| Settings              | Values                   |
| --------------------- | ------------------------ |
| Name                  | namespace-kubeflow       |
| Storage Policies      | pacific-storage-policy   |
| Content Library       | content-library-kubeflow |
| Associated VM Classes | guaranteed-large         |

## What's Next
---

Now you are ready to move to the next section [Create a Tanzu Kubernetes Cluster](../cluster)
