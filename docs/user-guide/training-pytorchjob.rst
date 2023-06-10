=========================================
PyTorch Distributed Training (PyTorchJob)
=========================================

Introduction
============

``PyTorchJob`` is a training operator in Freestone Kubeflow. It allows you to run distributed PyTorch jobs on Kubernetes clusters. It provides a PyTorch-specific implementation of the Kubernetes Operator pattern, which automates the management of PyTorch training jobs.

With ``PyTorchJob``, you define and manage PyTorch jobs as Kubernetes custom resources. The operator will then manage the creation, scaling, and deletion of the resources needed to run the job. This includes creating pods for PyTorch workers, launching PyTorch distributed training, and managing checkpoints.

``PyTorchJob`` supports a range of PyTorch configurations, including single-node and multi-node distributed training, automatic and manual scaling, and more. Additionally, it supports a range of storage backends for storing training data, including local storage, NFS, and cloud storage solutions like Amazon S3 or Google Cloud Storage.

Overall, ``PyTorchJob`` simplifies the process of running distributed PyTorch jobs in Kubernetes, making it easier to manage training workloads at scale.


Get started
===========

In this section, you create a training job by defining a ``PyTorchJob`` configuration file to train a model. Before that, you need a working Freestone Kubeflow deployment with PyTorch Operator up and running. Also, you need to create a volume to save logs and model file for the training.


Verify PyTorchJob running
-------------------------

Check that the PyTorch custom resource is installed:

.. code-block:: shell

    $ kubectl get crd
    NAME                                             CREATED AT
    ...
    pytorchjobs.kubeflow.org                         2023-01-31T06:02:59Z
    ...

Check that the Training operator is running via:

.. code-block:: shell

    $ kubectl get pods -n kubeflow
    NAME                                READY   STATUS    RESTARTS   AGE
    ...
    training-operator-0                 2/2     Running   4 (6d1h ago)    6d2h
    ...


Create a new volume
-------------------

In ``user``'s namespace, create a new volume named ``data``, with ``ReadWriteOnce`` access mode. The training job saves logs and model file in the volume.

.. code-block:: shell

  export USER_NAMESPACE=user # replace it with your namespace
  kubectl config set-context --current --namespace=$USER_NAMESPACE

  export storageClassName=k8s-storage-policy # replace it with your environment storageclass

  cat << EOF | kubectl apply -f -
  apiVersion: v1
  kind: PersistentVolumeClaim
  metadata:
    name: data
    labels:
      app: data
  spec:
    storageClassName: ${storageClassName}
    accessModes:
    - ReadWriteOnce
    resources:
      requests:
        storage: 10Gi
  EOF



Create a PyTorch training job
-----------------------------

You can create a training job by defining a ``PyTorchJob`` configuration file. See the manifests for the distributed NLP example. You may change the configuration file based on your requirements.

You just choose one of the below YAML files to apply according to your environment. If you just have *CPU* environment, follow the YAML file to deploy the ``PyTorchJob`` resource with *CPU* to start training. If you have *GPU* environment, you follow the other YAML file to deploy the ``PyTorchJob`` resource with *GPU* to start training. 

.. code-block:: shell

  # Deploy the PyTorchJob resource with CPU
  cat <<EOF | kubectl create -n $USER_NAMESPACE -f -
  apiVersion: "kubeflow.org/v1"
  kind: "PyTorchJob"
  metadata:
    name: "pytorchjob-distributed-training"
  spec:
    pytorchReplicaSpecs:
      Master:
        replicas: 1
        restartPolicy: OnFailure
        template:
          metadata:
            annotations:
              sidecar.istio.io/inject: "false"
          spec:
            volumes:
              - name: data
                persistentVolumeClaim:
                  claimName: data
            containers:
              - volumeMounts:
                  - name: data
                    mountPath: "/opt/pytorch/output"
                name: pytorch
                image: projects.registry.vmware.com/models/kubeflow-docs/model-training-pytorch:1.11.0-cpu-py3.8-v0.1
                imagePullPolicy: IfNotPresent
      Worker:
        replicas: 2
        restartPolicy: OnFailure
        template:
          metadata:
            annotations:
              sidecar.istio.io/inject: "false"
          spec:
            containers: 
              - name: pytorch
                image: projects.registry.vmware.com/models/kubeflow-docs/model-training-pytorch:1.11.0-cpu-py3.8-v0.1
                imagePullPolicy: IfNotPresent
    EOF


