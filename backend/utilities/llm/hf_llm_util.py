"""
Provides Utility Functions for HuggingFace LLM Models
-> Initializes the Embedder, Tokenizer, and Pipe
-> Provides universal interface to get Embedder/Tokenizer/Pipe
"""

from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, pipeline, PreTrainedModel, TextGenerationPipeline


embedder: SentenceTransformer | None = None
tokenizer: AutoTokenizer | None = None
pipe: TextGenerationPipeline | None = None

######################
#   DEFAULT VALUES   #
######################
DEFAULT_TEMPERATURE = 0.3
DEFAULT_TOP_P = 0.85
DEFAULT_REP_PENALTY = 1.1
DEFAULT_SENTENCE_TRANSFORMER = "all-MiniLM-L6-v2"

def initalizeEmbedder() -> SentenceTransformer:
    global embedder
    embedder = SentenceTransformer(DEFAULT_SENTENCE_TRANSFORMER)
    return embedder

def initalizeTokenizer(model_name: str, token: str) -> AutoTokenizer:
    """
    Creates the tokenizer that will be used by the Model
    
    :param model_name: The LLM model that will be used
    :type model_name: str
    :param token: The HuggingFace API Token
    :type token: str
    :return: The tokenizer that will be used by the LLM Model
    :rtype: AutoTokenizer
    """


    global tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=token)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    
    return tokenizer

def initalizePipe(model: PreTrainedModel, tokenizer: AutoTokenizer):
    """
    Creates the TextGenerationPipeline used by the HuggingFace API
    
    :param model: The pre-trained model loaded by Hugging Face
    :type model: PreTrainedModel
    :param tokenizer: The tokenizer used by the model
    :type tokenizer: AutoTokenizer
    """
    
    # Create the pipeline with the predefined default values
    global pipe
    pipe = pipeline("text-generation", 
                    model=model, 
                    tokenizer=tokenizer, 
                    device_map="auto",
                    temperature=DEFAULT_TEMPERATURE, 
                    do_sample=True, 
                    return_full_text=False,
                    top_p=DEFAULT_TOP_P,
                    repetition_penalty=DEFAULT_REP_PENALTY, 
                    eos_token_id=tokenizer.eos_token_id,
                    pad_token_id=tokenizer.eos_token_id)

def getEmbedder() -> SentenceTransformer:
    return embedder

def getTokenizer() -> AutoTokenizer:
    return tokenizer

def getPipe() -> TextGenerationPipeline:
    return pipe