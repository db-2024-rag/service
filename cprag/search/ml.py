from transformers import AutoModel, AutoTokenizer


class NeuralVectorizer:
    def __init__(self):
        self._model = AutoModel.from_pretrained('Tochka-AI/ruRoPEBert-e5-base-2k', trust_remote_code=True, attn_implementation='sdpa')
        self._tokenizer = AutoTokenizer.from_pretrained('')
