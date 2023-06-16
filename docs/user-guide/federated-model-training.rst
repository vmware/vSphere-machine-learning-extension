=========================
Federated model training
=========================

------------
Introduction
------------

Federated Learning is a machine learning technique where algorithms are trained across multiple distributed edge devices or servers, each having its own local data samples.

- `FATE`_ (Federated AI Technology Enabler) is the world's pioneering open-source framework for industrial-grade federated learning. It empowers businesses and institutions to collaborate on data while prioritizing the safety and privacy of the data involved. The FATE project leverages cutting-edge technologies such as Multi-Party Computation (MPC) and Homomorphic Encryption (HE) to build a robust and secure computing protocol, enabling a wide range of secure machine learning tasks, including logistic regression, tree-based algorithms, deep learning, and transfer learning, among others.

.. _FATE: https://github.com/FederatedAI/FATE

- `KubeFATE`_ is a solution that allows running FATE in containerized environments. It offers the capability to deploy FATE clusters with just one click, while also providing features to monitor the status of running FATE clusters, view logs, and perform version upgrades.

.. _KubeFATE: https://github.com/FederatedAI/KubeFATE

- FATE-Job is a task management tool specifically designed for FATE. It facilitates the submission and querying of FATE tasks through the use of the Kubernetes API.

FATE-Operator_ simplifies the deployment of FATE, KubeFATE and FATE-Job into Kubernetes clusters. It has been integrated into Kubeflow on vSphere, facilitating effortless utilization within the platform.

.. _FATE-Operator: https://github.com/kubeflow/fate-operator

This tutorial offers a comprehensive, step-by-step guide for demonstrating the usage of FATE-Operator on a Kubeflow on vSphere cluster:

- **Cluster Deployment: Setting up the FATE cluster.**
- **Federated Learning with FATE: Initial federated training on the deployed FATE cluster.**

--------------
Prerequisites
--------------

- Kubeflow on vSphere v1.6.1
- Deployed an additional FATE cluster with the ID 10000 or set both collaborative parties to 9999 (refer to the comments in the code example).

-------------------
Cluster Deployment
-------------------

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Deploy the FATE-Operator 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Get source code

.. code-block:: shell

  git clone https://github.com/kubeflow/fate-operator.git
  cd fate-operator

Deploy the FATE-Operator CRDs

.. code-block:: shell

  kustomize build config/crd | kubectl apply -f -


Deploy the FATE-Operator controller-manager 

.. code-block:: shell

  kustomize build config/default | kubectl apply -f -

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Deploy the FATE cluster 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

++++++++++++++++++++++++++++++
1. Install KubeFATE
++++++++++++++++++++++++++++++

Configuring RBAC (Role-Based Access Control) Permissions for KubeFATE.

.. code-block:: shell

  cat << EOF | kubectl apply -f -
  apiVersion: v1
  kind: Namespace
  metadata:
    name: kube-fate
    labels:
      name: kube-fate
  ---
  apiVersion: v1
  kind: ServiceAccount
  metadata:
    name: kubefate-admin
    namespace: kube-fate
  ---
  apiVersion: rbac.authorization.k8s.io/v1
  kind: RoleBinding
  metadata:
    name: kubefate
    namespace: fate-9999
  roleRef:
    apiGroup: rbac.authorization.k8s.io
    kind: ClusterRole
    name: cluster-admin
  subjects:
    - kind: ServiceAccount
      name: kubefate-admin
      namespace: kube-fate

  ---
  apiVersion: rbac.authorization.k8s.io/v1
  kind: RoleBinding
  metadata:
    name: kubefate
    namespace: fate-10000
  roleRef:
    apiGroup: rbac.authorization.k8s.io
    kind: ClusterRole
    name: cluster-admin
  subjects:
    - kind: ServiceAccount
      name: kubefate-admin
      namespace: kube-fate

  EOF

Set the key of KubeFATE

