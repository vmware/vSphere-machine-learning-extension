#!/bin/bash

#
# Get files necessary for the torchserve service from the Pytorch example
#
echo "  Downloading files"
wget https://raw.githubusercontent.com/pytorch/serve/master/examples/image_classifier/index_to_name.json

wget https://raw.githubusercontent.com/pytorch/serve/master/examples/image_classifier/resnet_18/model.py

echo "  Creating packages"
torch-model-archiver --model-name resnet-18 --version 1.0 --model-file ./model.py --serialized-file .cache/torch/hub/checkpoints/resnet18-f37072fd.pth --handler image_classifier --extra-files ./index_to_name.json

mkdir models
mv resnet-18.mar models

echo "  Starting torchserve service"
torchserve --start --model-store ./models --models resnet-18=resnet-18.mar

echo "Finished starting the torchserve service"

