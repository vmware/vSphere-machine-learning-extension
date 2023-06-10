=============
Model Serving
=============

Introduction
============

KServe is a standard Model Inference Platform on Kubernetes, built for highly scalable use cases. It provides performant, standardized inference protocol across machine learning (ML) frameworks and supports modern serverless inference workload with autoscaling including Scale to Zero on GPU.

You can use KServe to do the following:

- Provide a Kubernetes Custom Resource Definition for serving ML models on arbitrary frameworks.

- Encapsulate the complexity of autoscaling, networking, health checking, and server configuration to bring cutting edge serving features like GPU autoscaling, Scale to Zero, and canary rollouts to your ML deployments.

- Enable a simple, pluggable, and complete story for your production ML inference server by providing prediction, pre-processing, post-processing and explainability out of the box.

Please browse the `KServe GitHub repo <https://github.com/KServe/KServe>`__ for more details.


Get started
=========== 

In this section, you deploy an ``InferenceService`` with a predictor that loads a spam email detection model trained with custom dataset. We have prepared the files needed to deploy the model through KServe before experiment, including model file, configuration file. This preparation work is complicated and lengthy, so we do not elaborate here. If you want to know more details, for example, how to prepare the model files, please read the `KServe example tutorial <https://github.com/vmware/ml-ops-platform-for-vsphere/blob/main/website/content/en/docs/kubeflow-tutorial/lab4.ipynb>`__.


Prepare model and configuration files
-------------------------------------

First, you create a notebook refer to :ref:`user-guide-notebooks`. Then, download `model package <https://github.com/vmware/ml-ops-platform-for-vsphere/blob/main/website/content/en/docs/kubeflow-tutorial/lab4_files/v1.zip>`__ and unzip it in this notebook server:

.. code-block:: shell

    !wget https://github.com/vmware/ml-ops-platform-for-vsphere/blob/main/website/content/en/docs/kubeflow-tutorial/lab4_files/v1.zip
    
    !unzip v1.zip


Upload to MinIO
---------------

If you already have the MinIO storage, you can directly skip the MinIO deployment step, and follow the next steps to upload data to MinIO. If not, we also provide instructions on how to deploy standalone MinIO on the kubernetes clusters, you may refer to the `upload data to MinIO bucket` part in the :ref:`feature_store`. And the YAML files are the same with `MinIO deployment files <https://github.com/vmware/ml-ops-platform-for-vsphere/tree/main/website/content/en/docs/kubeflow-tutorial/lab4_minio_deploy>`__.

.. code-block:: shell
    
    # create pvc
    $ kubectl apply -f minio-standalone-pvc.yml

    # create service
    $ kubectl apply -f minio-standalone-service.yml

    # create deployment
    $ kubectl apply -f minio-standalone-deployment.yml

This step uploads ``v1/torchserve/model-store``, ``v1/torchserve/config`` to MinIO buckets. You need to find the MinIO ``endpoint_url``, ``accesskey``, ``secretkey`` before upload using the following commands in terminal:

.. code-block:: shell

    # get the endpoint url for MinIO
    $ kubectl get svc minio-service -n kubeflow -o jsonpath='{.spec.clusterIP}'
    
    # get the secret name for Minio. your-namespace is admin for this Kubernetes cluster.
    $ kubectl get secret -n <your-namespace> | grep minio

    # get the access key for MinIO
    $ kubectl get secret <minio-secret-name> -n <your-namespace> -o jsonpath='{.data.accesskey}' | base64 -d

    # get the secret key for MinIO
    $ kubectl get secret <minio-secret-name> -n <your-namespace> -o jsonpath='{.data.secretkey}' | base64 -d


You need to install ``boto3`` dependency package in the notebook server created earlier, and run the follow Python code to upload model files:

.. code-block:: shell

    !pip install boto3 -i https://pypi.tuna.tsinghua.edu.cn/simple


