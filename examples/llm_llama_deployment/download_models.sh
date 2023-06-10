#!/usr/bin/bash

#
# This script assumes that the LLaMA model files are available on a http server.
# If this is true, set correct model_size and download URLs and then run this script.
# Otherwise, ignore this script. Use any possible way to download the model files,
#   and make sure the file names and directory structure match the examples below.
#

MODEL_SIZE="7B"
mkdir -p $MODEL_SIZE

HTTP_SERVER_URL="http://10.117.4.208:8001"
echo "Downloading model files from $HTTP_SERVER_URL"

curl --output tokenizer.model "${HTTP_SERVER_URL}/tokenizer.model"
curl --output "${MODEL_SIZE}/params.json" "${HTTP_SERVER_URL}/params.json"
curl --output "${MODEL_SIZE}/consolidated.00.pth" "${HTTP_SERVER_URL}/consolidated.00.pth"
