# OpenNMT

OpenNMT is an open source ecosystem for neural machine translation and neural sequence learning. It is designed to be research friendly to try out new ideas in translation, language modeling, summarization, and many other NLP tasks. Some companies have proven the code to be production ready.

OpenNMT provides implementations in 2 popular deep learning frameworks:

- OpenNMT-py: User-friendly and multimodal, benefiting from PyTorch ease of use.
- OpenNMT-tf: Modular and stable, powered by the Tensorflow ecosystem.

Here we are using OpenNMT-py. 

This tutorial shows you the *training, inference and evaluation* of the model with 2 Jupyter notebooks:

- OpenNMT.ipynb: French -> English
- OpenNMT-zh.ipynb: Chinese -> English

Steps to run the example:

1. Create a new notebook server on **Kubeflow on vSphere** dashboard with 4 CPUs, 12G RAM and 1 GPU using custom Docker image `projects.registry.vmware.com/models/notebook/inference:nlp-pytorch-gpu-v3`. 

2. `CONNECT` to the notebook server and launch a Terminal in the created notebook server.

3. Download the Jupyter notebooks in the Terminal via command: 

   ```shell
   wget https://raw.githubusercontent.com/vmware/vSphere-machine-learning-extension/master/examples/model_training/nlp/opennmt/OpenNMT.ipynb
   wget https://raw.githubusercontent.com/vmware/vSphere-machine-learning-extension/master/examples/model_training/nlp/opennmt/OpenNMT-zh.ipynb
   ```

   These 2 notebooks are independent with each other. 

4. Open the downloaded notebooks and run the cells in the notebooks to reproduce the results. 
