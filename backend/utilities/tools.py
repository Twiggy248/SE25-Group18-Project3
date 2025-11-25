from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, pipeline

"""
tools.py
Essentially all the things that get used by programs that are initalized in main.py
Including the Embedder, Tokenizer, and Pipe
"""


embedder = None
tokenizer = None
pipe = None

def initalizeEmbedder() -> SentenceTransformer:
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return embedder

def initalizeTokenizer(model_name: str, token: str) -> AutoTokenizer:
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=token)
    return tokenizer

def initalizePipe(model, tokenizer):
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device_map="auto")


def getEmbedder():
    return embedder

def getTokenizer():
    return tokenizer

def getPipe():
    return pipe