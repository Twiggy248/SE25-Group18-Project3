import os
from fastapi import APIRouter, Request, HTTPException, Response
from ..security import require_user
from ...managers import llm_manager as llm_service

router = APIRouter(
    prefix="/model",
    tags=["model"],
)


@router.get("s/")
async def getAvailableModelOptions():
    """
    GET /models/ - Returns all available models from all services
    """
    # Get the list of available hosts that have been integrated into the system
    availableModels = llm_service.getAvailableModels()

    # Get the list of available models (both api and local)
    return {"available_models": availableModels}


@router.put("s/")
async def setCurrentModel(request: Request):
    """
    PUT /models/ - Set/activate the current model
    """
    # Need a logged in user for the model to use
    require_user(request)

    # Get the request data
    data = await request.json()
    print(data)

    # Check that the passed API exists and is available
    api = data.get("model_type")
    print(api)
    if api is None:
        raise HTTPException(status_code=400, detail="Missing 'api' field in request body")
    
    if not llm_service.checkService(api):
        raise HTTPException(status_code=404, detail=f"Service '{api}' not supported!")

    # Get the Model Name
    model_name = data.get("model_option")
    if model_name is None:
        raise HTTPException(status_code=400, detail="Missing 'model_name' field in request body")

    # Get the API Key (optional for HuggingFace, required for OpenAI)
    api_key = data.get("api_key")
    
    # If OpenAI and no API key provided in request, check environment
    if api == 'openai' and not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=400, 
                detail="OpenAI API key required. Please provide 'api_key' in request or set OPENAI_API_KEY environment variable"
            )

    # Attempt to initialize the model
    try:
        llm_service.initModel(api, api_key, model_name)
        return {"message": f"Successfully activated {model_name}"}
    except ValueError as e:
        # Model compatibility or validation errors
        error_msg = str(e)
        if "does not recognize this architecture" in error_msg:
            raise HTTPException(
                status_code=400, 
                detail=f"Model '{model_name}' is not supported by your current Transformers version. "
                "Try a different model or update Transformers with: pip install --upgrade transformers"
            )
        elif "not a supported chat model" in error_msg:
            raise HTTPException(
                status_code=400,
                detail=f"'{model_name}' is not a chat model. Please select a GPT chat model."
            )
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except RuntimeError as e:
        # Runtime errors like missing tokens or initialization failures
        error_msg = str(e)
        if "HF_TOKEN" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="HuggingFace token not found. Please set the HF_TOKEN environment variable."
            )
        elif "OPENAI_API_KEY" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key not found. Please provide it in the request or set OPENAI_API_KEY environment variable."
            )
        else:
            raise HTTPException(status_code=500, detail=f"Failed to load model: {error_msg}")
    except Exception as e:
        # Catch-all for unexpected errors
        error_msg = str(e)
        if "out of memory" in error_msg.lower() or "oom" in error_msg.lower():
            raise HTTPException(
                status_code=400,
                detail=f"Not enough memory to load '{model_name}'. Try a smaller model."
            )
        else:
            raise HTTPException(status_code=500, detail=f"Error initializing model: {error_msg}")


@router.get("/status")
async def getModelStatus(request: Request):
    """
    GET /model/status - Get current model status
    """
    require_user(request)
    
    is_initialized = llm_service.status()
    
    if not is_initialized:
        return {
            "initialized": False,
            "model_name": None,
            "service": None
        }
    
    try:
        from ...managers.services import model_details as service
        return {
            "initialized": True,
            "model_name": service.getModelName(),
            "service": service.getModelService()
        }
    except Exception as e:
        return {
            "initialized": False,
            "model_name": None,
            "service": None,
            "error": str(e)
        }


@router.put("/api")
async def updateAPIAccess(request: Request):
    """
    PUT /model/api - Store API credentials for a service
    """
    # Need a logged in user for the model to use
    require_user(request)

    # Get the request data (FIXED: added await)
    data = await request.json()

    # Check that the passed API exists and is available
    api = data.get("api")
    if api is None:
        raise HTTPException(status_code=400, detail="Invalid API Service!")
    
    if not llm_service.checkService(api):
        raise HTTPException(status_code=404, detail="Service not supported!")

    # Check that the API Key is passed and is valid
    api_key = data.get("api_key")
    if api_key is None:
        raise HTTPException(status_code=400, detail="Invalid API Key!")
    
    # Add the API Key/Token to the current environment variables
    os.environ[f"{api.upper()}_API_KEY"] = api_key
    
    return {"message": "API key stored successfully"}


@router.put("")
async def useServiceModel(request: Request):
    """
    PUT /model - Activate a specific model from a service
    """
    # Need a logged in user for the model to use
    require_user(request)

    # Get the request data (FIXED: added await)
    data = await request.json()

    # Check that the passed API exists and is available
    api = data.get("api")
    if api is None:
        raise HTTPException(status_code=400, detail="Missing 'api' field in request body")
    
    if not llm_service.checkService(api):
        raise HTTPException(status_code=404, detail=f"Service '{api}' not supported!")

    # Get the Model Name
    model_name = data.get("model_name")
    if model_name is None:
        raise HTTPException(status_code=400, detail="Missing 'model_name' field in request body")

    # Get the API Key (optional for HuggingFace, required for OpenAI)
    api_key = data.get("api_key")
    
    # If OpenAI and no API key provided in request, check environment
    if api == 'openai' and not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise HTTPException(
                status_code=400, 
                detail="OpenAI API key required. Please provide 'api_key' in request or set OPENAI_API_KEY environment variable"
            )

    # Attempt to connect to the API
    try:
        llm_service.initModel(api, api_key, model_name)
        return {"message": f"Successfully activated {model_name}"}
    except ValueError as e:
        # Model compatibility or validation errors
        error_msg = str(e)
        if "does not recognize this architecture" in error_msg:
            raise HTTPException(
                status_code=400, 
                detail=f"Model '{model_name}' is not supported by your current Transformers version. "
                "Try a different model or update Transformers with: pip install --upgrade transformers"
            )
        elif "not a supported chat model" in error_msg:
            raise HTTPException(
                status_code=400,
                detail=f"'{model_name}' is not a chat model. Please select a GPT chat model."
            )
        else:
            raise HTTPException(status_code=400, detail=error_msg)
    except RuntimeError as e:
        # Runtime errors like missing tokens or initialization failures
        error_msg = str(e)
        if "HF_TOKEN" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="HuggingFace token not found. Please set the HF_TOKEN environment variable."
            )
        elif "OPENAI_API_KEY" in error_msg:
            raise HTTPException(
                status_code=400,
                detail="OpenAI API key not found. Please provide it in the request or set OPENAI_API_KEY environment variable."
            )
        else:
            raise HTTPException(status_code=500, detail=f"Failed to load model: {error_msg}")
    except Exception as e:
        # Catch-all for unexpected errors
        error_msg = str(e)
        if "out of memory" in error_msg.lower() or "oom" in error_msg.lower():
            raise HTTPException(
                status_code=400,
                detail=f"Not enough memory to load '{model_name}'. Try a smaller model."
            )
        else:
            raise HTTPException(status_code=500, detail=f"Error initializing model: {error_msg}")