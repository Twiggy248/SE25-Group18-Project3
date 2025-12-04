import os
from fastapi import APIRouter, Request, HTTPException, Response
from api.security import require_user
from managers import llm_manager as llm_service

router = APIRouter(
    prefix="/model",
    tags=["model"],
)


@router.get("s/")
def getAvailableModelOptions():

    # Get the list of available hosts that have been integrated into the system
    availableModels = llm_service.getAvailableModels()

    # Get the list of available models (both api and local)
    return {"available_models": availableModels}

@router.put("/api")
def updateAPIAccess(request: Request):
    # Need a logged in user for the model to use
    require_user(request)

    # Get the request data
    data = request.json()

    # Check that the passed API exists and is available
    api = data.get("api")
    if (api is None):
        raise HTTPException(406, "Invalid API Service!")
    
    if (llm_service.checkService(api) is False):
        raise HTTPException(404, "Service not supported!")

    # Check that the API Key is passed and is valid
    api_key = data.get("api_key")
    if (api_key is None):
        raise HTTPException(406, "Invalid API Key!")
    
    # Add the API Key/Token to the current enviroment variables
    os.environ[f"{api}_key"] = api_key

@router.put("")
def useServiceModel(request: Request):

    # Need a logged in user for the model to use
    require_user(request)

    # Get the request data
    data = request.json()

    # Check that the passed API exists and is available
    api = data.get("api")
    if (api is None):
        raise HTTPException(406, "Invalid API Service!")
    
    if (llm_service.checkService(api) is False):
        raise HTTPException(404, "Service not supported!")

    # Check that the API Key is passed and is valid
    api_key = data.get("api_key")
    if (api_key is None):
        raise HTTPException(406, "Invalid API Key!")

    # Get the Model Name
    model_name = data.get("model_name")
    if (model_name is None):
        raise HTTPException(406, "Invalid Model Name!")

    # Attempt to connect to the API
    try:
        llm_service.initModel(api, api_key, model_name)
        return Response("Success!")
    except:
        raise HTTPException(404, "Error Initalizing LLM Service and Model")