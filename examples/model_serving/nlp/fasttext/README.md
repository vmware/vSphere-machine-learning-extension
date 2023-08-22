# fastText

FastText is an open-source, free, lightweight library that allows users to learn text representations and text classifiers. It works on standard, generic hardware. Models can later be reduced in size to even fit on mobile devices.

This tutorial guides you to run *text classification* examples of fastText with a Jupyter notebook.

Steps to run the examples:

1. Create a new notebook server on **Kubeflow on vSphere** dashboard with 2 CPUs and 4G RAM using custom Docker image `projects.registry.vmware.com/models/notebook/inference:nlp-pytorch-cpu-v1`. GPU is not needed. 

2. `CONNECT` to the notebook server and launch a Terminal in the created notebook server.

3. Download the Jupyter notebook in the Terminal via command: 

   ```shell
   wget https://raw.githubusercontent.com/vmware/vSphere-machine-learning-extension/master/examples/model_serving/nlp/fasttext/fastText.ipynb
   ```

4. Open the downloaded notebook and run the cells in the notebook step-by-step to reproduce the results.
