# spacytextblob

A TextBlob sentiment analysis pipeline component for [spaCy](https://spacy.io/).

This tutorial demonstrates how to use spacytextblob on a simple string with a Jupyter notebook.

Steps to run the examples:

1. Create a new notebook server on **Kubeflow on vSphere** dashboard with 0.5 CPU and 1G RAM using custom Docker image `projects.registry.vmware.com/models/notebook/inference:nlp-pytorch-cpu-v3`. GPU is not needed. 

2. `CONNECT` to the notebook server and launch a Terminal in the created notebook server.

3. Download the Jupyter notebook in the Terminal via command: 

   ```shell
   wget https://raw.githubusercontent.com/vmware/vSphere-machine-learning-extension/master/examples/model_serving/nlp/spacytextblob/spacytextblob.ipynb
   ```

4. Open the downloaded notebook and run the cells in the notebook to reproduce the results.
