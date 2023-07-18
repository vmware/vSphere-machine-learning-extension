import json
import logging
import os
import zipfile
from abc import ABC

os.environ['HTTP_PROXY'] = 'http://proxy.vmware.com:3128'
os.environ['HTTPS_PROXY'] = 'http://proxy.vmware.com:3128'

import torch
import transformers

from transformers import MaskFormerFeatureExtractor, MaskFormerForInstanceSegmentation
from PIL import Image
import requests

from ts.torch_handler.base_handler import BaseHandler

logger = logging.getLogger(__name__)
logger.info("Transformers version %s", transformers.__version__)


TORCH_DTYPES = {
    "float16": torch.float16,
    "float32": torch.float32,
    "float64": torch.float64,
}


class TransformersSeqClassifierHandler(BaseHandler, ABC):
    """
    Transformers handler class for sequence, token classification and question answering.
    """

    def __init__(self):
        super(TransformersSeqClassifierHandler, self).__init__()
        self.initialized = False

    def initialize(self, ctx):
        self.manifest = ctx.manifest
        properties = ctx.system_properties
        model_dir = properties.get("model_dir")
        self.device = torch.device(
            "cuda:" + str(properties.get("gpu_id"))
            if torch.cuda.is_available() and properties.get("gpu_id") is not None
            else "cpu"
        )
        # Loading the model and feature extractor from checkpoint and config files based on the user's choice of mode
        # further setup config can be added.
        with zipfile.ZipFile(model_dir + "/model.zip", "r") as zip_ref:
            zip_ref.extractall(model_dir + "/model")

        # read configs for the mode, model_name, etc. from setup_config.json
        setup_config_path = os.path.join(model_dir, "setup_config.json")
        if os.path.isfile(setup_config_path):
            with open(setup_config_path) as setup_config_file:
                self.setup_config = json.load(setup_config_file)
        else:
            logger.warning("Missing the setup_config.json file.")

        self.model = MaskFormerForInstanceSegmentation.from_pretrained(
            model_dir + "/model",
            revision=self.setup_config["revision"],
            max_memory={
                int(key) if key.isnumeric() else key: value
                for key, value in self.setup_config["max_memory"].items()
            },
            low_cpu_mem_usage=self.setup_config["low_cpu_mem_usage"],
            offload_folder=self.setup_config["offload_folder"],
            offload_state_dict=self.setup_config["offload_state_dict"],
            # torch_dtype=TORCH_DTYPES[self.setup_config["torch_dtype"]],
        )

        self.feature_extractor = MaskFormerFeatureExtractor.from_pretrained(
            model_dir + "/model"
        )

        self.model.eval()
        logger.info("Transformer model from path %s loaded successfully", model_dir)

        self.initialized = True

    def preprocess(self, requests_input):
        """Basic text preprocessing, based on the user's chocie of application mode.
        Args:
            requests (str): The Input data in the form of text is passed on to the preprocess
            function.
        Returns:
            list : The preprocess function returns a list of Tensor for the size of the word tokens.
        """
        # print("-------------------------------------")
        # print(enumerate(requests_input))
        for idx, data in enumerate(requests_input):
            url = data.get("data")
            if url is None:
                url = data.get("body")
            if isinstance(url, (bytes, bytearray)):
                url = url.decode("utf-8")
            return url

    def inference(self, url):
        image = Image.open(requests.get(url, stream=True).raw)
        inputs = self.feature_extractor(images=image, return_tensors="pt")
        outputs = self.model(**inputs)
        class_queries_logits = outputs.class_queries_logits
        masks_queries_logits = outputs.masks_queries_logits
        predicted_semantic_map = self.feature_extractor.post_process_semantic_segmentation(outputs, target_sizes=[image.size[::-1]])[0]
        # print("-------------------------------------")
        # print(list(predicted_semantic_map))
        # print("-------------------------------------")
        inferences = []
        predicted_semantic_map = self.feature_extractor.post_process_panoptic_segmentation(outputs, target_sizes=[image.size[::-1]])[0]
        inferences.append(predicted_semantic_map["segments_info"])
        return inferences

    def postprocess(self, inference_output):
        """Post Process Function converts the predicted response into Torchserve readable format.
        Args:
            inference_output (list): It contains the predicted response of the input text.
        Returns:
            (list): Returns a list of the Predictions and Explanations.
        """
        return inference_output