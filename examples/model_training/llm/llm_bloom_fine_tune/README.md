# BLOOM fine-tuning

## Overview

[BLOOM](https://huggingface.co/docs/transformers/model_doc/bloom) is the bigScience large open-science multilingual language Model. The architecture of BLOOM is essentially similar to GPT3 (auto-regressive model for next token prediction), but has been trained on 46 different languages and 13 programming languages, based on the transformer architecture.

The BLOOM model comes in different sizes: 560m, 1B1, 1B7, 3B, 7B1, 176B parameters. The bigger the model size, the more GPU resources required for the deployment.

**If you want to fine tune higher parameters model, please make sure you have sufficient GPU resources.**

This tutorial guides you reimplement BLOOM-LoRA using Alpaca-LoRA and Alpaca_data_cleaned.json using LoRA method to fine tune model.

## Model fine-tunning

### Create and run a Notebook server

You can directly use an image published on VMware harbor repo to create a Notebook server:

```bash
projects.registry.vmware.com/models/llm/pytorch/torchserve-notebook:latest-gpu-v0.15
```

Start the Notebook server with GPU:

```bash
docker run --gpus all -it -v `pwd`:/mnt projects.registry.vmware.com/models/llm/pytorch/torchserve-notebook:latest-gpu-v0.15
```

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start fine-tune model

When you choose the higher parameters model, please use large GPU resources to ensure the model running. There the author has fine tuned bloom-7b1 and bloom-560m model respectively, please refer to *bloom-7b1-fine-tune-final _ resultRecord – Weights & Biases.pdf* and *bloom-560m-medical-fine-tune _ resultRecord – Weights & Biases.pdf* these pdf files to know resource consumption.

```bash
python3 finetune.py
```

## Reference
- [BLOOM-LoRA: Low-Rank adaptation for various Instruct-Tuning datasets](https://github.com/linhduongtuan/BLOOM-LORA/tree/main)

- [List of Open Sourced Fine-Tuned Large Language Models (LLM)](https://medium.com/geekculture/list-of-open-sourced-fine-tuned-large-language-models-llm-8d95a2e0dc76)