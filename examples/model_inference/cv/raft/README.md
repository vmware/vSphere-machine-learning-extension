# RAFT

[Recurrent All-Pairs Field Transforms for Optical Flow](https://arxiv.org/pdf/2003.12039.pdf)

It is a new deep network architecture for optical flow. RAFT extracts per-pixel features, builds multi-scale 4D correlation volumes for all pairs
of pixels, and iteratively updates a flow field through a recurrent unit that performs lookups on the correlation volumes. RAFT achieves state-
of-the-art performance. On KITTI, RAFT achieves an F1-all error of 5.10%, a 16% error reduction from the best published result (6.10%).
On Sintel (final pass), RAFT obtains an end-point-error of 2.855 pixels, a 30% error reduction from the best published result (4.098 pixels). In
addition, RAFT has strong cross-dataset generalization as well as high efficiency in inference time, training speed, and parameter count. Code
is available at https://github.com/princeton-vl/RAFT.

This tutorial shows you the demo of the model with a Jupyter notebook.

Steps to run the example:

1. Create a new notebook server on **Kubeflow on vSphere** dashboard with 2 CPUs, 4G RAM and 1 GPU using custom Docker image `projects.registry.vmware.com/models/notebook/inference:cv-pytorch-gpu-v3`.

2. `CONNECT` to the notebook server and launch a Terminal in the created notebook server.

3. Download the Jupyter notebooks in the Terminal via command: 

   ```shell
   wget https://raw.githubusercontent.com/vmware/vSphere-machine-learning-extension/master/examples/model_inference/cv/raft/RAFT.ipynb
   ```

4. Open the downloaded notebook and run the cells in the notebook to reproduce the results.
