# Treating api/services as a package containing all functionality for LLM's

from . import openai_api, hf_llm
from sentence_transformers import SentenceTransformer


# This must be updated whenever a new service is added
SERVICE_MODELS = {
    "openai": [openai_api.getModels, openai_api.initalizeModel, openai_api.query],
    "hf": [hf_llm.getModels, hf_llm.initalizeModel, hf_llm.query]
}

def initDefault():
    hf_llm.initalizeModel()
    openai_api.initalizeModel("gpt-4o-mini")

# Global Embedder/SentenceTransformer
embedder: SentenceTransformer
DEFAULT_SENTENCE_TRANSFORMER = "all-MiniLM-L6-v2"

def preStart():
    global embedder
    embedder = SentenceTransformer(DEFAULT_SENTENCE_TRANSFORMER)

def getEmbedder() -> SentenceTransformer:
    return embedder