# LLaMA Deployment on Freestone Kubeflow with Torchserve

This tutorial guides you deploy the LLaMA model on the Freestone Kubeflow platform with torchserve.

[LLaMA](https://ai.facebook.com/blog/large-language-model-llama-meta-ai/) is a large language model Meta AI released for research purpose. LLaMA is an auto-regressive language model, based on the transformer architecture.

The LLaMA model comes in different sizes: 7B, 13B, 33B, 65B parameters. The bigger the model size, the more GPU resources required for the deployment.

The LLaMA model size this turorial uses is 7B. File size of the whole model is about 14GB. A 16G V100 GPU is required for this deployment.

## Setup

### Prerequisite

- The Freestone Kubeflow platform is ready for use.
- The LLaMA 7B model has been downloaded and ready for use.

### Step 1: Create a new Notebook Server
Create a new Notebook Server on the Freestone Kubeflow platform, 
- Use a customized image that has Java and torchserve installed. You can create your own custom image or use an image published by us here:
    ```
    projects.registry.vmware.com/models/llm/pytorch/torchserve-notebook:latest-gpu-v0.15
    ```
- set 8 CPUs, 12GB memory, 1 GPU, 40GB disk space for this Notebook Server. 
Wait until the Notebook Server is created successfully.

### Step 2: Connect to the Notebook Server
Connect to the Notebook Server. Open a Terminal window. Pull the code of this project by running
    ```
    git clone https://github.com/elements-of-ai/kubeflow-docs.git
    ```

Then change directory to this llm_llama_deployment project in the kubeflow-docs\examples directory.

### Step 3: Download the LLaMA model files
Download the LLaMA model files following the instructions in ```download_models.sh```

### Step 4: Generate the model package
Generate the model package required by torchserve. Run ```gen_pkgs.sh```
This step might take 10-20 minutes.

### Step 5: Install dependency
Install the necessary dependency packages. Run
    ```
    pip install -r requirements.txt
    ```

## Start the inference service

Run ```start_ts.sh``` to start the inference service with torchserve.
It might take more than 10 minutes for the service to be ready. Open another terminal window, check the output of ```nvidia-smi```. If all the model files have been loaded into GPU memory (more than 14GB), the service should be ready.

Run ```test.py``` to test the inference service. Modify test.py to try different prompts for your test.

