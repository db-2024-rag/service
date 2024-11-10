import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer

import torch.nn.functional as F

from cprag.settings import AppSettings


class Vectorizer:
    def __init__(self, settings: AppSettings):
        self._model = AutoModel.from_pretrained('Tochka-AI/ruRoPEBert-e5-base-2k', trust_remote_code=True,
                                                attn_implementation='sdpa')
        self._tokenizer = AutoTokenizer.from_pretrained('Tochka-AI/ruRoPEBert-e5-base-2k')

    def vectorize_document(self, text: str) -> torch.Tensor:
        tokenization = self._tokenizer.encode(f'passage: {text}', return_tensors='pt')
        with torch.inference_mode():
            return F.normalize(self._model(tokenization).pooler_output, dim=-1)[0]

    def vectorize_query(self, text: str) -> torch.Tensor:
        tokenization = self._tokenizer.encode(f'query: {text}', return_tensors='pt')
        with torch.inference_mode():
            return F.normalize(self._model(tokenization).pooler_output, dim=-1)[0]
