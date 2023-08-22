#!/usr/bin/bash

pip show sentencepiece > /dev/null 2>&1
if [ $? != 0 ]; then
    echo "  ERROR: Dependency not installed yet. Run \"pip install -r requirements.txt\""
    exit 1
fi

MODEL_PKG="./model_store/llama.mar"
if [ ! -f $MODEL_PKG ]; then
    echo "  ERROR: Model package file not found!"
    exit 1
fi

torchserve \
  --start \
  --ncs \
  --model-store "./model_store" \
  --models "./model_store/llama.mar" \
  --ts-config config.properties

