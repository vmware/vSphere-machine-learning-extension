# !/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import requests

url = "http://localhost:8080/predictions/albert"
data = "Hello I'm a [MASK] dog."

print("\nThe input is: " + data)

data = json.dumps(data)
res = requests.post(url=url, data=data)
if res.ok:
    res = res.text
    res = json.loads(res)
    print("The predition result is: ")
    print(res)
else:
    print("ERROR in the prediction test....")