.. code-block:: shell

  cat << EOF | kubectl apply -f -
  apiVersion: v1
  kind: Secret
  metadata:
    name: kubefate-secret
    namespace: kube-fate
  type: Opaque
  stringData:
    kubefateUsername: admin
    kubefatePassword: admin
    mariadbUsername: kubefate
    mariadbPassword: kubefate

  EOF

Deploy kubefate, here is the v1.3.0 version of kubefate

.. code-block:: shell
  
  cat << EOF | kubectl apply -f -
  apiVersion: app.kubefate.net/v1beta1
  kind: Kubefate
  metadata:
    name: kubefate-sample
    namespace: kube-fate
  spec:
    # kubefate image tag
    image: federatedai/kubefate:v1.4.0
    # ingress host
    ingressDomain: kubefate.net
    # serviceAccountName
    serviceAccountName: kubefate-admin
    # kubefate config
    volumeSource:
      hostPath:
        path: /home/kubefate/mysql/db
        type: DirectoryOrCreate
    config:
      - name: MYSQL_USER
        valueFrom:
          secretKeyRef:
            name: kubefate-secret
            key: mariadbUsername
      - name: MYSQL_PASSWORD
        valueFrom:
          secretKeyRef:
            name: kubefate-secret
            key: mariadbPassword
      - name: FATECLOUD_DB_USERNAME
        valueFrom:
          secretKeyRef:
            name: kubefate-secret
            key: mariadbUsername
      - name: FATECLOUD_DB_PASSWORD
        valueFrom:
          secretKeyRef:
            name: kubefate-secret
            key: mariadbPassword
      - name: FATECLOUD_REPO_NAME
        value: "kubefate"
      - name: FATECLOUD_REPO_URL
        value: "https://federatedai.github.io/KubeFATE"
      - name: FATECLOUD_USER_USERNAME
        valueFrom:
          secretKeyRef:
            name: kubefate-secret
            key: kubefateUsername
      - name: FATECLOUD_USER_PASSWORD
        valueFrom:
          secretKeyRef:
            name: kubefate-secret
            key: kubefatePassword
      - name: FATECLOUD_LOG_LEVEL
        value: "debug"
      - name: FATECLOUD_LOG_NOCOLOR
        value: "true"
        
  EOF

Check kubefate status

.. code-block:: shell

  kubectl get Kubefate -n kube-fate
  NAME              INGRESSDOMAIN   STATUS
  kubefate-sample   kubefate.net    Running

++++++++++++++++++++++++++++++
2. Install FATE
++++++++++++++++++++++++++++++

To establish a FATE Cluster, we use FATE version 1.5.1. By removing comments in the YAML file, you can easily configure the parameters of the FATE Cluster, enabling seamless connections with other FATE Clusters. This interconnected network forms the foundation of federated learning, empowering collaborative learning across distributed nodes.

