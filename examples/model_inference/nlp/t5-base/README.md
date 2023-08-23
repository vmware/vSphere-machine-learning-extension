# Text-To-Text Transfer Transformer



"With Text-To-Text Transfer Transformer (T5), we propose reframing all NLP tasks into a unified text-to-text-format where the input and output are always text strings, in contrast to BERT-style models that can only output either a class label or a span of the input. Our text-to-text framework allows us to use the same model, loss function, and hyperparameters on any NLP task."

**T5-Base** is the checkpoint with 220 million parameters. 

This tutorial guides you to run the T5-Base model with a Jupyter notebook.

Steps to run the example:

1. Create a new notebook server on **Kubeflow on vSphere** dashboard with 1 CPU and 4G RAM using custom Docker image `projects.registry.vmware.com/models/notebook/inference:nlp-pytorch-cpu-v3`. All the required Python modules are included in this image. GPU is not needed. 

2. `CONNECT` to the notebook server and launch a Terminal in the created notebook server.

3. Download the Jupyter notebook in the Terminal via command: 

   ```shell
   wget https://raw.githubusercontent.com/vmware/vSphere-machine-learning-extension/master/examples/model_inference/nlp/t5-base/t5-base.ipynb
   ```

4. Open the downloaded notebook and run the cells in the notebook to reproduce the results.

**Note:** You might need to try multiple times for downloading from Hugging Face in cell [2] and [5].