.. code-block:: shell

  # Deploy the PyTorchJob resource with GPU
  cat <<EOF | kubectl create -n $USER_NAMESPACE -f -
  apiVersion: "kubeflow.org/v1"
  kind: "PyTorchJob"
  metadata:
    name: "pytorchjob-distributed-training-gpu"
  spec:
    pytorchReplicaSpecs:
      Master:
        replicas: 1
        restartPolicy: OnFailure
        template:
          metadata:
            annotations:
              sidecar.istio.io/inject: "false"
          spec:
            volumes:
              - name: data
                persistentVolumeClaim:
                  claimName: data
            containers:
              - volumeMounts:
                - name: data
                  mountPath: "/opt/pytorch/output"
                name: pytorch
                image: projects.registry.vmware.com/models/kubeflow-docs/model-training-pytorch:1.11.0-gpu-cu11.6-py3.8-v0.1
                args: ["--backend", "nccl"]
                imagePullPolicy: IfNotPresent
                resources: 
                  limits:
                    nvidia.com/gpu: 1
      Worker:
        replicas: 1
        restartPolicy: OnFailure
        template:
          metadata:
            annotations:
              sidecar.istio.io/inject: "false"
          spec:
            containers: 
              - name: pytorch
                image: projects.registry.vmware.com/models/kubeflow-docs/model-training-pytorch:1.11.0-gpu-cu11.6-py3.8-v0.1
                args: ["--backend", "nccl"]
                imagePullPolicy: IfNotPresent
                resources: 
                  limits:
                    nvidia.com/gpu: 1
  EOF

To verify the number of the created pods matches the specified number of replicas:

.. code-block:: shell

    kubectl get pods -l job-name=pytorchjob-distributed-training -n $USER_NAMESPACE



Monitoring a PyTorchJob
-----------------------

Training takes 5-10 minutes to complete. Monitor the job status to become success and inspect logs to see the training progress:

.. code-block:: shell

    kubectl get pods -n $USER_NAMESPACE | grep pytorchjob-distributed-training
    kubectl logs -f pytorchjob-distributed-training-master-0 -n $USER_NAMESPACE
    kubectl logs -f pytorchjob-distributed-training-worker-0 -n $USER_NAMESPACE
    kubectl logs -f pytorchjob-distributed-training-worker-1 -n $USER_NAMESPACE


Test whether PyTorchJob is distributed training
-----------------------------------------------

Firstly, deploy the single pod to start training:

.. code-block:: shell

  cat <<EOF | kubectl create -n $USER_NAMESPACE -f -
  apiVersion: v1
  kind: Pod
  metadata:
    annotations:
      sidecar.istio.io/inject: "false"
    name: "pytorch-training-single-pod"
  spec:
    volumes:
      - name: data
        persistentVolumeClaim:
          claimName: data
    containers:
      - name: pytorch
        image: harbor-repo.vmware.com/kubeflow_learning/lab3-pytorch-training:dlc-0.0.1
        imagePullPolicy: IfNotPresent
        volumeMounts:
          - name: data
            mountPath: "/opt/pytorch/output"
  EOF

Waiting 10-15 minutes for the training process to complete and check logs.

Secondly, compare the training logs between the single pod and the ``PyTorchJob``.

.. image:: ../_static/user-guide-training-pytorchjob-result.png

As shown in the picture, the model is trained 48 times for 6 epochs in the single-pod. And after using PyTorch operator, the model is trained 16 times individually in the master and 2 workers, although the loss value after each training is different, the accuracy obtained is the same after the master communicates with the 2 workers.

.. seealso::

   `Use PytorchJob to train a model for predict Spam email <https://vmware.github.io/ml-ops-platform-for-vsphere/docs/kubeflow-tutorial/lab3/>`_
