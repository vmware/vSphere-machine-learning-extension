# spacytextblob

A TextBlob sentiment analysis pipeline component for [spaCy](https://spacy.io/).

This tutorial guides you to run the example with [this Jupyter notebook](https://github.com/vmware/vSphere-machine-learning-extension/blob/main/examples/model_serving/nlp/spacytextbolb/spacytextbolb.ipynb).

Steps to run the example:

1. Create a new notebook server on **Kubeflow on vSphere** dashboard with 0.5 CPU and 1G RAM using custom Docker image `projects.registry.vmware.com/models/notebook/inference:nlp-pytorch-cpu-v3`. GPU is not needed. 

2. `CONNECT` to the notebook server and launch a Terminal in the created notebook server.

3. Download the Jupyter notebook in the Terminal via command: 

   ```shell
   wget https://raw.githubusercontent.com/vmware/vSphere-machine-learning-extension/master/examples/model_serving/nlp/spacytextbolb/spacytextbolb.ipynb
   ```

4. Open the downloaded notebook file follow the steps in the notebook to reproduce the results.
