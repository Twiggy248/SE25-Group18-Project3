import os, torch
from huggingface_hub import HfApi
from transformers import AutoModelForCausalLM, BitsAndBytesConfig, AutoConfig

from ...utilities.llm.hf_llm_util import initalizeEmbedder, initalizeTokenizer, initalizePipe
from ...managers.services.model_details import setModelName, setModelService
from ...utilities.llm import hf_llm_util

"""
Hugging Face will be one of the locally hosted model services that can be utilized
"""
DEFAULT_MODEL_NAME = "meta-llama/Llama-3.2-1B-Instruct"  # Smaller, more compatible default

# Cache models to avoid repeated API calls
_cached_hf_models: list[str] = []

# Known compatible model architectures
COMPATIBLE_ARCHITECTURES = {
    'llama', 'mistral', 'phi', 'qwen', 'gemma', 'falcon', 
    'gpt2', 'gpt_neo', 'gpt_neox', 'opt', 'bloom', 'mpt', 'stablelm'
}

# Model name patterns to exclude (non-text or incompatible models)
EXCLUDE_PATTERNS = [
    'gguf',          # GGUF format models (need llama.cpp)
    'vision',        # Vision/multimodal models
    'vlm',           # Vision language models
    'audio',         # Audio models
    'speech',        # Speech models
    'ocr',           # OCR models
    'embedding',     # Embedding models
    'video',         # Video models
    'music',         # Music generation models
]

def is_model_compatible(model_id: str, token: str) -> bool:
    """
    Check if a model is compatible with the current Transformers version
    """
    model_id_lower = model_id.lower()
    
    # Quick filter: exclude known incompatible patterns
    if any(pattern in model_id_lower for pattern in EXCLUDE_PATTERNS):
        return False
    
    try:
        # Suppress warnings during config loading
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            config = AutoConfig.from_pretrained(
                model_id, 
                token=token, 
                trust_remote_code=False
            )
        
        model_type = getattr(config, 'model_type', '').lower()
        
        # Check if the model type is in our compatible list
        return any(arch in model_type for arch in COMPATIBLE_ARCHITECTURES)
    except Exception:
        # Silently fail for incompatible models
        return False

def initalizeModel(model_name: str = None):
    """
    Initialize the Hugging Face model with optional 4-bit quantization
    and set up tokenizer & pipeline for later queries.
    """
    global _cached_hf_models

    if model_name is None:
        model_name = DEFAULT_MODEL_NAME

    token = os.getenv("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN environment variable not set")

    # Check if model is compatible before trying to load
    if not is_model_compatible(model_name, token):
        raise ValueError(
            f"Model '{model_name}' is not compatible with your current Transformers version. "
            "Please try a different model or update Transformers."
        )

    # Initialize embedding and tokenizer
    initalizeEmbedder()
    tokenizer = initalizeTokenizer(model_name, token)

    # Configure 4-bit quantization
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16,
    )

    # Load model
    try:
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            quantization_config=bnb_config,
            device_map="auto",
            use_auth_token=token,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            trust_remote_code=False,  # Security: don't execute remote code
        )
    except Exception as e:
        raise RuntimeError(f"Failed to load model '{model_name}': {str(e)}")

    # Initialize pipeline
    initalizePipe(model, tokenizer)

    # Set service details
    setModelName(model_name)
    setModelService("hf")

    # Cache compatible models at initialization
    hf_api = HfApi(token=token)
    try:
        # Suppress API warnings
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            all_models = hf_api.list_models(
                filter="text-generation",
                sort="trendingScore",
                limit=50  # Reduced from 100 for faster loading
            )
        
        # Filter to only include compatible models (silently)
        _cached_hf_models = []
        for m in all_models:
            if is_model_compatible(m.modelId, token):
                _cached_hf_models.append(m.modelId)
                if len(_cached_hf_models) >= 15:  # Limit to top 15 compatible models
                    break
        
        # Always include the default model if not already present
        if DEFAULT_MODEL_NAME not in _cached_hf_models:
            _cached_hf_models.insert(0, DEFAULT_MODEL_NAME)
            
    except Exception as e:
        print(f"Warning: Could not fetch Hugging Face models list: {e}")
        # Fallback to a curated list of known compatible models
        _cached_hf_models = [
            DEFAULT_MODEL_NAME,
            "meta-llama/Llama-3.2-3B-Instruct",
            "mistralai/Mistral-7B-Instruct-v0.3",
            "microsoft/phi-2",
            "google/gemma-2b-it",
        ]


def getModels() -> list[str]:
    """
    Returns cached list of Hugging Face models.
    If cache is empty, returns a default list of compatible models.
    """
    global _cached_hf_models
    
    if not _cached_hf_models:
        # Return a safe default list
        return [
            DEFAULT_MODEL_NAME,
            "meta-llama/Llama-3.2-3B-Instruct",
            "mistralai/Mistral-7B-Instruct-v0.2",
            "microsoft/phi-2",
        ]
    
    return _cached_hf_models.copy()


def query(instruction: str, query: str, max_new_tokens: int) -> dict[str, str]:
    """
    Queries the Hugging Face pipeline with instructions and user input.
    Returns the output dictionary from the pipeline.
    """
    pipe = hf_llm_util.getPipe()
    if pipe is None:
        raise RuntimeError("Pipeline not initialized. Call initalizeModel() first.")

    request_text = f"{instruction}\n\nUser:\n{query}\n\nAssistant:"
    outputs = pipe(request_text, max_new_tokens=max_new_tokens)

    # Return the first output
    return outputs[0]