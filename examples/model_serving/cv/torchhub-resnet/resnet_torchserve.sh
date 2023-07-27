#!/bin/bash

#
# Get files necessary for the torchserve service from the Pytorch example on github
#
echo "  Downloading files"
wget https://raw.githubusercontent.com/pytorch/serve/master/examples/image_classifier/index_to_name.json

wget https://raw.githubusercontent.com/pytorch/serve/master/examples/image_classifier/resnet_18/model.py

#
# Sanity check
#
if [ ! -f "model.py" ] || [ ! -f "index_to_name.json" ]; then
    echo "  Error: Files could not be downloaded automatically. Download these files manually"
    exit 1
fi

if [ ! -f "$HOME/.cache/torch/hub/checkpoints/resnet18-f37072fd.pth" ]; then
    echo "  Error: Model file not found. Make sure pytorch_vision_resnet.ipynb has been executed properly with the resnet-18 model"
    exit 1
fi

echo "  Creating packages"
torch-model-archiver --model-name resnet-18 --version 1.0 --model-file ./model.py --serialized-file $HOME/.cache/torch/hub/checkpoints/resnet18-f37072fd.pth --handler image_classifier --extra-files ./index_to_name.json

echo "  Registering the model"
mkdir models
mv resnet-18.mar models

echo "  Starting torchserve service"
torchserve --start --ncs --model-store ./models --models resnet-18=resnet-18.mar

echo "Finished starting the torchserve service"

