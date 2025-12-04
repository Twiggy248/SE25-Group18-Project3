# -----------------------------------------------------------------------------
# File: main.py
# Description: Main FastAPI application for ReqEngine - handles API endpoints 
#              for requirements extraction, use case generation, and session management.
# Author: Pradyumna Chacham
#         Caleb Twigg
# Date: November 2025
# -----------------------------------------------------------------------------

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utilities.chunking_strategy import DocumentChunker
from database.db import init_db, migrate_db
from dotenv import load_dotenv
from api.router import router
from managers.llm_manager import initModel
from managers.services import preStart
app = FastAPI()
load_dotenv()

# Global Values
chunker = DocumentChunker(max_tokens=3000)

# Load in the API Router endpoints
app.include_router(router)


# --- CORS ---
origins = [
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Initialize SQLite ---
try:
    init_db()  # Initialize database tables
    migrate_db()  # Add new columns if needed
except Exception as e:
    migrate_db(reset=True)  # Reset and recreate database

# Check if we should load the model 
# (must not be in testing mode and Auto_boot should be true)
testing_mode = os.getenv("TESTING").lower() == "true"
auto_boot = os.getenv("AUTO_BOOT").lower() == "true"

load_model = auto_boot and (not testing_mode)

# If load model is true, the system will load the default model configuration
if load_model:
    initModel()
    
else:
    preStart()
    chunker = None