#!/bin/bash

#
# Kserve expects to get model files from a PV volume root directory
#   in the following structure
# 
mkdir -p /data/model-store
mkdir -p /data/config

cp models/resnet-18.mar /data/model-store/
cp config.properties /data/config

