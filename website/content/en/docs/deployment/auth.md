+++
title = "Setup Authentication"
description = "Setup Authentication for Kubeflow on vSphere"
weight = 60
+++

## Introduction
---

In this tutorial, we will learn how to configure **Kubeflow on vSphere** for multi-user collaboration with the **same identity provider used by TKG clusters**.

![](../assets/kubeflow_auth.png)

With the release of vSphere 8.0 and its **Pinniped authentication service** on TKG, you can now configure Supervisor with **any OIDC-compliant identity provider** such as [Okta](https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-with-tanzu-tkg/GUID-766CC14B-BE5D-427E-8EA5-1570F28C95DE.html#GUID-766CC14B-BE5D-427E-8EA5-1570F28C95DE__section_ovd_qn5_x5b), [Workspace One](https://pinniped.dev/docs/howto/configure-supervisor-with-workspace_one_access/), [Dex](https://pinniped.dev/docs/howto/configure-supervisor-with-dex/), [GitLab](https://pinniped.dev/docs/howto/configure-supervisor-with-gitlab/), [Google OAuth](https://developers.google.com/identity/protocols/oauth2/openid-connect), etc. following the document: [Configure an External IDP for Use with TKG 2 on Supervisor](https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-with-tanzu-tkg/GUID-766CC14B-BE5D-427E-8EA5-1570F28C95DE.html)

Kubeflow use [OIDC-AuthService](https://github.com/arrikto/oidc-authservice) to provide authentication service. By connecting OIDC-AuthService to the same identity provider used by Pinniped service, you will be able to access Kubeflow and TKG cluster with the same user account.

Depending on your goal, you may choose one of the following three options:

1. Configure OIDC-AuthService with the external Dex.  
> `Option 1 is preferred if Pinniped service on TKG cluster has been configured with Dex as IdP. `
2. Configure OIDC-AuthService with Embedded Dex, and further use upstream OIDC as IdP.
> `Option 2 is preferred if Pinniped service on TKG cluster has been configured with OIDC services as IdP. `
3. Configure OIDC-AuthService with Embedded Dex, and further use static passwords, LDAP / AD or OIDC.
> `Option 3 is preferred if you would like to use a standalone authentication system for Kubeflow`

## Option 1: Use external Dex
---

#### Prerequisites and procedures

- [**Prerequisites**] A Tanzu Kubernetes Cluster with Kubeflow on vSphere deployed. If you haven't, please follow the tutorial [here](http://localhost:1313/ml-ops-platform-for-vsphere/main/docs/deployment/carvel/).
- [**Prerequisites**] Pinniped service on TKG being configured with an external Dex. You can follow the documents [here](https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-with-tanzu-tkg/GUID-766CC14B-BE5D-427E-8EA5-1570F28C95DE.html) for instructions.
- Add a staticClients to external Dex for Kubeflow OIDC-Authservice.
- Connect Kubeflow OIDC_Authservice with external Dex.

#### Add staticClient to external Dex

Dex use a configmap for its configuration. You can get original Dex configuration file by
```bash
# Dex is installed in the namespace dex by default
$ kubectl get configmap dex -n dex

kind: ConfigMap
apiVersion: v1
metadata:
  name: dex
  namespace: dex
data:
  config.yaml: |
    issuer: https://dex.dex.svc.cluster.local

    # --     some configurations we don't care    -- #
    # --     some configurations we don't care    -- #

    staticClients:
    # --        staticClients configuration begin        -- #
    # It defines the downstream clients that use Dex as IdP #
    # --        staticClients configuration end          -- #

    # Assume Dex is also configured with Pinniped Supervisor,
    # so there should be one static client existing.
    - id: pinniped-supervisor
      redirectURIs: ["https://10.105.150.34/wcp/pinniped/callback "]
      name: 'Pinniped Supervisor client'
      secret: pinniped-supervisor-secret

    connectors:
    # --      connectors configuration begin        -- #
    #        It defines the upstream IdP of Dex        #
    # --      connectors configuration end          -- #
```

Edit the configmap to add a staticClient for our Kubeflow OIDC-AuthService. For the new static client, you will need to defines:
- **id**: you define any id here, which will be used later
- **secret**: you define any secret here, it will be used later
- **redirectURIs**: the IP address or domain name of the Kubeflow istio-ingressgateway + "/login/oidc", it will be used later
- **name**: does not matter

You also need to note down:
- **issuer**: note down this value, we will need it later.

If you don't know how to get the IP address of the Kubeflow istio-ingressgateway, please consult [docs here](../../kubeflow-tutorial/lab1/)

```bash
# Dex is installed in the namespace dex by default
$ kubectl edit configmap dex -n dex

kind: ConfigMap
apiVersion: v1
metadata:
  name: dex
  namespace: dex
data:
  config.yaml: |
    # issuer: note down this value, we will need it later.
    issuer: https://dex.dex.svc.cluster.local

    # --     some configurations we don't care    -- #
    # --     some configurations we don't care    -- #

    staticClients:
    # --        staticClients configuration begin        -- #
    # It defines the downstream clients that use Dex as IdP #
    # --        staticClients configuration end          -- #

    # Assume Dex is also configured with Pinniped Supervisor,
    # so there should be one static client existing.
    - id: pinniped-supervisor
      secret: pinniped-supervisor-secret
      redirectURIs: ["https://10.105.150.34/wcp/pinniped/callback "]
      name: 'Pinniped Supervisor client'

    # Add one more static client for Kubeflow OIDC authservice
      # id: you define any id here, which will be used later
    - id: kubeflow-oidc-authservice
      # secret: you define any secret here, it will be used later
      secret: kubeflow-oidc-authservice-secret
      # redirectURIs: the IP address or domain name of the Kubeflow istio-ingressgateway + "/login/oidc", it will be used later
      redirectURIs: ["http://istio-ingressgateway.istio-system.svc.cluster.local/login/oidc"]
      # name: does not matter
      name: 'kubeflow-oidc-authservice'

    connectors:
    # --      connectors configuration begin        -- #
    #        It defines the upstream IdP of Dex        #
    # --      connectors configuration end          -- #
```

#### Connect Kubeflow OIDC_Authservice with external Dex.

In the previous section, four values **id**, **secret**, **redirectURIs**, **issuer** are said to be used later.

Now update values.yaml according to the four values.

You will need to set:
- OIDC_Authservice.**OIDC_AUTH_URL**: `issuer` + '/auth'
- OIDC_Authservice.**OIDC_PROVIDER**: `issuer`
- OIDC_Authservice.**REDIRECT_URL**: `redirectURIs`
- OIDC_Authservice.**OIDC_CLIENT_ID**: `id`
- OIDC_Authservice.**OIDC_CLIENT_SECRET**: `secret`

Because we do not need the embedded Dex anymore, we will also set
- Dex.**use_external**: True

You can keep other values unchanged.

```bash
#-    Other values   -#
# keep them unchanged #
#-    Other values   -#

OIDC_Authservice:
  # OIDC_Authservice.OIDC_AUTH_URL: `issuer` + '/auth'
  OIDC_AUTH_URL: https://dex.dex.svc.cluster.local/auth
  # OIDC_Authservice.OIDC_PROVIDER: `issuer`
  OIDC_PROVIDER: https://dex.dex.svc.cluster.local
  OIDC_SCOPES: "profile email groups"
  # REDIRECT_URL: `redirectURIs`
  REDIRECT_URL: http://istio-ingressgateway.istio-system.svc.cluster.local/login/oidc
  SKIP_AUTH_URI: "/dex"
  USERID_CLAIM: email
  USERID_HEADER: kubeflow-userid
  USERID_PREFIX: ""
  # OIDC_CLIENT_ID: `id`
  OIDC_CLIENT_ID: kubeflow-oidc-authservice
  # OIDC_CLIENT_SECRET: `secret`
  OIDC_CLIENT_SECRET: kubeflow-oidc-authservice-secret
  
Dex:
  use_external: True
```

Update to an updated values file
```bash
kctrl package installed update --package-install kubeflow --values-file values.yaml
```

Restart the OIDC-AuthService by
```bash
kubectl delete pod authservice-0 -n istio-system
```

## Option 2: Use Embedded Dex with upstream OIDC
---

#### Prerequisites and procedures

- [**Prerequisites**] A Tanzu Kubernetes Cluster with Kubeflow on vSphere deployed. If you haven't, please follow the tutorial [here](http://localhost:1313/ml-ops-platform-for-vsphere/main/docs/deployment/carvel/).
- [**Prerequisites**] Pinniped service on TKG being configured with an upstream OIDC. You can follow the documents [here](https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-with-tanzu-tkg/GUID-766CC14B-BE5D-427E-8EA5-1570F28C95DE.html) for instructions.
- Add a new OIDC client to the upstream OIDC provier.
- Connect Kubeflow embedded Dex with the upstream OIDC.

#### Add a new OIDC client to the upstream OIDC provier.

We will use the same **Okta** example aligning with VMware official documents.

Please follow https://docs.vmware.com/en/VMware-vSphere/8.0/vsphere-with-tanzu-tkg/GUID-766CC14B-BE5D-427E-8EA5-1570F28C95DE.html to create a new App Integration, with the following settings:

- **redirect URIs**: the IP address or domain name of the Kubeflow istio-ingressgateway + "/login/oidc", it will be used later

You also need to note down those values, which will be used later.
- **Issuer URL**: e.g. https://trial-7937584.okta.com
- **Client ID**: e.g. 0oa2qxti4tNuljEHu697
- **Client Secret**: e.g. 7ERAlNa2RZsmGACE_tkUEhKzpZ2ir-65gjjU-wxI

If you don't know how to get the IP address of the Kubeflow istio-ingressgateway, please consult [docs here](../../kubeflow-tutorial/lab1/)

#### Connect Kubeflow embedded Dex with the upstream OIDC.

In the previous section, four values **redirect URIs**, **Issuer URL**, **Client ID**, **Client Secret** are said to be used later.

Now set Dex.**config** in values.yaml according to the four values.

You can keep other values unchanged.

```bash
#-    Other values   -#
# keep them unchanged #
#-    Other values   -#

Dex:
  use_external: False
  config: |-
    #-    Other values   -#
    # keep them unchanged #
    #-    Other values   -#
    # add a new connector
    connectors:
    - type: oidc
      id: okta
      name: Okta
      config:
        # Issuer URL
        issuer: https://trial-7937584.okta.com
        # Client ID
        clientID: 0oa2qxti4tNuljEHu697
        # Client Secret
        clientSecret: 7ERAlNa2RZsmGACE_tkUEhKzpZ2ir-65gjjU-wxI
        # redirect URIs
        redirectURI: http://istio-ingressgateway.istio-system.svc.cluster.local/dex/callback
        # for Dex with Okta to work, you will also need to set insecureSkipEmailVerified to be true
        insecureSkipEmailVerified: true
```

Update to an updated values file
```bash
kctrl package installed update --package-install kubeflow --values-file values.yaml
```

Restart the Dex by
```bash
kubectl rollout restart deployment dex -n auth
```

## Option 3: Use Embedded Dex with upstream OIDC, static passwords, LDAP / AD
---

You can also configure embedded Dex with all kinds of identity providers following Dex official docs: https://dexidp.io/docs/connectors/

We will introduce the simplest one: static passwords, which is very convenient for testing purpose.

#### Static User Creation

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
    #-    Other values   -#
    # keep them unchanged #
    #-    Other values   -#

    Dex:
      use_external: False
      config: |-
        #-    Other values   -#
        # keep them unchanged #
        #-    Other values   -#
        EnablePasswordDB: true
        static_users: 
        - email: "user@example.com"
          hash: $(python3 password_hash.py --password 12341234)
          username: user
          userID: $(cat /proc/sys/kernel/random/uuid)
        - email: "admin@vsphere.local"
          hash: $(python3 password_hash.py --password 88888888)
          username: admin
          userID: $(cat /proc/sys/kernel/random/uuid)
        #-    Other values   -#
        # keep them unchanged #
        #-    Other values   -#
    ```

3. Update to an updated values file
   ```bash
    kctrl package installed update --package-install kubeflow --values-file values.yaml
    ```

4. Restart dex
    ```bash
    kubectl rollout restart deployment dex -n auth
    ```

Then you will be able to login with
- user@example.com / 12341234
- admin@vsphere.local / 88888888