.. code-block:: shell

    import os
    from urllib.parse import urlparse
    import boto3

    os.environ["AWS_ENDPOINT_URL"] = "http://10.117.233.16:9000" # repalce it to your MinIO endpoint url
    os.environ["AWS_REGION"] = "us-east-1"
    os.environ["AWS_ACCESS_KEY_ID"] = "minioadmin"  # repalce it to your MinIO access key
    os.environ["AWS_SECRET_ACCESS_KEY"] = "minioadmin"   # repalce it to your MinIO secret key

    s3 = boto3.resource('s3',
                        endpoint_url=os.getenv("AWS_ENDPOINT_URL"),
                        verify=True)

    print("current buckets in s3:")
    print(list(s3.buckets.all()))

    curr_path = os.getcwd()
    base_path = os.path.join(curr_path, "torchserve")

    bucket_path = "spam_email"
    bucket = s3.Bucket(bucket_name)

    # upload
    bucket.upload_file(os.path.join(base_path, "model-store", "spam_email.mar"),
                    os.path.join(bucket_path, "model-store/spam_email.mar"))
    bucket.upload_file(os.path.join(base_path, "config", "config.properties"), 
                    os.path.join(bucket_path, "config/config.properties"))

    # check files 
    for obj in bucket.objects.filter(Prefix=bucket_path):
        print(obj.key)


Create MinIO service account and secret
---------------------------------------

When you create an ``InferenceService`` to start model, authorization is needed to access MinIO to get the model. Thus, you create MinIO service account and secret using the follow YAML file:

.. code-block:: shell

  cat << EOF | kubectl apply -f -
  apiVersion: v1
  kind: Secret
  metadata:
    name: minio-s3-secret-user # you can set a different secret name
    annotations:
      serving.kserve.io/s3-endpoint: "10.117.233.16:9000" # replace with your s3 endpoint e.g minio-service.kubeflow:9000
      serving.kserve.io/s3-usehttps: "0" # by default 1, if testing with minio you can set to 0
      serving.kserve.io/s3-region: "us-east-2"
      serving.kserve.io/s3-useanoncredential: "false" # omitting this is the same as false, if true will ignore provided credential and use anonymous credentials
  type: Opaque
  stringData: # use "stringData" for raw credential string or "data" for base64 encoded string
    AWS_ACCESS_KEY_ID: minioadmin  # repalce it to your MinIO access key
    AWS_SECRET_ACCESS_KEY: minioadmin # repalce it to your MinIO secret key
  ---
  apiVersion: v1
  kind: ServiceAccount
  metadata:
    name: minio-service-account-user # you can set a different sa name
  secrets:
  - name: minio-s3-secret-user
  EOF


Run ``InferenceService`` using KServe
------------------------------------------

Let's define a new ``InferenceService`` YAML for the model and apply it to the cluster. Meanwhile, please notice that set ``storageUri`` to your ``bucket_name/bucket_path``. You may also need to change ``metadata: name`` and ``serviceAccountName``.

.. code-block:: shell

  cat << EOF | kubectl apply -f -
  apiVersion: "serving.kserve.io/v1beta1"
  kind: "InferenceService"
  metadata:
    name: "spam-email-serving" # you can set a different secret name
  spec:
    predictor:
      serviceAccountName: minio-service-account-user # replace with your MinIO service account created before
      model:
        modelFormat:
          name: pytorch
        storageUri: "s3://spam-bucket/spam_email" # set yourself model s3 path
        resources:
            requests:
              cpu: 50m
              memory: 200Mi
            limits:
              cpu: 100m
              memory: 500Mi
            # limits:
            #   nvidia.com/gpu: "1"   # for inference service on GPU
  EOF


Check ``InferenceService`` status
---------------------------------

Run the following command in terminal to check the status of ``InferenceService``. ``True`` means your model server is running well.

.. code-block:: shell

    $ kubectl get inferenceservice spam-email-serving -n <your-namespace>
    NAME           URL                                                 READY   PREV   LATEST   PREVROLLEDOUTREVISION   LATESTREADYREVISION                    AGE
    spam-email-serving   http://spam-email-serving.kubeflow-user.example.com         True           100                              spam-email-serving-predictor-default-47q2g   23h


Test perform inference
----------------------

---------------------------------
Define a Test_bot for convenience
---------------------------------

Run the following cells to define a test_bot to make prediction in the notebook server. 

.. code-block:: shell

    !pip install multiprocess -i https://pypi.tuna.tsinghua.edu.cn/simple


