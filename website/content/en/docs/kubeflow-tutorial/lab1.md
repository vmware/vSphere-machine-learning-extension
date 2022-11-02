+++
title = "Lab1 Getting Started"
description = "Access Kubeflow Central Dashboard, User Creation"
weight = 10
+++

## Access Kubeflow Central Dashboard

To get the IP address of Kubeflow Central Dashboard, there are three options:

- When you set `service_type` to `LoadBalancer`, run the command below and visit `EXTERNAL-IP` of `istio-ingressgateway`.
    ```bash
    ## In this example, we should visit http://10.105.151.142:80
    $ kubectl get svc istio-ingressgateway -n istio-system

    NAME                   TYPE           CLUSTER-IP       EXTERNAL-IP      PORT(S)                                                                      AGE
    istio-ingressgateway   LoadBalancer   198.51.217.125   10.105.151.142   15021:31063/TCP,80:30926/TCP,443:31275/TCP,31400:30518/TCP,15443:31204/TCP   11d
    ```

- When you set `service_type` to `NodePort`, run the command below and visit `nodeIP`:`nodePort`.
    ```bash
    ## In this example, any one of the following will work:
    # http://10.105.151.73:30926
    # http://10.105.151.74:30926
    # http://10.105.151.75:30926

    $ kubectl get svc istio-ingressgateway -n istio-system

    NAME                   TYPE       CLUSTER-IP       EXTERNAL-IP   PORT(S)                                                                      AGE
    istio-ingressgateway   NodePort   198.51.217.125   <none>        15021:31063/TCP,80:30926/TCP,443:31275/TCP,31400:30518/TCP,15443:31204/TCP   11d


    $ kubectl get nodes -o wide

    NAME                                                      STATUS   ROLES                  AGE   VERSION            INTERNAL-IP     EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION      CONTAINER-RUNTIME
    v1a2-v1-23-8-tkc-v100-8c-dcpvc-4zct9                      Ready    control-plane,master   26d   v1.23.8+vmware.2   10.105.151.73   <none>        Ubuntu 20.04.4 LTS   5.4.0-124-generic   containerd://1.6.6
    v1a2-v1-23-8-tkc-v100-8c-workers-zwfx4-77b7df85f7-f7f6f   Ready    <none>                 26d   v1.23.8+vmware.2   10.105.151.74   <none>        Ubuntu 20.04.4 LTS   5.4.0-124-generic   containerd://1.6.6
    v1a2-v1-23-8-tkc-v100-8c-workers-zwfx4-77b7df85f7-l5mp5   Ready    <none>                 26d   v1.23.8+vmware.2   10.105.151.75   <none>        Ubuntu 20.04.4 LTS   5.4.0-124-generic   containerd://1.6.6
    ```

- Use port-forwarding. Then visit the IP address of your client-side machine.
    ```bash
    # if you are running the command locally, you should visit http://localhost:8080
    
    kubectl port-forward -n istio-system svc/istio-ingressgateway --address 0.0.0.0 8080:80
    ```

Then you can use default user and password to login

![](../screenshots/dex.png)

```bash
Email: user@example.com
Password: 12341234
```

![](../screenshots/centraldashboard.png)

## Static User Creation

Dex allows use to create a static user, and store the username / password in Kubernetes `configmap` object.

1. Create a python file that create the hash of your password

    ```bash
    pip install passlib

    cat > password_hash.py << EOF
    import argparse
    from passlib.hash import bcrypt

    parser = argparse.ArgumentParser()
    parser.add_argument('--password', type=str, metavar='P')
    args = parser.parse_args()

    print(bcrypt.using(rounds=12, ident="2y").hash(args.password))
    EOF
    ```

2. Add new users to values.yaml files.
    ```bash
    cat > values.yaml << EOF

    imageswap_labels: True

    service_type: "LoadBalancer"

    IP_address: ""

    CD_REGISTRATION_FLOW: True

    static_users: 
    - email: "user@example.com"
      hash: $(python3 password_hash.py --password 12341234)
    - email: "admin@vsphere.local"
      hash: $(python3 password_hash.py --password 88888888)
    EOF
    ```

3. Update to an updated values file
   ```bash
    kctrl package installed update --package-install kubeflow --values-file values.yaml
    ```

4. Restart dex
    ```bash
    kubectl rollout restart deployment dex -n auth
    ```

Follow the Registration Flow, create your Kubeflow profile.

![](../screenshots/CD_REGISTRATION_FLOW_1.png)

![](../screenshots/CD_REGISTRATION_FLOW_2.png)

You will see a profile and namespace being created 
```bash
$ kubectl get profile,namespace admin

NAME                         AGE
profile.kubeflow.org/admin   3m40s

NAME              STATUS   AGE
namespace/admin   Active   3m40s
```

## Add pod-security-policy for your namespace

To prevent error like
```bash
`create Pod test-0 in StatefulSet test failed error: pods "test-0" is forbidden: PodSecurityPolicy: unable to admit pod: []`
```

Run the following command to Add pod-security-policy for the namespace you just created, it will grant access to create pods in the namespace. 
```bash
export NAMESPACE=admin

cat << EOF | kubectl apply -f -
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: rb-all-sa_ns-${NAMESPACE}
  namespace: ${NAMESPACE}
roleRef:
  kind: ClusterRole
  name: psp:vmware-system-privileged
  apiGroup: rbac.authorization.k8s.io
subjects:
- kind: Group
  apiGroup: rbac.authorization.k8s.io
  name: system:serviceaccounts:${NAMESPACE}
EOF
```

## What's Next
---

Now you are ready to move to the next labs [Lab2 Notebook](../lab2) about Data cleaning, EDA, feature engineering, model training, evaluations 