# RoBERTa

A Robustly Optimized BERT Pretraining Approach

Bidirectional Encoder Representations from Transformers, or BERT, is a revolutionary self-supervised pretraining technique that learns to predict intentionally hidden (masked) sections of text. Crucially, the representations learned by BERT have been shown to generalize well to downstream tasks, and when BERT was first released in 2018 it achieved state-of-the-art results on many NLP benchmark datasets.

RoBERTa builds on BERT’s language masking strategy and modifies key hyperparameters in BERT, including removing BERT’s next-sentence pretraining objective, and training with much larger mini-batches and learning rates. RoBERTa was also trained on an order of magnitude more data than BERT, for a longer amount of time. This allows RoBERTa representations to generalize even better to downstream tasks compared to BERT.

This tutorial demonstrates the basic usage of RoBERTa, especially *classification tasks* with a Jupyter notebook.

Steps to run the example:

1. Create a new notebook server on **Kubeflow on vSphere** dashboard with 2 CPUs and 4G RAM using custom Docker image `projects.registry.vmware.com/models/notebook/inference:nlp-pytorch-cpu-v3`. GPU is not needed. 

2. `CONNECT` to the notebook server and launch a Terminal in the created notebook server.

3. Download the Jupyter notebook in the Terminal via command: 

   ```shell
   wget https://raw.githubusercontent.com/vmware/vSphere-machine-learning-extension/master/examples/model_inference/nlp/roberta/RoBERTa.ipynb
   ```

4. Open the downloaded notebook and run the cells in the notebook to reproduce the results.