.. code-block:: shell

    import requests
    import json
    import multiprocess as mp

    class Test_bot():
        def __init__(self, uri, model, host, session):
            self.uri = uri
            self.model = model
            self.host = host
            self.session = session
            self.headers = {'Host': self.host, 'Content-Type': "application/json", 'Cookie': "authservice_session=" + self.session}
            self.email = [
            # features: shorter_text, body, business, html, money
            "[0, 0, 0, 0, 0] email longer than 500 character" + "a" * 500,                                     # ham
            "[1, 0, 0, 0, 0] email shorter than 500 character",                                                # ham
            "[1, 0, 1, 1, 1] email shorter than 500 character + business + html + money",                      # spam
            "[0, 1, 0, 0, 1] email longer than 500 character + body" + "a" * 500,                              # spam
            "[0, 1, 1, 1, 1] email longer than 500 character + body + business + html + money" + "a" * 500,    # spam
            "[1, 1, 1, 1, 1] email shorter than 500 character body + business + html + money",                 # spam
            ]
        
        def update_uri(self, uri):
            self.uri = uri
            
        def update_model(self, model):
            self.model = model
            
        def update_host(self, host):
            self.host = host
            self.update_headers()
            
        def update_session(self, session):
            self.session = session
            self.update_headers()
            
        def update_headers(self):
            self.headers = {'Host': self.host, 'Content-Type': "application/json", 'Cookie': "authservice_session=" + self.session}
            
        def get_data(self, x):
            if isinstance(x, str):
                email = x
            elif isinstance(x, int):
                email = self.email[x % 6]
            else:
                email = self.email[0]
            json_data = json.dumps({
                "instances": [
                    email,
                ]
            })
            return json_data
            
        def readiness(self):
            uri = self.uri + '/v1/models/' + self.model
            response = requests.get(uri, headers = self.headers, timeout=5)
            return response.text

        def predict(self, x=None):
            uri = self.uri + '/v1/models/' + self.model + ':predict'
            response = requests.post(uri, data=self.get_data(x), headers = self.headers, timeout=10)
            return response.text
        
        def explain(self, x=None):
            uri = self.uri + '/v1/models/' + self.model + ':explain'
            response = requests.post(uri, data=self.get_data(x), headers = self.headers, timeout=10)
            return response.text
        
        def concurrent_predict(self, num=10):
            print("fire " + str(num) + " requests to " + self.host)
            with mp.Pool() as pool:
                responses = pool.map(self.predict, range(num))
            return responses


--------------------------
Determine host and session
--------------------------

Run the following command in terminal to get host, which is set to the headers in your request.

.. code-block:: shell

    $ kubectl get inferenceservice spam-email-serving -o jsonpath='{.status.url}' | cut -d "/" -f 3

Use your web browser to login to Freestone Kubeflow UI, and get Cookies: authservice_session. If you use Chrome browser, go to Developer Tools -> Applications -> Cookies to get session.

---------------------
Test model prediction
---------------------

Run the following cell to do model prediction in the notebook server.

.. code-block:: shell

                # replace it with the url you used to access Kubeflow
    bot = Test_bot(uri='http://10.117.233.8',
                model='spam_email',
                # replace it with what is printed above
                host='spam-email-serving.kubeflow-user-example-com.example.com',
                # replace with your browser session
                session='MTY2NjE2MDYyMHxOd3dBTkZZelVqVkdOVkJIVUVGR1IweEVTbG95VVRZMU5WaEVXbE5GTlV0WlVrWk1WRk5FTkU5WVIxZFJRelpLVFZoWVVFOVdSa0U9fMj0VhQPme_rORhhdy0mtBJk-yGWdzibFfPMdU3TztbJ')

    print(bot.readiness())
    print(bot.predict(0))


The output looks like:

.. code-block:: shell

    {"name": "spam_email", "ready": true}
    {"predictions": [{"version": "2", "prediction": "ham"}]}



Delete ``InferenceService``
---------------------------

When you are done with your ``InferenceService``, run the following command in terminal to delete it:

.. code-block:: shell

    $ kubectl delete inferenceservice <your-inferenceservice> -n  <your-namespace>
