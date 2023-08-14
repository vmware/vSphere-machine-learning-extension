# BLOOM Fine-tuning

## Overview

[BLOOM](https://huggingface.co/docs/transformers/model_doc/bloom) is the bigScience large open-science multilingual language Model. The architecture of BLOOM is essentially similar to GPT3 (auto-regressive model for next token prediction), but has been trained on 46 different languages and 13 programming languages, based on the transformer architecture.

The BLOOM model comes in different sizes: 560m, 1B1, 1B7, 3B, 7B1, 176B parameters. The bigger the model size, the more GPU resources required for the deployment.

**If you want to fine tune higher parameters model, please make sure you have sufficient GPU resources.**

This tutorial guides you reimplement BLOOM-LoRA using Alpaca-LoRA and Alpaca_data_cleaned.json using LoRA method to fine tune bloom-560m model.

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

Connect to the Notebook Server. Open a Terminal window. Pull the code of this project by running `git clone https://github.com/linhduongtuan/BLOOM-LORA.git`

Then change directory to this BLOOM-LORA directory.

### Install dependencies

```bash
LD_LIBRARY_PATH=
pip install -r requirements.txt
pip install fire
```

### Update finetune.py file

Some arguments need to modify in the `finetune.py` file. Only modify these arguments, the training process will be running. Then update these arguments as below:

```bash
# 1. comment out or delete this line of code. Or got error: ValueError: Target modules ['q_proj', 'v_proj'] not found in the base model. Please check the target modules and try again.
# NameError: name 'TARGET_MODULES' is not defined

# comment out it.
# TARGET_MODULES = [
#     "q_proj",
#     "v_proj",
# ]

#target_modules=TARGET_MODULES, # comment out it.

# 2. Update the DATA PATH as below:
DATA_PATH = "./data/alpaca_data_cleaned.json"

# 3. Update the tokenizer as below:
# tokenizer = AutoTokenizer.from_pretrained('bigscience/bloom')
tokenizer = AutoTokenizer.from_pretrained(model_name)

# 4. Comment out or delete fp16=True. Or got error:  RuntimeError: expected scalar type Half but found Float
# fp16=True # comment out it.

# 5. Update the below line, because there is no ddp parameter.
# ddp_find_unused_parameters=False if ddp else None,
ddp_find_unused_parameters=False,

# 6. Uodate the below line, because there is no checkpoint to resume.
# trainer.train(resume_from_checkpoint = True)
trainer.train() 
```

### Start fine-tune model

Fine-tune bigscience/bloom-560m model by running `python finetune.py`. You can see the result in the BLOOM-alpaca directory once fine-tuned process finished.

### Merge LoRa adapters back to base model

Using LoRA method to fine tune bloom-560m model, the fine-tuned result actually is the model LoRa adapters. Thus, need to merge LoRa adapters back the base model to get the whole fine-tuned model by running the below command.

```bash
python merge_peft_adapters.py --base_model_name_or_path <put your base model name> --peft_model_path ./BLOOM-alpaca
```

### Model inference using the fine-tuned model

Please refer to [llm_bloom_deployment](https://github.com/vmware/vSphere-machine-learning-extension/tree/main/examples/llm_bloom_deployment) to do model inference with the fine-tuned model.
