# AlexNet

AlexNet competed in the ImageNet Large Scale Visual Recognition Challenge on September 30, 2012. The network achieved a top-5 error of 15.3%, more than 10.8 percentage points lower than that of the runner up. The original paper’s primary result was that the depth of the model was essential for its high performance, which was computationally expensive, but made feasible due to the utilization of graphics processing units (GPUs) during training.

[AlexNet: The Architecture that Challenged CNNs](https://towardsdatascience.com/alexnet-the-architecture-that-challenged-cnns-e406d5297951)

This tutorial guides you to run the AlexNet model with a Jupyter notebook to show its basic capabilities.

Steps to run the example:

1. Create a new notebook server on **Kubeflow on vSphere** dashboard with 2 CPUs and 4G RAM using custom Docker image `projects.registry.vmware.com/models/notebook/inference:cv-pytorch-cpu-v3`. GPU is not needed. 

2. `CONNECT` to the notebook server and launch a Terminal in the created notebook server.

3. Download the Jupyter notebook in the Terminal via command: 

   ```shell
   wget https://github.com/vmware/vSphere-machine-learning-extension/blob/main/examples/model_inference/cv/alexnet/alexnet.ipynb
   ```

4. Open the downloaded notebook and run the cells in the notebook step-by-step to reproduce the results.
