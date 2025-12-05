import os, torch
from huggingface_hub import HfApi

from transformers import AutoModelForCausalLM, BitsAndBytesConfig

from ...utilities.llm.hf_llm_util import initalizeEmbedder, initalizeTokenizer, initalizePipe
from ...managers.services.model_details import setModelName, setModelService
from ...utilities.llm import hf_llm_util

"""
Hugging Face will be one of the locally hosted model services that can be utilized
"""
DEFAULT_MODEL_NAME = "meta-llama/Llama-3.2-3B-Instruct"

def initalizeModel(model_name: str = None):

    # If no model name is passed, just use the default
    if model_name is None:
        model_name = DEFAULT_MODEL_NAME

    token = os.getenv("HF_TOKEN")
    
    initalizeEmbedder()

    # Configure 4-bit quantization
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16,
    )
    
    tokenizer = initalizeTokenizer(model_name, token)

    # Load model with 4-bit quantization
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map="auto",
        token=token,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
    )

    initalizePipe(model, tokenizer)

    setModelName(model_name)
    setModelService("hf")


def getModels() -> list[str]:
    """
    Returns Available Hugging Face Models as a list of strings
    """

    token = os.getenv("HF_TOKEN")
    hf = HfApi(token=token)

    models = hf.list_models(task="text-generation")

    models_list = [m.id for m in models]

    return models_list


def query(instruction: str, query: str, max_new_tokens: int) -> dict[str, str]:
    pipe = hf_llm_util.getPipe()

    # Hugging face uses one string for a query
    request = f"{instruction}\n\nUser:\n{query}\n\nAssistant:"

    # Make the query
    outputs = pipe(request, max_new_tokens=max_new_tokens)
        
    return outputs[0]