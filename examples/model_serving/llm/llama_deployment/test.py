#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json
import requests

url = "http://localhost:8080/predictions/llama"

PROMPT = "What is Kubeflow?"

print("The PROMPT is: ", PROMPT)

data = {
    "prompts": [PROMPT],
    "max_gen_len": 100,
}

data = json.dumps(data)
res = requests.post(url=url, data=data)
if res.ok:
    print(res.text)
else:
    print("ERROR: Response not valid for your requests")


