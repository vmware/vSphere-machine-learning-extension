+++
title = "Configure a proxy"
description = "If you encounter ImagePullBackOff error"
weight = 10
+++

## Quick deployment
---

1. [VMware internal proxy] Deploy imageswap webhook with default settings:
```bash
git clone git@github.com:xujinheng/imageswap-webhook-proxycache.git
cd imageswap-webhook-proxycache
# Deletion is necessary to avoid MutatingWebhookConfiguration updating failures
# see issue https://github.com/phenixblue/imageswap-webhook/issues/78
kubectl delete -f imageswap_deploy_VMware.yaml --ignore-not-found=true
kubectl delete MutatingWebhookConfiguration imageswap-webhook --ignore-not-found=true
kubectl apply -f imageswap_deploy_VMware.yaml
```

1. [Public proxy] Deploy imageswap webhook with default settings:
```bash
git clone git@github.com:xujinheng/imageswap-webhook-proxycache.git
cd imageswap-webhook-proxycache
# Deletion is necessary to avoid MutatingWebhookConfiguration updating failures
# see issue https://github.com/phenixblue/imageswap-webhook/issues/78
kubectl delete -f imageswap_deploy_Public.yaml --ignore-not-found=true
kubectl delete MutatingWebhookConfiguration imageswap-webhook --ignore-not-found=true
kubectl apply -f imageswap_deploy_Public.yaml
```

Please Refer to https://github.com/xujinheng/imageswap-webhook-proxycache for more details.

## Proxy resources
---

| Registry   | Public Proxy                     | Internal VMware Proxy                                    |
| ---------- | -------------------------------- | -------------------------------------------------------- |
| docker.io  | docker.nju.edu.cn                | harbor-repo.vmware.com/dockerhub-proxy-cache             |
| gcr.io     | gcr.nju.edu.cn                   | harbor-repo.vmware.com/gcr-proxy-cache                   |
| k8s.gcr.io | gcr.nju.edu.cn/google-containers | harbor-repo.vmware.com/gcr-proxy-cache/google-containers |
| ghcr.io    | ghcr.nju.edu.cn                  | harbor-repo.vmware.com/ghcr-proxy-cache                  |
| quay.io    | quay.nju.edu.cn                  |                                                          |
