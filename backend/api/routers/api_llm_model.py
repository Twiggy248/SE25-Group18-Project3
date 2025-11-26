import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from database.managers import session_db_manager, usecase_db_manager
from utilities.exports import export_to_docx, export_to_markdown
from database.models import SessionRequest
from api.security import require_user, session_belongs_to_user

router = APIRouter(
    prefix="/model",
    tags=["model"],
)


@router.get("s/")
def getAvailableModelOptions():

    # Get the list of available hosts that have been integrated into the system
        # Get the list of available models for each host

    # Get the list of available local models (if can locally host)

    pass

@router.put("/api")
def useAPI(request: Request):

    # Check that the passed API exists and is available


    # Check that the API Key is passed


    # Attempt to connect to the API

    pass

@router.put("/")
def selectModel(request: Request):

    # Check that the type exists and is valid

    # Check that the Model exists and is valid

    # Attempt to start it up

    pass