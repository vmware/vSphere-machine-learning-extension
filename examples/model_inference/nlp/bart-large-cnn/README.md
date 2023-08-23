# BART (large-sized model)

BART is a transformer encoder-decoder (seq2seq) model with a bidirectional (BERT-like) encoder and an autoregressive (GPT-like) decoder. BART is pre-trained by (1) corrupting text with an arbitrary noising function, and (2) learning a model to reconstruct the original text.

BART is particularly effective when fine-tuned for text generation (e.g. summarization, translation) but also works well for comprehension tasks (e.g. text classification, question answering). This particular checkpoint has been fine-tuned on CNN Daily Mail, a large collection of text-summary pairs.

This tutorial guides you to run the BART large-sized model with a Jupyter notebook to show its *text summarization* capability.

Steps to run the example:

1. Create a new notebook server on **Kubeflow on vSphere** dashboard with 2 CPUs and 4G RAM using custom Docker image `projects.registry.vmware.com/models/notebook/inference:nlp-pytorch-cpu-v3`. GPU is not needed. 

2. `CONNECT` to the notebook server and launch a Terminal in the created notebook server.

3. Download the Jupyter notebook in the Terminal via command: 

   ```shell
   wget https://raw.githubusercontent.com/vmware/vSphere-machine-learning-extension/master/examples/model_inference/nlp/bart-large-cnn/text-summarization.ipynb
   ```

4. Open the downloaded notebook and run the cells in the notebook step-by-step to reproduce the results.
