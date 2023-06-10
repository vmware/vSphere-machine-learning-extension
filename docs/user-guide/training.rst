==============
Model Training
==============

Training Operator is a key component in Freestone Kubeflow, which provides a simple and flexible way to run distributed machine learning (ML) training jobs on Kubernetes. It abstracts away the complexity of managing distributed training, allowing users to focus on writing and running their training code. The Training Operator provides a high-level API to define training jobs, automatically scales resources on demand, manages data and job lifecycle, and allows users to monitor and debug training jobs through a web-based UI. It supports a variety of popular ML frameworks, such as TensorFlow, PyTorch, and MXNet, as well as custom containers for user-specific environments. By leveraging the power of Kubernetes and the simplicity of the Training Operator, users can easily run and manage large-scale training workloads with high efficiency and flexibility.

For more detailed information about training operator, please refer to `Training Operators <https://www.kubeflow.org/docs/components/training/>`_. To know how it works, please refer to its `source code <https://github.com/kubeflow/training-operator>`_. 

In this section, we provide 2 examples of training operator for PyTorch and TensorFlow to learn using PyTorchJob to train a model with PyTorch and using TFJob to train a model with TensorFlow.

.. toctree::
        :titlesonly:
        
        training-pytorchjob
        training-tfjob
