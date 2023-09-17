# ModelScope 

Text to Video Synthesis

The text-to-video generation diffusion model consists of three sub-networks: text feature extraction, text feature-to-video latent space diffusion model, and video latent space to video visual space. The overall model parameters are about 1.7 billion. Support English input. The diffusion model adopts the Unet3D structure, and realizes the function of video generation through the iterative denoising process from the pure Gaussian noise video.

This model has a wide range of applications and can reason and generate videos based on arbitrary English text descriptions.

This tutorial shows you *video generation* based on a short text description using the model with a Jupyter notebook.

Steps to run the example:

1. Create a new notebook server on **Kubeflow on vSphere** dashboard with 2 CPUs, 16G RAM and 1 GPU using custom Docker image `projects.registry.vmware.com/models/notebook/inference:cv-pytorch-gpu-v3`.

2. `CONNECT` to the notebook server and launch a Terminal in the created notebook server.

3. Download the Jupyter notebooks in the Terminal via command: 

   ```shell
   wget https://raw.githubusercontent.com/vmware/vSphere-machine-learning-extension/master/examples/model_inference/cv/modelscope/text_to_video_synthesis.ipynb
   ```

4. Open the downloaded notebook and run the cells in the notebook to reproduce the results.
