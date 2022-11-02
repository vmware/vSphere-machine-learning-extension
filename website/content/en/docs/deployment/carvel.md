+++
title = "Deploy Kubeflow"
description = "Deploy Kubeflow 1.6 with Carvel Package and App Platform"
weight = 40
+++

## Preparation
---
#### Configure a Proxy
If your network have trouble accessing one of the following Docker registries:
- docker.io
- gcr.io
- quay.io

Please refer to [**Configure a Proxy**](../troubleshooting/proxy) to configure a proxy.

#### Kapp-controller
The Carvel package manager "Kapp-controller" is shipped with unified TKG preinstalled.

By running the commands, you should see a pod whose name starts with **kapp-controller**
```bash
$ kubectl get pod -A | grep kapp-controller

tkg-system    kapp-controller-5b8579cb89-bkgps     2/2     Running   0          13d
```

If not, you need to manually install `Kapp-controller` following the guide: [**Install Kapp-controller**](../troubleshooting/app-platform)

#### Install kctrl

`kctrl` a kapp-controller’s native CLI, which will be used to install Kubeflow Carvel Package.

Go to https://github.com/vmware-tanzu/carvel-kapp-controller/releases, and install one release version.

Or run the following command to install it.

```bash
export KCTRL_VERSION=v0.41.2

echo "Installing kctrl..."
dst_dir="/usr/local/bin"
if [[ `uname` == Darwin ]]; then
    binary_type=darwin-amd64
else
    binary_type=linux-amd64
fi
wget -O- github.com/vmware-tanzu/carvel-kapp-controller/releases/download/${KCTRL_VERSION}/kctrl-${binary_type} > /tmp/kctrl
sudo mv /tmp/kctrl ${dst_dir}/kctrl
chmod +x ${dst_dir}/kctrl
echo "Installed ${dst_dir}/kctrl ${KCTRL_VERSION}"
```

## Add PackageRepository
---
```bash
kubectl create ns carvel-kubeflow-namespace
kubectl config set-context --current --namespace=carvel-kubeflow-namespace

kctrl package repository add \
    --repository kubeflow-carvel-repo \
    --url projects.registry.vmware.com/kubeflow/kubeflow-carvel-repo:0.1
```

## Install Kubeflow
---

Run the command to print values schema of the Kubeflow package.

```bash
$ kctrl package available get -p kubeflow.community.tanzu.vmware.com/1.6.0 --values-schema

Target cluster 'https://10.117.233.12:6443' (nodes: tkgs-ubucluster-carvel-testing-control-plane-87649, 2+)

Values schema for 'kubeflow.community.tanzu.vmware.com/1.6.0'

Key                   Default       Type     Description  
CD_REGISTRATION_FLOW  true          boolean  Turn on Registration Flow, so that Kubeflow Central Dashboard will prompt new users to create a namespace (profile)  
IP_address            ""            string   EXTERNAL_IP address of istio-ingressgateway, valid only if service_type is LoadBalancer  
imageswap_labels      true          boolean  Add labels k8s.twr.io/imageswap: enabled to Kubeflow namespaces, which enable imageswap webhook to swap images.  
service_type          LoadBalancer  string   Service type of istio-ingressgateway. Available options: "LoadBalancer" or "NodePort"  
static_users          -             array    Dex static user. Hash is bcrypt hash value of password  

Succeeded
```

Create a values.yaml files according to values schema.

```bash
cat > values.yaml << 'EOF'

imageswap_labels: True

service_type: "LoadBalancer"

IP_address: ""

CD_REGISTRATION_FLOW: True

static_users: 
- email: "user@example.com"
  hash: "$2y$12$4K/VkmDd1q1Orb3xAt82zu8gk7Ad6ReFR4LCP9UeYE90NLiN9Df72"

EOF
```

Install Kubeflow 1.6.0 Carvel package and specify the values-file `values`.yaml by running:

```bash
kctrl package install \
    --wait-check-interval 5s \
    --wait-timeout 30m0s \
    --package-install kubeflow \
    --package kubeflow.community.tanzu.vmware.com \
    --version 1.6.0 \
    --values-file values.yaml
```

## Useful Commands:
---

Check PackageInstall Status
```bash
kubectl get PackageInstall kubeflow -o yaml
```

Print status of app created by package installation
```bash
kctrl package installed status --package-install kubeflow
```

Update to an updated values file
```bash
kctrl package installed update --package-install kubeflow --values-file values.yaml
```

Kapp-controller keeps reconciliating Kubeflow, which prevent you from editing a Kubeflow resource. In this case, you may want to pause or trigger of Kubeflow.

Pausing reconciliation for a package install
```bash
kctrl package installed pause --package-install kubeflow
```

Trigger reconciliation of package install
```bash
kctrl package installed kick --package-install kubeflow --wait --wait-check-interval 5s --wait-timeout 30m0s
```

Uninstall installed package
```bash
kctrl package installed delete --package-install kubeflow
```

Check more commands on kapp-controller docs: https://carvel.dev/kapp-controller/docs/v0.41.0/management-command/

## Trouble shooting
---

- When deleting the Kubeflow package, Some resources got stuck at `deleting` status.
```bash
# take namespace knative-serving as an example
kubectl patch ns knative-serving -p '{"spec":{"finalizers":null}}'
kubectl delete ns knative-serving --grace-period=0 --force
```

- During `kctrl package install`, you see errors like `Pending: ImagePullBackOff`. 

![](../assets/troubleshooting_imagepullerror.png)

Please refer to [**Configure a Proxy**](../troubleshooting/proxy) to configure a proxy.

After proxy is configured properly, you may need to uninstall and install Kubeflow again.
## What's Next
---

We have prepared an end-to-end tutorial for you to get started quickly. Check it out [Kubeflow Tutorial](../../kubeflow-tutorial/)
