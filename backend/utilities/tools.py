from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer

embedder = None
tokenizer = None

def initalizeEmbedder() -> SentenceTransformer:
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return embedder

def initalizeTokenizer(model_name: str, token: str) -> AutoTokenizer:
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=token)
    return tokenizer


def getEmbedder():
    return embedder

def getTokenizer():
    return tokenizer