# BLOOM Fine-tuning

## Overview

[BLOOM](https://huggingface.co/docs/transformers/model_doc/bloom) is the bigScience large open-science multilingual language Model. The architecture of BLOOM is essentially similar to GPT3 (auto-regressive model for next token prediction), but has been trained on 46 different languages and 13 programming languages, based on the transformer architecture.

The BLOOM model comes in different sizes: 560m, 1B1, 1B7, 3B, 7B1, 176B parameters. The bigger the model size, the more GPU resources required for the deployment.

**If you want to fine tune higher parameters model, please make sure you have sufficient GPU resources.**

This tutorial guides you to fine tune the bloom-560m model with the Alpaca dataset on the Kubeflow on vSphere platform.

## Setup

### Prerequisite

- The Kubeflow on vSphere platform is ready for use.

### Create a Notebook server

Create a new Notebook Server on the Kubeflow on vSphere platform,

- Select kubeflow docker image as below:
    ```bash
    kubeflownotebookswg/jupyter-pytorch-cuda-full:v1.6.0 
    ```
- Set 4 CPUs, 8 GB memory, 1 GPU, 20GB disk space for this Notebook Server.

### Connect to the Notebook Server

Connect to the Notebook Server. Open a Terminal window. Pull the code of a github project by running `git clone https://github.com/linhduongtuan/BLOOM-LORA.git`

Then change directory to the BLOOM-LORA directory.

### Install dependencies

```bash
pip install -r requirements.txt
```

### Update finetune.py file

Before starting the fine tune process, some arguments in file `finetune.py` must be modified. Check the details below.

```bash
# 1. comment out or delete these lines of code.

# TARGET_MODULES = [
#     "q_proj",
#     "v_proj",
# ]

#target_modules=TARGET_MODULES,

# 2. Update the DATA PATH as below:
DATA_PATH = "./data/alpaca_data_cleaned.json"

# 3. Update the tokenizer as below:
# tokenizer = AutoTokenizer.from_pretrained('bigscience/bloom')
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 4. Comment out this line of code
# fp16=True

# 5. Update this line of code, because there is no ddp parameter.
# ddp_find_unused_parameters=False if ddp else None,
ddp_find_unused_parameters=False,

# 6. Update this line of code, because we have no checkpoint to resume.
# trainer.train(resume_from_checkpoint = True)
trainer.train(resume_from_checkpoint = False) 
```

### Start fine-tune model

Fine-tune bigscience/bloom-560m model by running `python finetune.py`. The fine tuning process might take more than 5 hours on a V100 GPU. You can see the result in the BLOOM-alpaca directory once fine-tuned process finished.

### Merge LoRa adapters back to base model

Using LoRA method to fine tune bloom-560m model, the fine-tuned result actually is the model LoRa adapters. Thus, need to merge LoRa adapters back to the base model to get the whole fine-tuned model. You can do this by running this command.

```bash
python ../merge_peft_adapters.py [ --base_model_name_or_path <your base model name> ] --peft_model_path ./BLOOM-alpaca
```
If you don't provide a path to your downloaded base model, this script by default downloads the bloom-560m model and use it as the base model. After the merging complete, the new model is saved in bigscience/bloom-560m-merged/

### Model inference using the fine-tuned model

Please refer to [llm_bloom_deployment](https://github.com/vmware/vSphere-machine-learning-extension/tree/main/examples/model_deployment/llm/bloom_deployment) to do model inference with the fine-tuned model.