.. code-block:: shell
  
  cat << EOF | kubectl apply -f -
  apiVersion: app.kubefate.net/v1beta1
  kind: FateCluster
  metadata:
    name: fatecluster-sample
    namespace: fate-9999
  spec:
    kubefate:
      name: kubefate-sample
      namespace:  kube-fate
    clusterSpec:
      name: fate-9999
      namespace: fate-9999
      chartName: fate
      chartVersion: v1.5.1
      partyId: 9999
      registry: ""
      imageTag: ""
      pullPolicy: ""
      imagePullSecrets: 
        - name: myregistrykey  
      persistence: false
      istio:
        enabled: false
      modules:
        - rollsite
        - clustermanager
        - nodemanager
        - mysql
        - python
        - fateboard
        - client

      backend: eggroll

      host:
        fateboard: 9999.fateboard.kubefate.net
        client: 9999.notebook.kubefate.net
        # sparkUI: 9999.spark.kubefate.net
        # rabbitmqUI: 9999.rabbitmq.kubefate.net
      rollsite: 
        type: NodePort
        nodePort: 30091
        exchange:
          ip: 192.168.0.1
          port: 30000
        partyList:
        - partyId: 10000
          partyIp: 192.168.0.1
          partyPort: 30101
        nodeSelector: {}
      # lbrollsite:
        # type: NodePort
        # nodePort: 30091
        # size: "2M"
        # exchangeList:
        # - id: 9991
          # ip: 192.168.0.1
          # port: 30910
        # nodeSelector:

      nodemanager:
        count: 3
        sessionProcessorsPerNode: 4
        # storageClass: "nodemanagers"
        # accessMode: ReadWriteOnce
        # size: 2Gi
        list:
          - name: nodemanager
            nodeSelector: {}
            sessionProcessorsPerNode: 2
            subPath: "nodemanager"
            existingClaim: ""
            storageClass: "nodemanager"
            accessMode: ReadWriteOnce
            size: 1Gi

      python:
        type: NodePort
        httpNodePort: 30097
        grpcNodePort: 30092
        nodeSelector: {}
        enabledNN: false
        # spark: 
        #   master: spark://spark-master:7077
        #   home: 
        #   cores_per_node: 20
        #   nodes: 2
        # hdfs:
        #   name_node: hdfs://namenode:9000
        #   path_prefix:
        # rabbitmq:
        #   host: rabbitmq
        #   mng_port: 15672
        #   port: 5672
        #   user: fate
        #   password: fate
        #   # default conf/rabbitmq_route_table.yaml
        #   route_table: 
        # nginx:
        #   host: nginx
        #   http_port: 9300
        #   grpc_port: 9310

      mysql:
        nodeSelector: {}
        ip: mysql
        port: 3306
        database: eggroll_meta
        user: fate
        password: fate_dev
        subPath: ""
        existingClaim: ""
        storageClass: "mysql"
        accessMode: ReadWriteOnce
        size: 1Gi

      # externalMysqlIp: mysql
      # externalMysqlPort: 3306
      # externalMysqlDatabase: eggroll_meta
      # externalMysqlUser: fate
      # externalMysqlPassword: fate_dev

      servingIp: 192.168.9.1
      servingPort: 30209
      
      # spark:
        # master:
          # Image: "federatedai/spark-master"
          # ImageTag: "1.5.0-release"
          # replicas: 1
          # cpu: "100m"
          # memory: "512Mi"
          # nodeSelector: 
          # type: ClusterIP
        # worker:
          # Image: "federatedai/spark-worker"
          # ImageTag: "1.5.0-release"
          # replicas: 2
          # cpu: "1000m"
          # memory: "512Mi"
          # nodeSelector: 
          # type: ClusterIP
      # hdfs:
        # namenode:
          # nodeSelector: 
          # type: ClusterIP
        # datanode:
          # nodeSelector: 
          # type: ClusterIP
      # nginx:
        # nodeSelector: 
        # type: ClusterIP
        # httpNodePort: 30093
        # grpcNodePort: 30098
        # route_table: 
          # 10000: 
            # proxy: 
              # - host: 192.168.0.1 
                # http_port: 30103
                # grpc_port: 30108 
            # fateflow: 
              # - host: 192.168.0.1
                # http_port: 30107
                # grpc_port: 30102
      # rabbitmq:
        # nodeSelector: 
        # type: ClusterIP
        # nodePort: 30094
        # default_user: fate
        # default_pass: fate
        # user: fate
        # password: fate
        # route_table:
          # 10000:
            # host: 192.168.0.1
            # port: 30104
  EOF

Check FATE cluster status

.. code-block:: shell

  kubectl get fatecluster -n fate-9999
  NAME                 PARTYID   STATUS
  fatecluster-sample   9999      Running


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Federated Learning with FATE
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There are two options for running FATE training tasks: either by submitting them using the "fate-job" command or by using the "fateclient" with FATE pipeline. Both approaches provide convenient ways to execute and manage your FATE training tasks.

