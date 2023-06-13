# BLOOM Deployment on Freestone Kubeflow with Torchserve and Kserve

This tutorial guides you deploy the BLOOM model on the Freestone Kubeflow platform with torchserve.

[BLOOM](https://huggingface.co/docs/transformers/model_doc/bloom) is the bigScience large open-science multilingual language Model. The architecture of BLOOM is essentially similar to GPT3 (auto-regressive model for next token prediction), but has been trained on 46 different languages and 13 programming languages, based on the transformer architecture.

The BLOOM model comes in different sizes: 560m, 1B1, 1B7, 3B, 7B1, 176B parameters. The bigger the model size, the more GPU resources required for the deployment.

The BLOOM model size this turorial for torchserve uses is 560m. File size of the whole model MAR package is about 3GB. A 16G V100 GPU is required for this deployment.

## Setup

### Prerequisite

- The Freestone Kubeflow platform is ready for use.

### 1. Create a Notebook server

Create a new Notebook Server on the Freestone Kubeflow platform,
- Use a customized image that has Java and torchserve installed. You can use [Dockerfile](https://github.com/vmware/vSphere-machine-learning-extension/blob/main/examples/llm_bloom_deployment/Dockerfile) to generate your own custom image. You can also directly use an image published on VMware harbor repo:
    ```
    projects.registry.vmware.com/models/llm/pytorch/torchserve-notebook:latest-gpu-v0.15
    ```
- Set 8 CPUs, 16GB memory, 1 GPU, 50GB disk space for this Notebook Server.
Wait until the Notebook Server is created successfully.

### 2. Prepare MAR model package and it's config

Clone this repo in the notebook and entry ``examples/llm_bloom_deployment/`` directory:

```bash
cd ./examples/llm_bloom_deployment/
```

#### 2.1 Download model

```bash
python Download_model.py --model_name bigscience/bloom-560m
```
The script prints the path where the model is downloaded as below.

`model/models--bigscience-bloom-560m/snapshots/5546055f03398095e385d7dc625e636cc8910bf2/`

The downloaded model is around 3GB.

#### 2.2 Compress downloaded model

Install Zip cli tool

```bash
apt install zip
```

Navigate to the path got from the above script. In this example it is

```bash
cd model/models--bigscience-bloom-560m/snapshots/5546055f03398095e385d7dc625e636cc8910bf2/
zip -r ~/kubeflow-docs/examples/llm_bloom_deployment/model.zip *
cd ~/kubeflow-docs/examples/llm_bloom_deployment # return to the `llm_bloom_deployment` directory.
```

#### 2.3 Generate MAR file

Use the ``torch-model-archiver`` CLI to generate the model MAR file.

```bash
torch-model-archiver --model-name bloom --version 1.0 --handler custom_handler.py --extra-files model.zip,setup_config.json -r requirements.txt
```

The MAR model package is around 25GB.

**__Note__**: Modifying setup_config.json
- Enable `low_cpu_mem_usage` to use accelerate
- Recommended `max_memory` in `setup_config.json` is the max size of shard.
- Refer: https://huggingface.co/docs/transformers/main_classes/model#large-model-loading

**__Note__**: Notice that add ``-r requirements.txt`` field when generate MAR file, that mean install dependencies firstly when start model using ``torchserve --start`` later.

#### 2.4 Add the mar file to model store

```bash
mv bloom.mar torchserve/model_store
```

### 3. Start torchserve

Update ``torchserve/config/config.properties``, especially notice that chanage ``model_store`` field to your model directory. Then start torchserve.

Suggestion: run ``torchserve --start`` command in the jupyter terminal, and you can see the detail logs directly about running model using torchserve. You can't see the whole logs if you run ``torchserve --start`` command in the jupyter notebook

```bash
torchserve --start --ncs --ts-config torchserve/config/config.properties
```

### 4. Run inference

```bash
curl -v "http://localhost:8080/predictions/bloom" -T sample_text.txt
```

### Troubleshooting

Jupyter: XSRF cookie does not match POST

Solution: https://stackoverflow.com/questions/44088615/jupyter-xsrf-cookie-does-not-match-post

## Reference
- [Loading large Huggingface models with constrained resources using accelerate](https://github.com/pytorch/serve/tree/master/examples/large_models/Huggingface_accelerate)

- [TorchServe example with Huggingface BLOOM model](https://github.com/kserve/kserve/tree/master/docs/samples/v1beta1/torchserve/v1/bloom)
