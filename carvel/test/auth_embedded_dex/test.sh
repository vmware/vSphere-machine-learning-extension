#!/bin/bash

#############################################
# OIDC-authservice -> Embedded Dex -> Okta
#############################################

dir=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $dir

cat << 'EOF' | ytt --file ../../bundle/config --file - > kubeflow_manifest_preview.yaml
#@data/values
---

imageswap_labels: True

service_type: "LoadBalancer"

IP_address: "10.117.233.30"

CD_REGISTRATION_FLOW: True

OIDC_Authservice:
  OIDC_AUTH_URL: /dex/auth
  OIDC_PROVIDER: http://istio-ingressgateway.istio-system.svc.cluster.local/dex
  OIDC_SCOPES: "profile email groups"
  REDIRECT_URL: /login/oidc
  SKIP_AUTH_URI: "/dex"
  USERID_CLAIM: email
  USERID_HEADER: kubeflow-userid
  USERID_PREFIX: ""
  OIDC_CLIENT_ID: kubeflow-oidc-authservice
  OIDC_CLIENT_SECRET: pUBnBOY80SnXgjibTYM9ZWNzY2xreNGQok

Dex:
  use_external: False
  config: |-
    issuer: http://istio-ingressgateway.istio-system.svc.cluster.local/dex
    storage:
      type: kubernetes
      config:
        inCluster: true
    web:
      http: 0.0.0.0:5556
    logger:
      level: debug
      format: text
    oauth2:
      skipApprovalScreen: true
    enablePasswordDB: true
    staticPasswords:
    - email: user@embedded.com
      # password: 12341234
      hash: $2y$12$B1gPMr/RgOUzyjhv8trvf.XgF6Uz/yefTOtqBlg3ZGRGZus.dfpbK
      username: user
      userID: b58996c504c5638798eb6b511e6f49af
    - email: admin@embedded.com
      # password: 88888888
      hash: $2y$12$4K/VkmDd1q1Orb3xAt82zu8gk7Ad6ReFR4LCP9UeYE90NLiN9Df72
      username: admin
      userID: 31626e0748cb566de91145de41c22100
    staticClients:
    - idEnv: OIDC_CLIENT_ID
      redirectURIs: ["/login/oidc"]
      name: Dex Login Application
      secretEnv: OIDC_CLIENT_SECRET
    connectors:
    - type: oidc
      id: okta
      name: Okta
      config:
        issuer: https://trial-7937584.okta.com
        clientID: 0oa2qxti4tNuljEHu697
        clientSecret: 7ERAlNa2RZsmGACE_tkUEhKzpZ2ir-65gjjU-wxI
        redirectURI: http://istio-ingressgateway.istio-system.svc.cluster.local/dex/callback
        insecureSkipEmailVerified: true
EOF

kubectl apply -f kubeflow_manifest_preview.yaml 
kubectl rollout restart deployment dex -n auth
kubectl rollout restart StatefulSet authservice -n istio-system
# kubectl delete pod authservice-0 -n istio-system


# on local client
# sudo vim /etc/hosts
# dex.dex.svc.cluster.local
# istio-ingressgateway.istio-system.svc.cluster.local