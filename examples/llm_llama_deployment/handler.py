#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import os
import time
from pathlib import Path
from typing import List

import torch
from ts.torch_handler.base_handler import BaseHandler

from llama import ModelArgs
from llama import Tokenizer
from llama import Transformer

logger = logging.getLogger(__name__)


class LLAMAHandler(BaseHandler):
    def __init__(self):
        super().__init__()

        # model param
        self.max_seq_len = 1000
        self.max_batch_size = 1
        self.vocab_size = -1

        self.tokenizer = None
        self.model_args = None
        self.model = None

    def initialize(self, context):

        # super().initialize(context)
        # self.initialized = False

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
        model_dir = properties.get("model_dir")
        # serialized_file = self.manifest["model"]["serializedFile"]
        # model_pt_path = os.path.join(model_dir, serialized_file)

        tokenizer_model_path = os.path.join(model_dir, "tokenizer.model")
        self._init_tokenizer(tokenizer_model_path)

        params_file = os.path.join(model_dir, "params.json")
        self._init_model_params(params_file)

        self._init_model(model_dir)

        self.initialized = True

    def preprocess(self, data):
        logger.info("====preprocess start...")
        data = data[0]["body"].decode("utf-8")
        data = json.loads(data)
        logger.info(f"prompts:{data}")
        logger.info("====preprocess done")
        return data

    def inference(self, data, *args, **kwargs):
        logger.info(f"====kwargs:{kwargs}")
        logger.info(f"====torch.cuda.is_available():{torch.cuda.is_available()}")
        max_gen_len = kwargs["max_gen_len"]
        temperature = kwargs["temperature"]
        top_p = kwargs["top_p"]
        with torch.no_grad():
            result = self.generate(prompts=data,
                                   max_gen_len=max_gen_len,
                                   temperature=temperature,
                                   top_p=top_p)
        return result

    def postprocess(self, data):
        return data

    def handle(self, data, context):
        start_time = time.time()

        self.context = context
        metrics = self.context.metrics

        data = self.preprocess(data)
        # ["hello world", ...]
        prompts = data["prompts"]
        max_gen_len = data.get("max_gen_len", 100)
        temperature = data.get("temperature", 0.8)
        top_p = data.get("top_p", 0.95)
        output = self.inference(prompts,
                                max_gen_len=max_gen_len,
                                temperature=temperature,
                                top_p=top_p)
        output = self.postprocess(output)

        stop_time = time.time()
        metrics.add_time(
            "HandlerTime", round((stop_time - start_time) * 1000, 2), None, "ms"
        )
        return output

    def _init_tokenizer(self, tokenizer_model_path):
        assert os.path.isfile(tokenizer_model_path)

        tokenizer = Tokenizer(model_path=tokenizer_model_path)
        self.vocab_size = tokenizer.n_words
        self.tokenizer = tokenizer
        logger.info("===init tokenizer done")

    def _init_model_params(self, params_file):
        assert os.path.isfile(params_file)

        with open(params_file, "r") as f:
            params = json.loads(f.read())

        model_args: ModelArgs = ModelArgs(
            max_seq_len=self.max_seq_len,
            max_batch_size=self.max_batch_size,
            **params
        )
        model_args.vocab_size = self.vocab_size
        self.model_args = model_args
        logger.info("===init model_params done")

    def _init_model(self, ckpt_dir):
        checkpoints = sorted(Path(ckpt_dir).glob("*.pth"))
        logger.info(f"=====chekcpoints:{checkpoints}")
        # assert world_size == len(
        #     checkpoints
        # ), f"Loading a checkpoint for MP={len(checkpoints)} but world size is {world_size}"
        # ckpt_path = checkpoints[local_rank]

        ckpt_path = checkpoints[0]
        print("Loading")
        checkpoint = torch.load(ckpt_path, map_location="cpu")
        logger.info("====torch load done")

        # torch.set_default_tensor_type(torch.cuda.HalfTensor)
        if self.map_location == "cuda":
            torch.set_default_tensor_type(torch.cuda.HalfTensor)
        model = Transformer(self.model_args)
        torch.set_default_tensor_type(torch.FloatTensor)
        model.load_state_dict(checkpoint, strict=False)
        logger.info("====load_state_dict done")
        # model = model.to(device=self.device)
        model.eval()
        self.model = model
        logger.info("====init model done")

    def generate(self,
                 prompts: List[str],
                 max_gen_len: int,
                 temperature: float = 0.8,
                 top_p: float = 0.95,
                 ) -> List[str]:
        bsz = len(prompts)
        params = self.model.params
        assert bsz <= params.max_batch_size, (bsz, params.max_batch_size)

        prompt_tokens = [self.tokenizer.encode(
            x, bos=True, eos=False) for x in prompts]

        min_prompt_size = min([len(t) for t in prompt_tokens])
        max_prompt_size = max([len(t) for t in prompt_tokens])

        # total_len = min(params.max_seq_len, max_gen_len + max_prompt_size)
        total_len = min(params.max_seq_len, max_gen_len + max_prompt_size)

        tokens = torch.full(
            (bsz, total_len), self.tokenizer.pad_id).long().to(device=self.device)
        for k, t in enumerate(prompt_tokens):
            tokens[k, : len(t)] = torch.tensor(t).long()
        input_text_mask = tokens != self.tokenizer.pad_id
        start_pos = min_prompt_size
        prev_pos = 0
        for cur_pos in range(start_pos, total_len):
            print(f"------self.model:{next(self.model.parameters()).device}")
#            print(f"------tokens:{tokens.device}")
            logits = self.model.forward(tokens[:, prev_pos:cur_pos], prev_pos)
            if temperature > 0:
                probs = torch.softmax(logits / temperature, dim=-1)
                next_token = sample_top_p(probs, top_p)
            else:
                next_token = torch.argmax(logits, dim=-1)
            next_token = next_token.reshape(-1)
            # only replace token if prompt has already been generated
            next_token = torch.where(
                input_text_mask[:, cur_pos], tokens[:, cur_pos], next_token
            )
            tokens[:, cur_pos] = next_token
            prev_pos = cur_pos

        decoded = []
        for i, t in enumerate(tokens.tolist()):
            # cut to max gen len
            t = t[: len(prompt_tokens[i]) + max_gen_len]
            # cut to eos tok if any
            try:
                t = t[: t.index(self.tokenizer.eos_id)]
            except ValueError:
                pass
            decoded.append(self.tokenizer.decode(t))
        return decoded


def sample_top_p(probs, p):
    probs_sort, probs_idx = torch.sort(probs, dim=-1, descending=True)
    probs_sum = torch.cumsum(probs_sort, dim=-1)
    mask = probs_sum - probs_sort > p
    probs_sort[mask] = 0.0
    probs_sort.div_(probs_sort.sum(dim=-1, keepdim=True))
    next_token = torch.multinomial(probs_sort, num_samples=1)
    next_token = torch.gather(probs_idx, -1, next_token)
    return next_token
