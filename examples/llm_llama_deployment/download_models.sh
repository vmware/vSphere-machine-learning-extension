#!/usr/bin/bash

#
# This script assumes that the LLaMA model files are available on a http server.
# If this is true, set correct model_size and download URLs and then run this script.
# Otherwise, ignore this script. Use any possible way to download the model files,
#   and make sure the file names and directory structure match the examples below.
#

MODEL_SIZE="7B"
mkdir -p $MODEL_SIZE

#
# This is an example of the http server URL.
# HTTP_SERVER_URL="http://10.117.7.217:8001/llama"

if [ -z "$HTTP_SERVER_URL" ]
then
    echo "  Error: Modify the script and specify the model download URL, then try again."
    exit 1
else
    echo "Downloading model files from $HTTP_SERVER_URL"
fi

curl --output tokenizer.model "${HTTP_SERVER_URL}/tokenizer.model"
curl --output "${MODEL_SIZE}/params.json" "${HTTP_SERVER_URL}/${MODEL_SIZE}/params.json"
curl --output "${MODEL_SIZE}/consolidated.00.pth" "${HTTP_SERVER_URL}/${MODEL_SIZE}/consolidated.00.pth"