+++++++++++++
fate-job
+++++++++++++

To start a FATE training task, you can execute the following commands. The specifics of the task, such as the pipeline and modules configuration, can be customized within the "pipeline" and "modulesConf" sections of the "fate_v1alpha1_fatejob.yaml" file.

.. code-block:: shell

  kubectl apply -f https://raw.githubusercontent.com/kubeflow/fate-operator/master/config/samples/app_v1beta1_fatejob.yaml


+++++++++++++
fateclient
+++++++++++++

During the model experimentation phase, leveraging the fateclient offers a user-friendly approach to define and submit FATE tasks. This streamlined process provides convenience and ease-of-use when configuring and starting FATE jobs.

To obtain the Jupyter Notebook URL, you can use the following command which is already installed fateclient.

.. code-block:: shell

  kubectl get ingress -n fate-9999
  NAMESPACE   NAME        CLASS    HOSTS                         ADDRESS   PORTS   AGE
  fate-9999   fateboard   <none>   9999.fateboard.kubefate.net             80      13m
  fate-9999   notebook    <none>   9999.notebook.kubefate.net              80      13m


Initiate the pipeline to establish connectivity with fateflow.

.. code-block:: sh

  !pipeline init --ip fateflow --port 9380

Before proceeding, ensure that all participants have uploaded their respective data to FATE. Once this is done, follow the steps outlined in the notebook page:

The guest party should upload their data. You can use the provided sample file, "breast_homo_guest.csv," and replace it with your own dataset.

.. code-block:: python

  import os

  from pipeline.backend.pipeline import PipeLine
  from pipeline.utils.tools import load_job_config

  guest = 9999
  data_base = "/data/projects/fate/"

  # partition for data storage
  partition = 4

  # table name and namespace, used in FATE job configuration
  dense_data = {"name": "breast_homo_guest", "namespace": f"experiment"}

  pipeline_upload = PipeLine().set_initiator(role="guest", party_id=guest).set_roles(guest=guest)

  # add upload data info
  # path to csv file(s) to be uploaded
  pipeline_upload.add_upload_data(file=os.path.join(data_base, "examples/data/breast_homo_guest.csv"),
                                  table_name=dense_data["name"],             # table name
                                  namespace=dense_data["namespace"],         # namespace
                                  head=1, partition=partition,               # data info
                                  id_delimiter=",")

  # upload both data
  pipeline_upload.upload(drop=1)


The host party should upload their data. Use the provided example file, "breast_homo_host.csv," and replace it with your own dataset.

.. code-block:: python

  import os

  from pipeline.backend.pipeline import PipeLine
  from pipeline.utils.tools import load_job_config

  host = 10000 # Please change to 9999 if only one party is deployed
  data_base = "/data/projects/fate/"

  # partition for data storage
  partition = 4

  # table name and namespace, used in FATE job configuration
  dense_data = {"name": "breast_homo_host", "namespace": f"experiment"}

  pipeline_upload = PipeLine().set_initiator(role="host", party_id=host).set_roles(host=host)

  # add upload data info
  # path to csv file(s) to be uploaded
  pipeline_upload.add_upload_data(file=os.path.join(data_base, "examples/data/breast_homo_host.csv"),
                                  table_name=dense_data["name"],             # table name
                                  namespace=dense_data["namespace"],         # namespace
                                  head=1, partition=partition,               # data info
                                  id_delimiter=",")

  # upload both data
  pipeline_upload.upload(drop=1)



Use the FATE pipeline to create a federated training task specifically for homo-lr. This will enable you to perform federated learning using the homomorphic logistic regression (homo-lr) algorithm.

