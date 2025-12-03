# Treating api/services as a package containing all functionality for LLM's

import openai_api, hf_llm

# This must be updated whenever a new service is added
SERVICE_MODELS = {
    "openai": [openai_api.getModels, openai_api.initalizeModel, openai_api.query],
    "hf": [hf_llm.getModels, hf_llm.initalizeModel, hf_llm.query]
}

def initDefault():
    hf_llm.initalizeModel()