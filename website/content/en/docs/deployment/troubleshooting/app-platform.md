+++
title = "Install Kapp-controller"
description = "If you Kapp-controller is not running on your cluster"
weight = 10
+++

Go to https://github.com/vmware-tanzu/carvel-kapp-controller/releases, and install one release version. 

Or run the following command to install it.

```bash
export KAPP_CONTROLLER_VERSION=v0.41.2

cat << EOF | kubectl apply -f -
---
apiVersion: v1
kind: Namespace
metadata:
  name: kapp-controller
---
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: rb-all-sa_ns-kapp-controller
  namespace: kapp-controller
roleRef:
  kind: ClusterRole
  name: psp:vmware-system-privileged
  apiGroup: rbac.authorization.k8s.io
subjects:
- kind: Group
  apiGroup: rbac.authorization.k8s.io
  name: system:serviceaccounts:kapp-controller
---
EOF

kubectl apply -f https://github.com/vmware-tanzu/carvel-kapp-controller/releases/download/${KAPP_CONTROLLER_VERSION}/release.yml
```


After installation, you should see a pod whose name starts with **kapp-controller** when running the following command:

```bash
$ kubectl get pod -A | grep kapp-controller

kapp-controller    kapp-controller-5b8579cb89-bkgps     2/2     Running   0          13d
```