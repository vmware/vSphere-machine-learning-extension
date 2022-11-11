#!/bin/bash

#############################################
# OIDC-authservice -> External Dex -> GitHub
#############################################

dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $dir

# create CA
mkdir -p ssl
openssl genrsa -out ssl/ca-key.pem 2048
openssl req -x509 -new -nodes -key ssl/ca-key.pem -days 10 -out ssl/ca.pem -subj "/CN=kube-ca"

# create external dex
kubectl create namespace dex --dry-run=client -o yaml | kubectl apply -f -

cat << EOF > ssl/req.cnf
[req]
req_extensions = v3_req
distinguished_name = req_distinguished_name

[req_distinguished_name]

[ v3_req ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment
subjectAltName = @alt_names

[alt_names]
DNS.1 = dex.dex.svc.cluster.local
EOF

openssl genrsa -out ssl/key.pem 2048
openssl req -new -key ssl/key.pem -out ssl/csr.pem -subj "/CN=kube-ca" -config ssl/req.cnf
openssl x509 -req -in ssl/csr.pem -CA ssl/ca.pem -CAkey ssl/ca-key.pem -CAcreateserial -out ssl/cert.pem -days 10 -extensions v3_req -extfile ssl/req.cnf

[[ $(kubectl get secret dex.dex.svc.cluster.local.tls -n dex 2>/dev/null) ]] && kubectl delete secret dex.dex.svc.cluster.local.tls -n dex
kubectl create secret tls dex.dex.svc.cluster.local.tls -n dex \
  --cert=ssl/cert.pem \
  --key=ssl/key.pem

kubectl apply -f dex_https.yaml
kubectl rollout restart deployment dex -n dex

# create Kubeflow
cat << 'EOF' | ytt --file ../../bundle/config --file - > kubeflow_manifest_preview.yaml
#@data/values
---

imageswap_labels: True

service_type: "LoadBalancer"

IP_address: "10.117.233.30"

CD_REGISTRATION_FLOW: True

OIDC_Authservice:
  OIDC_AUTH_URL: https://dex.dex.svc.cluster.local/auth
  OIDC_PROVIDER: https://dex.dex.svc.cluster.local
  OIDC_SCOPES: "profile email groups"
  REDIRECT_URL: http://istio-ingressgateway.istio-system.svc.cluster.local/login/oidc
  SKIP_AUTH_URI: "/dex"
  USERID_CLAIM: email
  USERID_HEADER: kubeflow-userid
  USERID_PREFIX: ""
  OIDC_CLIENT_ID: kubeflow-oidc-authservice
  OIDC_CLIENT_SECRET: kubeflow-oidc-authservice-secret
  
Dex:
  use_external: True
EOF

kubectl apply -f kubeflow_manifest_preview.yaml 


# add ca certificate to pods's trust root 
[[ $(kubectl get configmap ca-pemstore -n istio-system 2>/dev/null) ]] && kubectl delete configmap ca-pemstore -n istio-system
kubectl create configmap ca-pemstore -n istio-system \
  --from-file=ssl/ca.pem

cat > authservice_patch.yaml << EOF
spec:
  template:
    spec:
      containers:
      - name: authservice
        volumeMounts:
        - name: ca-pemstore
          mountPath: /etc/ssl/certs/ca.pem
          subPath: ca.pem
          readOnly: false
      volumes:
      - name: ca-pemstore
        configMap:
          name: ca-pemstore
EOF
kubectl patch StatefulSet authservice -n istio-system --patch-file=authservice_patch.yaml
# kubectl rollout restart StatefulSet authservice -n istio-system
kubectl delete pod authservice-0 -n istio-system


# on local client
# sudo vim /etc/hosts
# dex.dex.svc.cluster.local
# istio-ingressgateway.istio-system.svc.cluster.local