# -----------------------------------------------------------------------------
# File: main.py
# Description: Main FastAPI application for ReqEngine - handles API endpoints 
#              for requirements extraction, use case generation, and session management.
# Author: Pradyumna Chacham
#         Caleb Twigg
# Date: November 2025
# -----------------------------------------------------------------------------

import os, torch

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from transformers import AutoModelForCausalLM, BitsAndBytesConfig, AutoTokenizer, pipeline

from backend.utilities.chunking_strategy import DocumentChunker
from backend.database.db import init_db, migrate_db
from dotenv import load_dotenv
from backend.api.router import router

app = FastAPI()
load_dotenv()

# Global Values
tokenizer = None
model = None
pipe = None
embedder = SentenceTransformer("all-MiniLM-L6-v2")
chunker = DocumentChunker(max_tokens=3000)
MODEL_NAME = "meta-llama/Llama-3.2-3B-Instruct"  # Define for tests

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
    print(f"Database initialization error: {str(e)}")
    print("Attempting database reset...")
    migrate_db(reset=True)  # Reset and recreate database

# ============================================================================
# MODEL LOADING - Skip in test environment
# ============================================================================

if not os.getenv("TESTING"):
    # --- Load LLaMA 3.2 3B Instruct ---
    MODEL_NAME = "meta-llama/Llama-3.2-3B-Instruct"
    token = os.getenv("HF_TOKEN")

    print("Loading model with 4-bit quantization...")

    # Configure 4-bit quantization for RTX 3050
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16,
    )

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, token=token)

    # Load model with 4-bit quantization
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        token=token,
        torch_dtype=torch.float16,
        low_cpu_mem_usage=True,
    )

    pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, device_map="auto")

    print("Model loaded successfully with 4-bit quantization!")

    # Already initialized embedding model for duplicate detection
    # Already initialized document chunker

else:
    print("Testing mode: Model loading skipped")
    embedder = None
    chunker = None
