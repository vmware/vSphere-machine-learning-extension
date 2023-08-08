# `facebook/maskformer-swin-tiny-ade` Model Serving on VMware Kubeflow Using TorchServe

This tutorial guides you to serve `facebook/maskformer-swin-tiny-ade` on VMware Kubeflow using `torchserve`.

MaskFormer model trained on ADE20k semantic segmentation (tiny-sized version, Swin backbone). MaskFormer addresses instance, semantic and panoptic segmentation with the same paradigm: by predicting a set of masks and corresponding labels. Hence, all 3 tasks are treated as if they were instance segmentation. You can use this particular checkpoint for semantic segmentation. 

## Prerequisites

- 0 GPU, 8 CPUs (recommended), 16Gi memory (recommended)
- Use custom notebook image ``projects.registry.vmware.com/models/notebook/serve:pytorch-cpu-v3``.

## Get Started

### 1. Create a Notebook Server

In VMware Kubeflow UI, create a new Notebook Server using the custom notebook imge listed in [prerequisites](#prerequisites).

### 2. Download the model

Download the model from HuggingFace Hub using [`Download_model.py`](./Download_model.py).

```bash

python Download_model.py --model_name facebook/maskformer-swin-tiny-ade

```

Above command would return the path of the saved model, something like `model/models--facebook--maskformer-swin-tiny-ade/snapshots/cb488c7620d6b5fc737c94b86b25efe09ea750d1`. Use this path to compress the downloaded model.

```bash

cd model/models--facebook--maskformer-swin-tiny-ade/snapshots/<your_downloaded_model_id>
zip -r ../../../../model.zip *
cd ../../../../

```

Remember to change `<your_downloaded_model_id>`.

### Archive the model

Archive the model using `torch-model-archiver`. Note that in this command, file [`setup_config.json`](./setup_config.json) and [`custom_handler.py`](./custom_handler.py) are needed.

A few things to note here:

- This model only requires package `scipy`. So if you are using the notebook image mentioned in [Prerequisites](#prerequisites), then you do not need any extra `pip` install work or `requirement.txt` file.
- So far the configuration files are designed to NOT use GPU.

```bash

torch-model-archiver --model-name maskformer --version 1.0 --handler custom_handler.py --extra-files model.zip,setup_config.json

```

The above command would generate a `.mar` file, `maskformer.mar` in this case.

### Register the model

Create a directory to hold the model.

```bash

mkdir model_store
mv maskformer.mar model_store

```

### Start model server

Start model server using `torchserve`. File [`config.properties`](./config.properties) is needed. **Note that you need to change `model_store` value in this file to your `model_store` folder path.**

```bash

torchserve --start --ncs --ts-config config.properties

```

The model server should start soon.

### Model inference

You can then test the served model.

This model requires an image URL as input. The image URL should be stored in a `.txt` file. We provide your with a sample image URL in [`sample_url.txt`](./sample_url.txt).

Curl the model inference API.

```bash

curl -v "http://localhost:8080/predictions/maskformer" -T sample_url.txt

```

The output contains the score of each segmented elements. The output of the provided image is provided below.

```text

root@test-serve-big-02-0:~# curl -v "http://localhost:8080/predictions/maskformer" -T sample_url.txt
*   Trying ::1:8080...
* TCP_NODELAY set
* Connected to localhost (::1) port 8080 (#0)
> PUT /predictions/maskformer HTTP/1.1
> Host: localhost:8080
> User-Agent: curl/7.68.0
> Accept: */*
> Content-Length: 101
> Expect: 100-continue
> 
* Mark bundle as not supporting multiuse
< HTTP/1.1 100 Continue
* We are completely uploaded and fine
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 
< x-request-id: b403b6a4-423e-4f05-8048-25662307fa66
< Pragma: no-cache
< Cache-Control: no-cache; no-store, must-revalidate, private
< Expires: Thu, 01 Jan 1970 00:00:00 UTC
< content-length: 612
< connection: keep-alive
< 
[
  {
    "id": 1,
    "label_id": 17,
    "was_fused": false,
    "score": 0.900921
  },
  {
    "id": 2,
    "label_id": 25,
    "was_fused": false,
    "score": 0.95619
  },
  {
    "id": 3,
    "label_id": 6,
    "was_fused": false,
    "score": 0.985853
  },
  {
    "id": 4,
    "label_id": 4,
    "was_fused": false,
    "score": 0.998232
  },
  {
    "id": 5,
    "label_id": 9,
    "was_fused": false,
    "score": 0.995336
  },
  {
    "id": 6,
    "label_id": 0,
    "was_fused": false,
    "score": 0.969291
  },
  {
    "id": 7,
    "label_id": 2,
    "was_fused": false,
    "score": 0.999394
  }
* Connection #0 to host localhost left intact

```

## Troubleshooting

### SSL Error

While downingloading the model or executing the custom handler, some users may meet error messages similar to `SSLError: HTTPSConnectionPool(host='huggingface.co', port=443): Max retries exceeded with url: /togethercomputer/RedPajama-INCITE-Instruct-3B-v1/resolve/main/tokenizer_config.json (Caused by SSLError(SSLEOFError(8, 'EOF occurred in violation of protocol (_ssl.c:1129)')))`. This is because some of the codes require downloading or using resources from Hugging Face Hub. And therefore there may be HTTPS proxy issues depending on your own settings.

To solve this, you need to add below chunks of codes at the beginning of [Download_model.py](./Download_model.py) and [custom_handler.py](./custom_handler.py) to manually export the proxy.

```python
import os
os.environ['HTTP_PROXY'] = <your_http_proxy>
os.environ['HTTPS_PROXY'] = <your_https_proxy>
```

