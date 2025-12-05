from openai import OpenAI
import os

from . import model_details as service

client: OpenAI

# Initalize OpenAI model
def initalizeModel(model_name: str):
    """
    Boots Up the OpenAI API, and assigns model name for future reference
    """
    key = None
    if (os.environ("openai_key") is not None):
        key = os.environ("openai_key")


    global client
    client = OpenAI(key)
    service.setModelName(model_name)
    service.setModelService("openai")


def getModels() -> list[str]:
    """
    Returns Available OpenAI Models as a list of strings
    """
    models = client.models.list()
    models_list = [m.id for m in models.data]
    return models_list


def query(instructionsStr: str, query: str, max_tokens: int) -> dict[str, object]:
    """
    Queries an OpenAI Model given the request and the system context
    Returns the response as a Dict object
    """
    response = client.responses.create(
        model=service.getModelName(),
        instructions=instructionsStr,
        input=query,
        max_output_tokens=max_tokens
    )

    return response.to_dict()