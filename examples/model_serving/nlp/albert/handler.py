#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import os
import time
import torch
from transformers import pipeline
from ts.torch_handler.base_handler import BaseHandler

logger = logging.getLogger(__name__)


class AlbertHandler(BaseHandler):
    def __init__(self):
        super().__init__()

        self.model_name = "albert"

    def initialize(self, context):
        properties = context.system_properties
        self.map_location = (
            "cuda"
            if torch.cuda.is_available() and properties.get("gpu_id") is not None
            else "cpu"
        )
        self.device = torch.device(
            self.map_location + ":" + str(properties.get("gpu_id"))
            if torch.cuda.is_available() and properties.get("gpu_id") is not None
            else self.map_location
        )
        self.manifest = context.manifest
        logger.info("========properties:" + json.dumps(properties, ensure_ascii=False))
        logger.info("========manifest:" + json.dumps(self.manifest, ensure_ascii=False))
        model_dir = os.path.join(properties.get("model_dir"), self.model_name)
        logger.info(f"========model_dir:{model_dir}")
        self.initialized = True

        unmasker = pipeline('fill-mask', model=model_dir)
        self.unmasker = unmasker

    def preprocess(self, data):
        data = data[0]["body"].decode("utf-8")
        data = json.loads(data)
        logger.info(f"data:{data}")
        return data

    def inference(self, data, *args, **kwargs):
        logger.info(f"====torch.cuda.is_available():{torch.cuda.is_available()}")
        with torch.no_grad():
            result = self.generate(input_data=data)
        return result

    def postprocess(self, data):
        return data

    def handle(self, data, context):
        start_time = time.time()

        self.context = context
        metrics = self.context.metrics

        logger.info('handle(),===============')

        data = self.preprocess(data)
        output = self.inference(data)
        output = self.postprocess(output)

        stop_time = time.time()
        metrics.add_time(
            "HandlerTime", round((stop_time - start_time) * 1000, 2), None, "ms"
        )
        return output

    def generate(self, input_data):
        unmasker = self.unmasker
        output = unmasker(input_data)
        output = [output]

        return output








