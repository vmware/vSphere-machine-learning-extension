# Neural Machine Translation (NMT)

The Transformer, introduced in the paper Attention Is All You Need, is a powerful sequence-to-sequence modeling architecture capable of producing state-of-the-art NMT systems.

Recently, the fairseq team has explored large-scale semi-supervised training of Transformers using back-translated data, further improving translation quality over the original model. 

This tutorial shows you the *translation* capability of the model with a Jupyter notebook.

Steps to run the example:

1. Create a new notebook server on **Kubeflow on vSphere** dashboard with 4 CPUs, 12G RAM and 1 GPU using custom Docker image `projects.registry.vmware.com/models/notebook/inference:nlp-pytorch-gpu-v1`. 

2. `CONNECT` to the notebook server and launch a Terminal in the created notebook server.

3. Download the Jupyter notebook in the Terminal via command: 

   ```shell
   wget https://raw.githubusercontent.com/vmware/vSphere-machine-learning-extension/master/examples/model_inference/nlp/nmt/NMT.ipynb
   ```

4. Open the downloaded notebook and run the cells in the notebook to reproduce the results.
