import json
from openai import OpenAI
import backend.utilities.model_details as service

client = None

# Initalize OpenAI model
def initalizeModel(model_name: str):
    """
    Boots Up the OpenAI API, and assigns model name for future reference
    """
    global client
    client = OpenAI()
    service.setModelName(model_name)
    service.setModelService("openai")


def getModels() -> list[str]:
    """
    Returns Available OpenAI Models as a list of strings
    """
    models = client.models.list()
    models_list = [m.id for m in models.data]
    return models_list


def query(request: str, system_context: str):
    """
    Queries an OpenAI Model given the request and the system context
    Returns the response
    """
    response = client.chat.completions.create(
        model=service.getModelName(),
        messages=[
            {"role": "system", "content": system_context},
            {"role": "user", "content": request},
        ]
    )
    return response.choices[0].message.content