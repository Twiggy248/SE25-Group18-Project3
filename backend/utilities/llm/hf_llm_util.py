from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, pipeline, PreTrainedModel

"""
tools.py
Essentially all the things that get used by programs that are initalized in main.py
Including the Embedder, Tokenizer, and Pipe
"""


embedder = None
tokenizer = None
pipe = None

def initalizeEmbedder() -> SentenceTransformer:
    global embedder
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return embedder

def initalizeTokenizer(model_name: str, token: str) -> AutoTokenizer:
    global tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=token)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    
    return tokenizer

def initalizePipe(model: PreTrainedModel, tokenizer: AutoTokenizer):
    model.config.eos_token_id = tokenizer.eos_token_id
    model.config.pad_token_id = tokenizer.pad_token_id
    
    global pipe
    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device_map="auto")

def getEmbedder():
    return embedder

def getTokenizer():
    return tokenizer

def getPipe():
    return pipe