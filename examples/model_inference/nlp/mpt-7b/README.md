# MPT-7B

MPT-7B is a decoder-style transformer pretrained from scratch on 1T tokens of English text and code. This model was trained by [MosaicML](https://www.mosaicml.com/).

MPT-7B is part of the family of MosaicPretrainedTransformer (MPT) models, which use a modified transformer architecture optimized for efficient training and inference.

These architectural changes include performance-optimized layer implementations and the elimination of context length limits by replacing positional embeddings with Attention with Linear Biases (ALiBi). Thanks to these modifications, MPT models can be trained with high throughput efficiency and stable convergence. MPT models can also be served efficiently with both standard HuggingFace pipelines and NVIDIA's [FasterTransformer](https://github.com/NVIDIA/FasterTransformer).

This model uses the MosaicML LLM codebase, which can be found in the llm-foundry repository. It was trained by MosaicML’s NLP team on the MosaicML platform for LLM pretraining, finetuning, and inference.

This tutorial shows you the *text generation* capability of the model with a Jupyter notebook.

Steps to run the example:

1. Create a new notebook server on **Kubeflow on vSphere** dashboard with 2 CPUs, 20G RAM and 1 GPU using custom Docker image `projects.registry.vmware.com/models/notebook/inference:nlp-pytorch-gpu-v4`. 

2. `CONNECT` to the notebook server and launch a Terminal in the created notebook server.

3. Download the Jupyter notebooks in the Terminal via command: 

   ```shell
   wget https://raw.githubusercontent.com/vmware/vSphere-machine-learning-extension/master/examples/model_inference/nlp/mpt-7b/MPT-7B.ipynb
   ```

4. Open the downloaded notebook and run the cells in the notebook to reproduce the results. 
