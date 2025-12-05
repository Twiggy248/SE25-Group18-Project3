from openai import OpenAI
import os

from . import model_details as service

client: OpenAI | None = None

# Known chat model prefixes/patterns for OpenAI
CHAT_MODEL_PATTERNS = [
    'gpt-4',
    'gpt-3.5',
    'gpt-4o',
    'chatgpt',
    'o1',  # OpenAI's reasoning models
    'o3',  # Future reasoning models
]

# Models to explicitly exclude (non-chat models)
EXCLUDE_PATTERNS = [
    'whisper',      # Audio transcription
    'tts',          # Text-to-speech
    'dall-e',       # Image generation
    'davinci',      # Legacy completion models
    'curie',        # Legacy completion models
    'babbage',      # Legacy completion models
    'ada',          # Legacy completion models
    'embedding',    # Embedding models
    'text-embedding',
    'moderation',   # Moderation models
]

def is_chat_model(model_id: str) -> bool:
    """
    Determine if a model is a chat model based on its ID.
    
    :param model_id: The model identifier
    :return: True if it's a chat model, False otherwise
    """
    model_lower = model_id.lower()
    
    # Exclude non-chat models first
    if any(pattern in model_lower for pattern in EXCLUDE_PATTERNS):
        return False
    
    # Include known chat models
    if any(pattern in model_lower for pattern in CHAT_MODEL_PATTERNS):
        return True
    
    # Default to False for unknown models
    return False

# Initialize OpenAI model
def initalizeModel(model_name: str):
    """
    Boots Up the OpenAI API, and assigns model name for future reference
    """
    key = os.getenv("OPENAI_API_KEY")

    if not key:
        raise RuntimeError("Missing environment variable: OPENAI_API_KEY")

    global client
    client = OpenAI(api_key=key)

    # Verify that the selected model is a chat model
    if not is_chat_model(model_name):
        raise ValueError(f"Model '{model_name}' is not a supported chat model")

    service.setModelName(model_name)
    service.setModelService("openai")


def getModels() -> list[str]:
    """
    Returns Available OpenAI Chat Models as a list of strings.
    Filters out non-chat models like Whisper, DALL-E, embeddings, etc.
    """
    global client
    if client is None:
        raise RuntimeError("OpenAI client not initialized. Call initializeModel() first.")

    try:
        models = client.models.list()
        
        # Filter to only include chat models
        chat_models = [
            m.id for m in models.data 
            if is_chat_model(m.id)
        ]
        
        # Sort models with priority order
        priority_models = []
        other_models = []
        
        for model in chat_models:
            if model.startswith('gpt-4o'):
                priority_models.insert(0, model)  # gpt-4o at the top
            elif model.startswith('gpt-4'):
                priority_models.append(model)
            elif model.startswith('o1'):
                priority_models.append(model)
            else:
                other_models.append(model)
        
        # Combine and return
        sorted_models = priority_models + sorted(other_models)
        
        # If no models found, return a default list
        if not sorted_models:
            return [
                "gpt-4o",
                "gpt-4o-mini", 
                "gpt-4-turbo",
                "gpt-4",
                "gpt-3.5-turbo"
            ]
        
        return sorted_models
        
    except Exception as e:
        print(f"Warning: Could not fetch OpenAI models: {e}")
        # Return a default list of known chat models
        return [
            "gpt-4o",
            "gpt-4o-mini",
            "gpt-4-turbo", 
            "gpt-4",
            "gpt-3.5-turbo"
        ]


def query(instructionsStr: str, query: str, max_tokens: int) -> dict[str, object]:
    """
    Queries an OpenAI Chat Model given the request and the system context.
    Returns the response as a Dict object.
    """
    global client
    if client is None:
        raise RuntimeError("OpenAI client not initialized. Call initializeModel() first.")

    try:
        # Use the Chat Completions API (correct endpoint for chat models)
        response = client.chat.completions.create(
            model=service.getModelName(),
            messages=[
                {"role": "system", "content": instructionsStr},
                {"role": "user", "content": query}
            ],
            max_tokens=max_tokens
        )
        
        # Convert to dict format matching your expected structure
        return {
            "id": response.id,
            "model": response.model,
            "content": response.choices[0].message.content,
            "role": response.choices[0].message.role,
            "finish_reason": response.choices[0].finish_reason,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
    except Exception as e:
        raise RuntimeError(f"Error querying OpenAI model: {str(e)}")