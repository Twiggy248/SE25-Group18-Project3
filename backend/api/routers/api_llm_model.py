from fastapi import APIRouter, Request, HTTPException
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

    if len(availableModels) == 0:
        return HTTPException(404, "No Models Available")

    # Get the list of available local models (if can locally host)
    return {
        "available_models": availableModels
    }

@router.put("/api")
def useAPI(request: Request):

    # Need a logged in user for the model to use
    require_user(request)

    # Check that the passed API exists and is available


    # Check that the API Key is passed


    # Attempt to connect to the API

    pass

@router.put("")
def selectModel(request: Request):
    
    # Need a logged in user to select a model to use
    require_user(request)

    # Check that the type exists and is valid

    # Check that the Model exists and is valid

    # Attempt to start it up

    pass