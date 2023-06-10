#!/bin/bash

sudo rm -rf _build/html /var/www/html/kubeflow
docker run --rm -it -e SPHINX_IMMATERIAL_EXTERNAL_RESOURCE_CACHE_DIR="/" -v `pwd`:/mnt ubuntu-python-playground-img:2.1 bash -c "cd /mnt; rm -rf _build/html; sphinx-build -b html . _build/html"
# sphinx-build -b html . _build/html
sudo mv _build/html /var/www/html/kubeflow