.. code-block:: python

  import argparse
  import json

  from pipeline.backend.pipeline import PipeLine
  from pipeline.component import DataTransform
  from pipeline.component import Evaluation
  from pipeline.component import HomoLR
  from pipeline.component import Reader
  from pipeline.component import FeatureScale
  from pipeline.interface import Data
  from pipeline.utils.tools import load_job_config

  # obtain config
  guest = 9999
  host = 10000 # Please change to 9999 if only one party is deployed
  arbiter = 9999 

  guest_train_data = {"name": "breast_homo_guest", "namespace": f"experiment"}
  host_train_data = {"name": "breast_homo_host", "namespace": f"experiment"}

  # initialize pipeline
  pipeline = PipeLine()
  # set job initiator
  pipeline.set_initiator(role='guest', party_id=guest)
  # set participants information
  pipeline.set_roles(guest=guest, host=host, arbiter=arbiter)

  # define Reader components to read in data
  reader_0 = Reader(name="reader_0")
  # configure Reader for guest
  reader_0.get_party_instance(role='guest', party_id=guest).component_param(table=guest_train_data)
  # configure Reader for host
  reader_0.get_party_instance(role='host', party_id=host).component_param(table=host_train_data)

  # define DataTransform components
  data_transform_0 = DataTransform(
      name="data_transform_0",
      with_label=True,
      output_format="dense")  # start component numbering at 0

  scale_0 = FeatureScale(name='scale_0')
  param = {
      "penalty": "L2",
      "optimizer": "sgd",
      "tol": 1e-05,
      "alpha": 0.01,
      "max_iter": 30,
      "early_stop": "diff",
      "batch_size": -1,
      "learning_rate": 0.15,
      "decay": 1,
      "decay_sqrt": True,
      "init_param": {
          "init_method": "zeros"
      },
      "cv_param": {
          "n_splits": 4,
          "shuffle": True,
          "random_seed": 33,
          "need_cv": False
      }
  }

  homo_lr_0 = HomoLR(name='homo_lr_0', **param)

  # add components to pipeline, in order of task execution
  pipeline.add_component(reader_0)
  pipeline.add_component(data_transform_0, data=Data(data=reader_0.output.data))
  # set data input sources of intersection components
  pipeline.add_component(scale_0, data=Data(data=data_transform_0.output.data))
  pipeline.add_component(homo_lr_0, data=Data(train_data=scale_0.output.data))
  evaluation_0 = Evaluation(name="evaluation_0", eval_type="binary")
  evaluation_0.get_party_instance(role='host', party_id=host).component_param(need_run=False)
  pipeline.add_component(evaluation_0, data=Data(data=homo_lr_0.output.data))

  # compile pipeline once finished adding modules, this step will form conf and dsl files for running job
  pipeline.compile()

  # fit model
  pipeline.fit()

  deploy_components = [data_transform_0, scale_0, homo_lr_0]
  pipeline.deploy_component(components=deploy_components)
  #
  predict_pipeline = PipeLine()
  # # add data reader onto predict pipeline
  predict_pipeline.add_component(reader_0)
  # # add selected components from train pipeline onto predict pipeline
  # # specify data source
  predict_pipeline.add_component(
      pipeline, data=Data(
          predict_input={
              pipeline.data_transform_0.input.data: reader_0.output.data}))
  predict_pipeline.compile()
  predict_pipeline.predict()

  dsl_json = predict_pipeline.get_predict_dsl()
  conf_json = predict_pipeline.get_predict_conf()
  # import json
  json.dump(dsl_json, open('./homo-lr-normal-predict-dsl.json', 'w'), indent=4)
  json.dump(conf_json, open('./homo-lr-normal-predict-conf.json', 'w'), indent=4)

  # query component summary
  print(json.dumps(pipeline.get_component("homo_lr_0").get_summary(), indent=4, ensure_ascii=False))
  print(json.dumps(pipeline.get_component("evaluation_0").get_summary(), indent=4, ensure_ascii=False))

Upon successful completion of the task, you will be able to examine the outcomes of the federated training process.  