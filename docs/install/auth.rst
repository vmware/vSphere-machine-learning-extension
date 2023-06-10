==========================
Authentication Integration
==========================

------------
Introduction
------------

The goal of Freestone Kubeflow's integration with LDAP Server is that you can login to Freestone Kubeflow using your LDAP account. As shown in the following screenshots, choose **Log in with OpenLDAP**, input your account name and password, then you can login to Freestone Kubeflow successfully. When you login, it will create your own user profile automatically.

.. image:: ../_static/operation-guide-auth-ldap-goal01.png
.. image:: ../_static/operation-guide-auth-ldap-goal02.jpeg
.. image:: ../_static/operation-guide-auth-ldap-goal03.png

-------------------------
Enable *Log in with LDAP*
-------------------------

""""""""""""""""""""""
Update Dex's ConfigMap
""""""""""""""""""""""

Dex uses a ConfigMap for its configuration.

You need to edit `Dex's ConfigMap  <https://github.com/kubeflow/manifests/blob/master/common/dex/base/config-map.yaml>`__ to change the ``issuer`` to ``<public_ip>/dex`` and add LDAP connector.

.. code-block:: shell

    kubectl edit configmap dex -n auth

.. code-block:: shell

  issuer: http://dex.auth.svc.cluster.local:5556/dex

  # --     some configurations we don't care    -- #
  # --     some configurations we don't care    -- #

  staticPasswords:

  # --     staticClstaticPasswordsients configuration we don't care   -- #
  # --     staticClstaticPasswordsients configuration we don't care   -- #

  staticClients:

  # --     staticClients configuration we don't care   -- #
  # --     staticClients configuration we don't care   -- #

  connectors:
  - type: ldap
    name: OpenLDAP
    id: ldap
    config:
      # Host and optional port of the VMware LDAP server in the form "host:port".
      # More detailes here: https://dexidp.io/docs/connectors/ldap/
      host: ldap.example.com:636
      insecureNoSSL: false
      insecureSkipVerify: true
      bindDN: ""
      bindPW: ""
      usernamePrompt: SSO Username
      userSearch:
        baseDN: ou=people,dc=example,dc=com
        filter: "(objectclass=inetOrgPerson)"
        username: uid
        idAttr: DN
        emailAttr: mail
        nameAttr: cn  


For the LDAP connector, you need to finish the `LDAP connector configurations <https://dexidp.io/docs/connectors/ldap/>`__.


"""""""""""""""""""""""""""""""""""""""""""
Update ConfigMap and restart dex deployment
"""""""""""""""""""""""""""""""""""""""""""

.. code-block:: shell

    # run the following two lines to update dex config with the user you add
    kubectl get configmap dex -n auth -o yaml | kubectl replace -f -
    # restart dex deployment to make the new configuration work
    kubectl rollout restart deployment dex -n auth

---------------------------------
Enable automatic profile creation
---------------------------------

""""""""""""""""""""""""""""""""""""
Update Central Dashboard's ConfigMap
""""""""""""""""""""""""""""""""""""

The automatic profile creation can be enabled as part of the deployment by setting the ``CD_REGISTRATION_FLOW`` environment variable to ``true``. Modify the ``<manifests-path>/apps/centraldashboard/upstream/base/params.env`` to set the registration variable to ``true``.

You need to edit  `Central Dashboard's ConfigMap <https://github.com/kubeflow/manifests/blob/master/apps/centraldashboard/upstream/base/params.env>`_ changing ``CD_REGISTRATION_FLOW`` to ``true``.

.. code-block:: shell

    kubectl edit configmap centraldashboard-parameters -n kubeflow

    # Set CD_REGISTRATION_FLOW to true
    # CD_REGISTRATION_FLOW: false
    CD_REGISTRATION_FLOW: "true"

""""""""""""""""""""""""""""""""""""""""""""""""""
Update Central Dashboard deployment and restart it
""""""""""""""""""""""""""""""""""""""""""""""""""

.. code-block:: shell

  kubectl edit deploy centraldashboard -n kubeflow

  # --     some configurations we don't care    -- #
  spec:
    containers:
    - env:
      ...
      ...
      # Change the value of REGISTRATION_FLOW from false to true
      - name: REGISTRATION_FLOW
        value: "true"

.. code-block:: shell

    # restart centraldashboard deployment
    kubectl get deploy centraldashboard -n kubeflow -o yaml | kubectl replace -f -


When an authenticated user logs into the system and visits the Central Dashboard for the first time, it triggers profile creation automatically.
A brief message introduces profiles, and the user can name her profile and click **Finish**. This redirects the user to the Dashboard where she views and selects her profile in the drop down list.

.. image:: ../_static/operation-guide-auth-ldap-login-namespace01.png
.. image:: ../_static/operation-guide-auth-ldap-login-namespace02.png

---------------------------------------------------
Configure pod security policy for your user profile
---------------------------------------------------

Before starting to use Freestone Kubeflow, remember to configure the pod security policy for your user profile in order to create pods. This is important as pod creation is needed for many Freestone Kubeflow functions, such as Notebook Server creation. 
Refer to :ref:`configure pod security policy` for more details and instructions.

---------------
Troubleshooting
---------------

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Restrict specific LDAP accounts to login to Freestone Kubeflow
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

Most of the time, you hope to specify some LDAP accounts can login to Freestone Kubeflow, but not all LDAP accounts. Thus you need to add more filter restrictions when searching the directory. 
As in the following example, you only allow ``user1`` and ``user2`` these 2 users to login to Freestone Kubeflow. 

.. code-block:: shell

  kubectl edit configmap dex -n auth

  ...
      userSearch:
        baseDN: ou=people,dc=vmware,dc=com
        filter: "(objectclass=inetOrgPerson)(|(uid=user1)(uid=user2))"
        ...

""""""""""""""""""""
Pod creation failure
""""""""""""""""""""

You may meet the following error in some operation:

.. code-block:: text

    FailedCreate 1s (x2 over 1s) statefulset-controller create Pod test-01-0 in StatefulSet test-01 failed error: pods “test-01-0” is forbidden: PodSecurityPolicy: unable to admit pod: []

This error occurs because you did not configure your pod security policy correctly. To solve this problem, you need to configure pod security policy based on :ref:`configure pod security policy`.
