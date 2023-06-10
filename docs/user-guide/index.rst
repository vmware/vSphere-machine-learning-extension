========
Overview
========

In this section, we go through the end-to-end machine learning operations (MLOps) workflow using Freestone Kubeflow’s features. The overall MLOps workflow could be split into two major phases: Training and Inference. During the Training phase, you build a champion model that can solve the problem you need to address and achieve the performance to your satisfaction. In the Inference phase, you use this model to provide services.


Model Training
--------------

Data Processing
^^^^^^^^^^^^^^^

Data Exploration
""""""""""""""""

Let’s start with the data exploration where you can learn more about the data to understand the possible solution to the problem you need to address. *Jupyter Notebook* is equipped in the Freestone Kubeflow core components. In Jupyter Notebook you can share data, code, and make experiments.

Data Preparation
""""""""""""""""

In order for machine learning (ML) algorithms to be effective, the traditional ETL (Extract, Transfer, Load) method can be applied to raw data to assure the quality of the data is suitable for the models. Freestone Kubeflow integrates some tools to support this:

- Apache *Spark*: Spark is the most popular tool to handle big data. It can handle a variety of data formats and sizes and is designed to scope with your data exploration environment.

- TensorFlow Transform (*TFT*): TFT helps to process the raw data efficiently in the context of the entire dataset.

Feature Engineering
"""""""""""""""""""

Feature engineering is the process to transform the raw data into features that the ML model can use. Often time, it is the most time-consuming part of the data processing and results in high amount of development and repeated features across projects. Freestone Kubeflow offers the Feature Store (Feast) to 
overcome the time inefficiency and effort duplication.

Model Development
^^^^^^^^^^^^^^^^^

After the data processing tasks are done and a good set of data and features is identified, you are ready to build and train the model. Freestone Kubeflow offers rich features to cover this process.

Model Training
""""""""""""""

Once you construct a model from the algorithm, you can employ the Freestone Kubeflow *Training Operators* to perform the model training. The list of the Training Operators offered by Freestone Kubeflow is growing from coming releases. Here are the highlights:

- TFJob (TensorFlow)

- PyTorchJob (PyTorch)

- MXJob (Apache MXNet)

- XGBoostJob (XGBoost)

- MPIJob (MPI)

- PaddleJob (PaddlePaddle)


By employing these operators, you can effectively manage the model training process, monitor progress, and make experiments to find the best algorithm. With Freestone Kubeflow’s operators, you have the flexibility to tackle complex ML tasks while minimizing infrastructure complexities.

Model Tuning
""""""""""""

Hyperparameters are the variables that control the model training process. The examples for hyperparameters are: 

- The learning rate in a neural network

- The numbers of layers and nodes in a neural network

- Regularization

- Type of loss function

Hyperparameter tuning is the process of optimizing the hyperparameter values to maximize the model metrics 
such as accuracy in validation phase.

Freestone Kubeflow offers *Katib* to automate the hyperparameter tuning process by automatically tuning the target variable which you specify in the configuration. Katib offers exploration algorithms such as Random search, Grid search and Bayesian optimization to perform the hyperparameter evaluation and tries to achieve the optimal set of hyperparameters for the given model.

Model Validation
""""""""""""""""

You can use Freestone Kubeflow’s *Experiments* and *Runs* to compare the metrics of a given model across multiple models. For example, these may be the same model trained on different datasets, or two models with different hyperparameters trained on the same dataset. By using the Freestone Kubeflow’s *Pipeline*, you can automate these processes to report whether a model runs smoothly or encounters some problems.


Data Storage
^^^^^^^^^^^^

Shared Storage
""""""""""""""

To host data used in the common data access during the creation of the model such as using pipeline and saving results of the experiments, some sort of external and distributed storage can be the solution. Different cloud providers have different storage offerings, for example Amazon S3, Azure Data Storage, Google Cloud Storage. Due to the complexity to deal with different storage offerings, Freestone Kubeflow ships with *MinIO* to reduce the dependency on the storage offerings from different cloud providers by acting as a common gateway to public cloud storage APIs. This gateway option is the most flexible one, and allows you to create cloud independent implementation without scale limits.

Model Registry
""""""""""""""

This is a storage unit that holds model specific data (classes) or weights. Its purpose is to hold trained models for fast retrieval by other applications. Without the model registry, the model classes and weights would be saved to the source code repository and are hard to retrieve.

Metadata Database
"""""""""""""""""

Metadata of a model is to hold the collection of the datasets and the transformation of these datasets during the data exploration. Capturing the metadata lets you understand the variations during the model experiments phase. This understanding helps you iteratively develop and efficiently improve the models. vSphere Enterprise Kuebflow employs ML Metadata (*MLMD*) library to faciliate this enhancement.


Model Inference (Model Serving)
-------------------------------

Once the model is selected from the validation where the metrics are met, you can deploy the model to the 
production environment. This trained and then deployed model acts as a service that can handle prediction 
requests. 

Freestone Kubeflow simplifies the model deployment by dealing with the given model‘s different formats using *Seldon Core*, *TFServe* and *KFServe*. The model-as-data methodology is used by these implementations to leverage an intermediate model format and Freestone Kubeflow allows the swapping between model frameworks as smoothly as possible. With Freestone Kubeflow, you can train the model using PyTorch or TensorFlow. When the model is serving for production, the underlying serving remains consistent with the user's APIs. Furthermore the hardware serving the model can be optimized for better performance than the hardware used during the model training phase.

Freestone Kubeflow also handles the infrastructure complexities such as modeling monitoring, scaling, revisioning during the model serving. The hosted models could be updated with newer versions to fit the current dataset better and therefore increases the performance metrics. They can be rolled back to previous versions if certain problems are encountered after deployment. These kinds of model management can be handled smoothly and automatically with Freestone Kubeflow without much of human involvements.
