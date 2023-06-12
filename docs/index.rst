.. Kubeflow documentation master file, created by
   sphinx-quickstart on Fri Jan 13 06:56:36 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: ./_static/kubeflow-logo.png
   :align: center
   :scale: 20%

Welcome
=======

Data scientists and engineers often face the challenge to manually execute all the steps in a machine learning (ML) workflow, including moving and transforming data, training models, and promoting them to production. This is where Kubeflow comes in. Kubeflow is a free and open source ML platform that streamlines the entire ML process, from data preparation and modeling to deployment. It uses pipelines to orchestrate complicated ML workflows and is dedicated to simplifying the deployments by providing a straightforward approach.

Kubeflow is a powerful ML operations (MLOps) platform that can be used for experimentation, development, and production. Based on Kubeflow, we’ve developed vSphere Machine Learning Extension, which is a VMware-sponsored initiative aimed at meeting the strict business and technical requirements for enterprise infrastructure. To address the challenges faced by enterprises, we've made several enhancements, including:

- Optimized GPU utilization with GPU sharing management, enabling enterprises to optimize the ML workflows for better performance.
- A rich offering of popular training models, covering a wide range of use cases.
- Streamlined packaging and deployment user experience, making the deployment of vSphere Machine Learning Extension easier and swifter.

Additionally, vSphere Machine Learning Extension incorporates several Kubeflow add-ons and community software to create an enterprise-ready MLOps platform on vSphere. With vSphere Machine Learning Extension, enterprises can enjoy the benefits of an efficient and streamlined ML workflow, allowing them to achieve faster and more accurate results.

This documentation presents a comprehensive end-to-end workflow of using vSphere Machine Learning Extension to build, train, and deploy ML models. It guides you through the entire process, from data preparation to model serving, and explain how various components of vSphere Machine Learning Extension work together to streamline and enhance your ML workflow. Furthermore, we provide our best practices for deploying vSphere Machine Learning Extension components locally, on-prem, and in the cloud. By the end of this documentation, you have a better understanding of how to use vSphere Machine Learning Extension to manage your ML projects and you are able to apply the additionally provided features to your projects.


.. toctree::
    :caption: Introduction
    :hidden:

    introduction/index
    introduction/oss
    introduction/ekf
    introduction/mlops

.. toctree::
    :caption: Install and Configure
    :hidden:

    install/index
    install/tkgs
    install/auth
    install/monitor

.. toctree::
    :caption: User Guide
    :hidden:

    user-guide/index
    user-guide/notebooks
    user-guide/feast
    user-guide/spark
    user-guide/mlmd
    user-guide/mlflow
    user-guide/training
    user-guide/tensorboard
    user-guide/katib
    user-guide/kserve
    user-guide/kfp

.. toctree::
    :caption: Use Cases
    :hidden:

    use-cases/index
    use-cases/helmet
    use-cases/modelserving
    use-cases/codegen

.. toctree::
    :caption: Internals
    :hidden:

    internals/auth

License
-------

Kubeflow is released under the Apache License 2.0.

vSphere Machine Learning Extension and its documents are offered as free, open-source software. You don’t need a support agreement or license to deploy them.

.. Indices and tables
   ==================

   * :ref:`genindex`
   * :ref:`modindex`
   * :ref:`search`
