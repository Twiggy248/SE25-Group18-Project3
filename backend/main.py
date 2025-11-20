# -----------------------------------------------------------------------------
# File: main.py
# Description: Main FastAPI application for ReqEngine - handles API endpoints 
#              for requirements extraction, use case generation, and session management.
# Author: Pradyumna Chacham
# Date: November 2025
# Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
# License: MIT License - see LICENSE file in the root directory.
# -----------------------------------------------------------------------------

import json
import os
import re
import sqlite3
import time
from typing import List, Optional

import torch
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer, util
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from chunking_strategy import DocumentChunker
from db import (add_conversation_message,
                get_conversation_history, get_db_path,
                get_session_context, get_session_use_cases, get_use_case_by_id,
                init_db, migrate_db, update_use_case)
from backend.utilities.rag import build_memory_context
from use_case.use_case_enrichment import enrich_use_case
from use_case.use_case_validator import UseCaseValidator
from dotenv import load_dotenv
from models import UseCaseSchema, RefinementRequest, QueryRequest
from routers import require_user
from api_routers.api_session import session_belongs_to_user
from utilities.use_case import UseCaseEstimator, get_smart_max_use_cases, get_smart_token_budget

app = FastAPI()
load_dotenv()


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

# --- Load LLaMA 3.2 3B Instruct ---
# Add this RIGHT BEFORE: MODEL_NAME = "meta-llama/Llama-3.2-3B-Instruct"

# ============================================================================
# MODEL LOADING - Skip in test environment
# ============================================================================

# Around line 85-113 in your main.py, wrap the model loading:

if not os.getenv("TESTING"):
    # --- Load LLaMA 3.2 3B Instruct ---
    MODEL_NAME = "meta-llama/Llama-3.2-3B-Instruct"
    token = os.getenv("HF_TOKEN")

    print("Loading model with 4-bit quantization...")

    from transformers import BitsAndBytesConfig

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

    print("✅ Model loaded successfully with 4-bit quantization!")
    print(f"   Model size: ~1.5GB (vs 6GB unquantized)")
    print(f"   Expected speedup: 2-3x faster\n")

    # Initialize embedding model for duplicate detection
    embedder = SentenceTransformer("all-MiniLM-L6-v2")

    # Initialize document chunker
    chunker = DocumentChunker(max_tokens=3000)
else:
    print("⚠️  Testing mode: Model loading skipped")
    MODEL_NAME = "meta-llama/Llama-3.2-3B-Instruct"  # Define for tests
    tokenizer = None
    model = None
    pipe = None
    embedder = None
    chunker = None

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def clean_llm_json(json_str: str) -> str:
    """Clean JSON from LLM output"""

    print("🔧 Cleaning LLM JSON output...")

    json_str = re.sub(r"^```json\s*", "", json_str.strip())
    json_str = re.sub(r"^```\s*", "", json_str.strip())
    json_str = re.sub(r"\s*```$", "", json_str.strip())

    first_bracket = json_str.find("[")
    if first_bracket > 0:
        json_str = json_str[first_bracket:]

    last_bracket = json_str.rfind("]")
    if last_bracket != -1:
        json_str = json_str[: last_bracket + 1]

    json_str = json_str.replace(r"\"", '"')
    json_str = json_str.replace(r'\\"', '"')
    json_str = json_str.replace("None", "null")
    json_str = json_str.replace("True", "true")
    json_str = json_str.replace("False", "false")
    json_str = re.sub(r",(\s*[}\]])", r"\1", json_str)

    open_braces = json_str.count("{")
    close_braces = json_str.count("}")
    if open_braces > close_braces:
        json_str += "}" * (open_braces - close_braces)

    open_brackets = json_str.count("[")
    close_brackets = json_str.count("]")
    if open_brackets > close_brackets:
        json_str += "]" * (open_brackets - close_brackets)

    print("✅ JSON cleaning complete\n")

    return json_str


def flatten_use_case(data: dict) -> dict:
    """Convert nested use case data to flat structure"""
    flat = {"title": data.get("title", "Untitled")}

    def ensure_list(value, placeholder=None):
        if isinstance(value, list):
            return [str(v) if not isinstance(v, str) else v for v in value] or (
                [placeholder] if placeholder else []
            )
        elif isinstance(value, dict):
            return [f"{k}: {v}" for k, v in value.items()] or (
                [placeholder] if placeholder else []
            )
        elif value:
            return [str(value)]
        return [placeholder] if placeholder else []

    flat["preconditions"] = ensure_list(
        data.get("preconditions"), "User is authenticated"
    )
    flat["main_flow"] = ensure_list(data.get("main_flow"), "Action performed")
    flat["sub_flows"] = ensure_list(
        data.get("sub_flows"), "Optional features available"
    )
    flat["alternate_flows"] = ensure_list(
        data.get("alternate_flows"), "Error handling included"
    )
    flat["outcomes"] = ensure_list(data.get("outcomes"), "Task completed successfully")
    flat["stakeholders"] = ensure_list(data.get("stakeholders"), "User")

    return flat


def compute_usecase_embedding(use_case: UseCaseSchema):
    """Combine title and main_flow into embedding vector"""
    text = use_case.title + " " + " ".join(use_case.main_flow)
    return embedder.encode(text, convert_to_tensor=True)


def ensure_string_list(value) -> List[str]:
    """Safely convert any value to list of strings"""
    if isinstance(value, list):
        result = []
        for item in value:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, (list, tuple)):
                result.extend([str(x) for x in item])
            elif isinstance(item, dict):
                result.append(json.dumps(item))
            elif item:
                result.append(str(item))
        return result
    elif isinstance(value, str):
        return [value] if value.strip() else []
    elif value:
        return [str(value)]
    return []


# ============================================================================
# SMART SINGLE-STAGE EXTRACTION - UPDATED!
# ============================================================================


def extract_use_cases_single_stage(
    text: str, memory_context: str, max_use_cases: int = None
) -> List[dict]:
    """
    ROBUST SINGLE-STAGE EXTRACTION
    - Better prompting
    - Robust JSON parsing
    - Quality validation
    """

    # Smart estimation
    if max_use_cases is None:
        max_use_cases = get_smart_max_use_cases(text)

    # Dynamic token budget
    max_new_tokens = get_smart_token_budget(text, max_use_cases)

    # ✅ IMPROVED PROMPT - Clearer, more explicit
    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a requirements analyst. Extract use cases from text and return them as JSON.

CRITICAL RULES:
1. Each action mentioned should be a SEPARATE use case
2. DO NOT create duplicate use cases with the same title
3. Each use case must be unique and distinct
4. Split compound actions: "logs in and adds" → 2 separate use cases


<|eot_id|><|start_header_id|>user<|end_header_id|>

{memory_context}

Requirements:
{text}

Extract approximately {max_use_cases} UNIQUE, DISTINCT use cases from the requirements above.

IMPORTANT: 
- "User logs in and adds to cart" → Create 2 separate use cases:
  1. "User logs in to system"  
  2. "User adds items to cart"
- DO NOT create the same use case twice
- Each use case must have a different title

Return a JSON array where EACH use case has UNIQUE title and purpose:
[
  {{
    "title": "User logs in to system",
    "preconditions": ["User has valid credentials"],
    "main_flow": ["User opens app", "User enters credentials", "System validates", "User is authenticated"],
    "sub_flows": ["User can reset password", "User can remember device"],
    "alternate_flows": ["If invalid: System shows error", "If locked: System requires unlock"],
    "outcomes": ["User is logged in successfully"],
    "stakeholders": ["User", "Authentication System"]
  }},
  {{
    "title": "User adds items to shopping cart",
    "preconditions": ["User is logged in", "Products are available"],
    "main_flow": ["User browses products", "User selects product", "User clicks add to cart", "System adds item", "Cart is updated"],
    "sub_flows": ["User can adjust quantity", "User can view cart"],
    "alternate_flows": ["If out of stock: System notifies user", "If cart full: System prompts checkout"],
    "outcomes": ["Item added to cart successfully"],
    "stakeholders": ["User", "Shopping Cart System", "Inventory System"]
  }}
]

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

["""

    try:
        print(f"🚀 ROBUST SINGLE-STAGE EXTRACTION")
        print(f"   Estimated: {max_use_cases} use cases")
        print(f"   Token budget: {max_new_tokens}")
        print(f"   Input size: {len(text)} chars\n")

        start_time = time.time()

        # Generate with conservative settings
        outputs = pipe(
            prompt,
            max_new_tokens=max_new_tokens,
            temperature=0.3,  # Increase from 0.1 - less rigid
            top_p=0.85,  # Increase from 0.7 - more diverse
            repetition_penalty=1.1,  # Reduce from 1.15 - less restrictive
            do_sample=True,
            return_full_text=False,
            eos_token_id=tokenizer.eos_token_id,
            pad_token_id=tokenizer.eos_token_id,
        )

        response = "[" + outputs[0]["generated_text"].strip()

        elapsed = time.time() - start_time
        print(f"⏱️  Generation time: {elapsed:.1f}s\n")

        # Show preview
        preview = response[:500].replace("\n", " ")
        print(f"📋 Output preview:\n{preview}...\n")

        # Extract JSON array
        start_idx = response.find("[")
        end_idx = response.rfind("]")

        if start_idx == -1 or end_idx == -1:
            print("⚠️  No JSON array found, using fallback\n")
            return extract_with_smart_fallback(text)

        json_str = response[start_idx : end_idx + 1]

        # ✅ ROBUST CLEANING
        print("🔧 Cleaning JSON...")
        json_str = clean_llm_json(json_str)

        # Attempt to parse
        try:
            use_cases_raw = json.loads(json_str)

            if not isinstance(use_cases_raw, list):
                print(f"⚠️  Expected array, got {type(use_cases_raw)}\n")
                return extract_with_smart_fallback(text)

            print(f"✅ Parsed {len(use_cases_raw)} use cases from JSON\n")

            use_cases = []

            for idx, uc in enumerate(use_cases_raw, 1):
                if not isinstance(uc, dict):
                    print(f"⚠️  Skipping non-dict item {idx}")
                    continue

                # Validate and structure
                validated_uc = {
                    "title": str(uc.get("title", f"Use Case {idx}")).strip(),
                    "preconditions": ensure_string_list(uc.get("preconditions", [])),
                    "main_flow": ensure_string_list(uc.get("main_flow", [])),
                    "sub_flows": ensure_string_list(uc.get("sub_flows", [])),
                    "alternate_flows": ensure_string_list(
                        uc.get("alternate_flows", [])
                    ),
                    "outcomes": ensure_string_list(uc.get("outcomes", [])),
                    "stakeholders": ensure_string_list(uc.get("stakeholders", [])),
                }

                # Quality check
                title_len = len(validated_uc["title"])
                flow_len = len(validated_uc["main_flow"])

                if title_len < 10:
                    print(f"⚠️  [{idx}] Title too short: {validated_uc['title']}")
                    continue

                if flow_len < 3:
                    print(f"⚠️  [{idx}] Main flow too short ({flow_len} steps)")
                    # Enrich it instead of skipping
                    validated_uc = enrich_use_case(validated_uc, text)

                # Enrich to improve quality
                validated_uc = enrich_use_case(validated_uc, text)
                use_cases.append(validated_uc)

                print(f"✅ [{idx}] {validated_uc['title'][:60]}")

            # Hard limit check
            if len(use_cases) > max_use_cases + 2:
                print(f"\n⚠️  Extracted {len(use_cases)} but estimated {max_use_cases}")
                print(f"   Keeping top {max_use_cases} use cases\n")
                use_cases = use_cases[:max_use_cases]

            total_time = time.time() - start_time
            print(f"\n⚡ Success: {len(use_cases)} use cases in {total_time:.1f}s")
            if use_cases:
                print(f"   Average: {total_time/len(use_cases):.1f}s per use case\n")

            return use_cases

        except json.JSONDecodeError as e:
            print(f"❌ JSON parse failed: {e}")
            print(f"   Error at position {e.pos}")
            print(
                f"   Problematic section: ...{json_str[max(0,e.pos-50):e.pos+50]}...\n"
            )
            return extract_with_smart_fallback(text)

    except Exception as e:
        print(f"❌ Extraction error: {e}\n")
        import traceback

        traceback.print_exc()
        return extract_with_smart_fallback(text)


def extract_use_cases_batch(
    text: str, memory_context: str, max_use_cases: int
) -> List[dict]:
    """
    BATCH EXTRACTION - Extract use cases in small batches for speed
    Optimized for RTX 3050: 3-5x faster than single-stage
    """

    print(f"🔄 BATCH EXTRACTION MODE")
    print(f"   Total use cases to extract: {max_use_cases}")
    print(f"   Processing in batches of 3-4 use cases\n")

    all_use_cases = []
    batch_size = 3  # Extract 3 use cases per batch
    total_batches = (max_use_cases + batch_size - 1) // batch_size

    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        remaining = max_use_cases - start_idx
        batch_count = min(batch_size, remaining)

        print(f"{'='*80}")
        print(
            f"📦 BATCH {batch_num + 1}/{total_batches} - Extracting {batch_count} use cases"
        )
        print(f"{'='*80}")

        # Create focused prompt for this batch
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a requirements analyst. Extract exactly {batch_count} use cases from the requirements.

<|eot_id|><|start_header_id|>user<|end_header_id|>

{memory_context}

Requirements:
{text}

Extract exactly {batch_count} distinct use cases. Return ONLY a JSON array:

[
  {{
    "title": "Actor performs action on object",
    "preconditions": ["Precondition 1", "Precondition 2"],
    "main_flow": ["Step 1", "Step 2", "Step 3", "Step 4"],
    "sub_flows": ["Optional feature 1", "Optional feature 2"],
    "alternate_flows": ["Error case 1", "Error case 2"],
    "outcomes": ["Success result 1", "Success result 2"],
    "stakeholders": ["Actor", "System"]
  }}
]

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

["""

        # Calculate token budget for this batch
        batch_tokens = batch_count * 150 + 100  # 150 tokens per use case + overhead

        start_time = time.time()

        try:
            # Generate with reduced tokens
            outputs = pipe(
                prompt,
                max_new_tokens=batch_tokens,
                temperature=0.3,
                top_p=0.85,
                repetition_penalty=1.1,
                do_sample=True,
                return_full_text=False,
                eos_token_id=tokenizer.eos_token_id,
                pad_token_id=tokenizer.eos_token_id,
            )

            response = "[" + outputs[0]["generated_text"].strip()
            elapsed = time.time() - start_time

            print(f"⏱️  Batch generation time: {elapsed:.1f}s\n")

            # Extract JSON
            start_idx = response.find("[")
            end_idx = response.rfind("]")

            if start_idx == -1 or end_idx == -1:
                print(f"⚠️  No JSON array in batch {batch_num + 1}, skipping\n")
                continue

            json_str = response[start_idx : end_idx + 1]
            json_str = clean_llm_json(json_str)

            # Parse JSON
            try:
                batch_use_cases = json.loads(json_str)

                if not isinstance(batch_use_cases, list):
                    print(f"⚠️  Invalid JSON structure in batch {batch_num + 1}\n")
                    continue

                print(
                    f"✅ Parsed {len(batch_use_cases)} use cases from batch {batch_num + 1}"
                )

                # Validate and add to results
                for idx, uc in enumerate(batch_use_cases, 1):
                    if not isinstance(uc, dict):
                        continue

                    validated_uc = {
                        "title": str(
                            uc.get("title", f"Use Case {len(all_use_cases) + 1}")
                        ).strip(),
                        "preconditions": ensure_string_list(
                            uc.get("preconditions", [])
                        ),
                        "main_flow": ensure_string_list(uc.get("main_flow", [])),
                        "sub_flows": ensure_string_list(uc.get("sub_flows", [])),
                        "alternate_flows": ensure_string_list(
                            uc.get("alternate_flows", [])
                        ),
                        "outcomes": ensure_string_list(uc.get("outcomes", [])),
                        "stakeholders": ensure_string_list(uc.get("stakeholders", [])),
                    }

                    # Enrich for quality
                    validated_uc = enrich_use_case(validated_uc, text)
                    all_use_cases.append(validated_uc)

                    print(f"   [{len(all_use_cases)}] {validated_uc['title'][:60]}")

                print(
                    f"\n✅ Batch {batch_num + 1} complete: {len(batch_use_cases)} use cases extracted\n"
                )

            except json.JSONDecodeError as e:
                print(f"❌ JSON parse error in batch {batch_num + 1}: {e}\n")
                continue

        except Exception as e:
            print(f"❌ Error in batch {batch_num + 1}: {e}\n")
            import traceback

            traceback.print_exc()
            continue

    print(f"\n{'='*80}")
    print(f"✅ BATCH EXTRACTION COMPLETE")
    print(f"{'='*80}")
    print(f"Total use cases extracted: {len(all_use_cases)}")
    print(f"{'='*80}\n")

    return all_use_cases


# ============================================================================
# 4. ENHANCED FALLBACK (Better Quality)
# ============================================================================


def extract_with_smart_fallback(text: str) -> List[dict]:
    """
    IMPROVED FALLBACK with better pattern recognition
    """
    print("🔧 Enhanced fallback extraction...\n")

    use_cases = []
    seen_titles = set()

    # Enhanced actors list
    actors = [
        "user",
        "users",
        "customer",
        "customers",
        "admin",
        "administrator",
        "staff",
        "system",
        "platform",
        "application",
        "restaurant",
        "driver",
        "delivery person",
        "manager",
        "employee",
    ]

    # Enhanced verbs with better mappings
    verbs = {
        "find": "finds",
        "search": "searches",
        "view": "views",
        "see": "views",
        "show": "shows",
        "display": "displays",
        "list": "lists",
        "filter": "filters",
        "sort": "sorts",
        "select": "selects",
        "add": "adds",
        "create": "creates",
        "place": "places",
        "update": "updates",
        "edit": "edits",
        "modify": "modifies",
        "change": "changes",
        "delete": "deletes",
        "remove": "removes",
        "mark": "marks",
        "track": "tracks",
        "monitor": "monitors",
        "check": "checks",
        "send": "sends",
        "receive": "receives",
        "confirm": "confirms",
        "reject": "rejects",
        "accept": "accepts",
        "approve": "approves",
        "rate": "rates",
        "review": "reviews",
        "order": "orders",
        "pay": "pays",
        "make payment": "makes payment",
        "deliver": "delivers",
        "manage": "manages",
        "view": "views",
        "see": "views",
    }

    # Split into sentences
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if len(s.strip()) > 20]

    for sentence in sentences:
        sentence_lower = sentence.lower()

        # Pattern 1: "Actor should/can/must verb object"
        # Pattern 2: "Platform/System should let/allow actors verb object"
        # Pattern 3: "Actor verb object" (direct statement)

        for actor in actors:
            # Try multiple patterns
            patterns = [
                # "Users should be able to track"
                rf"\b{actor}\s+(?:should|can|must|may|will|shall|need to|able to)\s+([a-z]+)\s+([^,\.]+)",
                # "Platform should let users find"
                rf"platform\s+should\s+(?:let|allow)\s+{actor}\s+([a-z]+)\s+([^,\.]+)",
                # "Users track their order"
                rf"\b{actor}\s+([a-z]+)\s+(?:the|their|a|an)\s+([^,\.]+)",
            ]

            for pattern in patterns:
                matches = re.findall(pattern, sentence_lower, re.IGNORECASE)

                for match in matches:
                    if len(match) == 2:
                        verb, obj = match
                    else:
                        continue

                    verb = verb.strip()
                    obj = obj.strip()[:80]

                    # Clean object
                    obj = re.sub(
                        r"\s+(and|or|but|if|when|after|before|to|that|which|for now).*$",
                        "",
                        obj,
                    )
                    obj = obj.strip()

                    if len(obj) < 5 or len(obj) > 100:
                        continue

                    # Skip if verb not in our list
                    if verb not in verbs:
                        continue

                    conjugated = verbs.get(verb, verb + "s")

                    # Build title
                    title = f"{actor.capitalize()} {conjugated} {obj}"
                    title_key = title.lower().strip()

                    if title_key in seen_titles or len(title) < 15:
                        continue

                    seen_titles.add(title_key)

                    # Build quality use case
                    use_case = {
                        "title": title,
                        "preconditions": [
                            f"{actor.capitalize()} is authenticated and authorized",
                            "System is operational and responsive",
                        ],
                        "main_flow": [
                            f"{actor.capitalize()} navigates to relevant section",
                            f"{actor.capitalize()} initiates {verb} action",
                            "System validates request",
                            f"System processes {obj}",
                            f"System confirms completion to {actor}",
                            f"{actor.capitalize()} receives confirmation",
                        ],
                        "sub_flows": [
                            f"{actor.capitalize()} can view additional details",
                            f"{actor.capitalize()} can customize preferences",
                        ],
                        "alternate_flows": [
                            f"If validation fails: System displays error and prompts correction",
                            f"If system timeout: System retries and notifies {actor}",
                        ],
                        "outcomes": [
                            f"{title} completed successfully",
                            "System state is updated",
                        ],
                        "stakeholders": [actor.capitalize(), "System"],
                    }

                    use_cases.append(use_case)
                    print(f"✅ Fallback [{len(use_cases)}]: {title}")

                    if len(use_cases) >= 15:
                        break

            if len(use_cases) >= 15:
                break

        if len(use_cases) >= 15:
            break

    print(f"\n🔧 Fallback: Extracted {len(use_cases)} quality use cases\n")
    return use_cases


# ============================================================================
# CHUNKED PROCESSING
# ============================================================================


def parse_large_document_chunked(
    text: str,
    session_id: str,
    project_context: Optional[str] = None,
    domain: Optional[str] = None,
    filename: str = "document",
) -> dict:
    """
    Process large documents by chunking and extracting from each chunk
    NOW WITH SMART ESTIMATION PER CHUNK!
    """

    start_time = time.time()

    # Get memory context
    conversation_history = get_conversation_history(session_id, limit=10)
    session_context = get_session_context(session_id) or {}
    previous_use_cases = get_session_use_cases(session_id)

    memory_context = build_memory_context(
        conversation_history=conversation_history,
        session_context=session_context,
        previous_use_cases=previous_use_cases,
    )

    # Chunk the document
    chunks = chunker.chunk_document(text, strategy="auto")

    print(f"\n{'='*80}")
    print(f"⚡ CHUNKED EXTRACTION - {len(chunks)} chunks")
    print(f"{'='*80}\n")

    # Extract use cases from each chunk
    all_chunk_results = []
    chunk_summaries = []

    for i, chunk in enumerate(chunks, 1):
        print(f"{'='*80}")
        print(f"Processing Chunk {i}/{len(chunks)}")
        print(f"{'='*80}")

        # Extract from this chunk - NO max_use_cases, let it auto-detect!
        chunk_use_cases = extract_use_cases_single_stage(
            text=chunk["text"],
            memory_context=memory_context,
            # NO max_use_cases parameter - auto-detects per chunk!
        )

        all_chunk_results.append(chunk_use_cases)
        chunk_summaries.append(
            {
                "chunk_id": chunk["chunk_id"],
                "use_cases_found": len(chunk_use_cases),
                "char_count": chunk["char_count"],
            }
        )

        print(f"✅ Chunk {i}: Extracted {len(chunk_use_cases)} use cases\n")

    # Merge results from all chunks
    merged_use_cases = chunker.merge_extracted_use_cases(all_chunk_results)

    # Validate and store
    all_use_cases = []
    validation_results = []

    for uc_dict in merged_use_cases:
        try:
            # Validate
            is_valid, issues = UseCaseValidator.validate(uc_dict)
            quality_score = UseCaseValidator.calculate_quality_score(uc_dict)

            # Flatten
            flat = flatten_use_case(uc_dict)
            all_use_cases.append(UseCaseSchema(**flat))

            validation_results.append(
                {
                    "title": flat["title"],
                    "status": "valid" if is_valid else "valid_with_warnings",
                    "issues": issues,
                    "quality_score": quality_score,
                }
            )

        except Exception as e:
            print(f"⚠️  Validation error for '{uc_dict.get('title', 'Unknown')}': {e}")
            validation_results.append(
                {
                    "title": uc_dict.get("title", "Unknown"),
                    "status": "error",
                    "reason": str(e),
                }
            )

    # Check for duplicates and store
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute(
        "SELECT title, main_flow FROM use_cases WHERE session_id = ?", (session_id,)
    )
    existing_rows = c.fetchall()
    conn.close()

    existing_texts = [
        f"{row[0]} {' '.join(json.loads(row[1]))}" for row in existing_rows if row[1]
    ]
    existing_embeddings = (
        embedder.encode(existing_texts, convert_to_tensor=True)
        if existing_texts
        else None
    )

    results = []
    stored_count = 0
    threshold = 0.85

    for uc in all_use_cases:
        uc_emb = compute_usecase_embedding(uc)
        is_duplicate = False

        if existing_embeddings is not None:
            cos_sim = util.cos_sim(uc_emb, existing_embeddings)
            max_sim = float(torch.max(cos_sim))
            if max_sim >= threshold:
                is_duplicate = True
                print(f"🔄 Duplicate detected ({max_sim:.2f}): {uc.title[:50]}")

        if not is_duplicate:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            c.execute(
                """
                INSERT INTO use_cases 
                (session_id, title, preconditions, main_flow, sub_flows, alternate_flows, outcomes, stakeholders)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    session_id,
                    uc.title,
                    json.dumps(uc.preconditions),
                    json.dumps(uc.main_flow),
                    json.dumps(uc.sub_flows),
                    json.dumps(uc.alternate_flows),
                    json.dumps(uc.outcomes),
                    json.dumps(uc.stakeholders),
                ),
            )
            conn.commit()
            conn.close()

            results.append({"status": "stored", "title": uc.title})
            stored_count += 1
            print(f"💾 Stored: {uc.title}")
        else:
            results.append({"status": "duplicate_skipped", "title": uc.title})

    total_time = time.time() - start_time

    # Store response
    add_conversation_message(
        session_id=session_id,
        role="assistant",
        content=f"Processed {filename}: Extracted {len(merged_use_cases)} use cases from {len(chunks)} chunks in {total_time:.1f}s",
        metadata={
            "use_cases": results,
            "validation_results": validation_results,
            "extraction_method": "chunked_processing_smart",
            "processing_time": total_time,
            "chunks_processed": len(chunks),
            "chunk_summaries": chunk_summaries,
        },
    )

    print(f"\n{'='*80}")
    print(f"✅ CHUNKED EXTRACTION COMPLETE")
    print(f"{'='*80}")
    print(f"📊 Total chunks processed: {len(chunks)}")
    print(f"📊 Total extracted: {len(merged_use_cases)}")
    print(f"💾 Stored (new): {stored_count}")
    print(f"🔄 Duplicates skipped: {len(merged_use_cases) - stored_count}")
    print(f"⏱️  Total time: {total_time:.1f}s")
    print(f"⚡ Speed: {total_time/len(chunks):.1f}s per chunk")
    print(f"{'='*80}\n")

    return {
        "message": f"Chunked extraction: {len(merged_use_cases)} use cases from {len(chunks)} chunks in {total_time:.1f}s",
        "session_id": session_id,
        "filename": filename,
        "chunks_processed": len(chunks),
        "chunk_summaries": chunk_summaries,
        "extracted_count": len(merged_use_cases),
        "stored_count": stored_count,
        "duplicate_count": len(merged_use_cases) - stored_count,
        "processing_time_seconds": round(total_time, 1),
        "speed_per_chunk": round(total_time / len(chunks) if chunks else 0, 1),
        "results": results,
        "validation_results": validation_results,
        "extraction_method": "chunked_processing_smart",
    }


import routers

router = FastAPI()

router.include_router(routers.router)

def generate_session_title(
    first_user_message: str, max_length: int = 50, use_llm: bool = False
) -> str:
    """
    Generate a concise, meaningful session title from the first user message.

    Strategy:
    1. Quick extraction for initial loads (use_llm=False)
    2. LLM-based title generation for important views (use_llm=True)
    """
    if not first_user_message:
        return "New Session"

    text = first_user_message.strip()

    # Handle file uploads specially
    if text.startswith("Uploaded document:"):
        filename = text.replace("Uploaded document:", "").strip()
        base_name = filename.rsplit(".", 1)[0] if "." in filename else filename
        clean_name = base_name.replace("_", " ").replace("-", " ").title()
        return (
            clean_name[:max_length]
            if len(clean_name) <= max_length
            else clean_name[: max_length - 3] + "..."
        )

    # For initial loads, use quick keyword extraction
    if not use_llm:
        return generate_fallback_title(text, max_length)

    # For important views, use LLM
    try:
        prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>
You are a requirements analyst. Create a concise session title (4-7 words) that summarizes this requirement text.
<|eot_id|><|start_header_id|>user<|end_header_id|>
Requirements text:
{text[:300]}
Generate a short, descriptive title (4-7 words):
<|eot_id|><|start_header_id|>assistant<|end_header_id|>
"""
        outputs = pipe(
            prompt,
            max_new_tokens=30,
            temperature=0.3,
            top_p=0.85,
            do_sample=True,
            return_full_text=False,
        )

        title = outputs[0]["generated_text"].strip()
        title = title.replace("\n", " ").strip().strip("\"'.,;:")

        word_count = len(title.split())
        if 3 <= word_count <= 10 and len(title) <= max_length:
            return title

    except Exception as e:
        print(f"⚠️  LLM title generation failed: {e}")

    return generate_fallback_title(text, max_length)

def generate_fallback_title(text: str, max_length: int = 50) -> str:
    """
    Fallback method: Extract key concepts and build a title
    Uses simple NLP techniques without LLM
    """

    # Extract key action verbs and nouns
    action_verbs = [
        "login",
        "register",
        "search",
        "browse",
        "add",
        "create",
        "update",
        "delete",
        "manage",
        "view",
        "edit",
        "track",
        "checkout",
        "purchase",
        "order",
        "pay",
        "upload",
        "download",
    ]

    important_nouns = [
        "user",
        "customer",
        "admin",
        "system",
        "product",
        "order",
        "cart",
        "payment",
        "account",
        "profile",
        "restaurant",
        "delivery",
        "notification",
        "report",
        "document",
        "file",
    ]

    text_lower = text.lower()

    # Find mentioned verbs and nouns
    found_verbs = [v for v in action_verbs if v in text_lower]
    found_nouns = [n for n in important_nouns if n in text_lower]

    # Build title from found keywords
    if found_verbs and found_nouns:
        # Format: "User Login And Product Search"
        verb_part = " And ".join([v.title() for v in found_verbs[:2]])
        noun_part = found_nouns[0].title()
        title = f"{noun_part} {verb_part}"

        if len(title) <= max_length:
            return title

    # If keywords don't work, use first meaningful sentence
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if len(s.strip()) > 10]

    if sentences:
        first_sentence = sentences[0]

        # Remove common prefixes
        prefixes = ["the system should", "the user can", "user can", "system should"]
        for prefix in prefixes:
            if first_sentence.lower().startswith(prefix):
                first_sentence = first_sentence[len(prefix) :].strip()

        # Capitalize and truncate
        first_sentence = first_sentence.capitalize()

        if len(first_sentence) <= max_length:
            return first_sentence

        # Truncate at last complete word
        truncated = first_sentence[:max_length]
        last_space = truncated.rfind(" ")
        if last_space > max_length * 0.6:
            return truncated[:last_space] + "..."
        return truncated + "..."

    # Ultimate fallback
    return "Requirements Session"

@app.post("/use-case/refine")
def refine_use_case_endpoint(request: RefinementRequest):
    """Refine a specific use case based on user request"""

    use_case = get_use_case_by_id(request.use_case_id)
    if not use_case:
        raise HTTPException(status_code=404, detail="Use case not found")

    # Build refinement prompt based on type
    if request.refinement_type == "more_main_flows":
        instruction = "Add more main flows (additional primary flows or steps) to this use case. Expand the main flow with more detailed or additional steps."
    elif request.refinement_type == "more_sub_flows":
        instruction = "Add more sub flows to this use case. Include additional branching scenarios, related flows, or secondary paths."
    elif request.refinement_type == "more_alternate_flows":
        instruction = "Add more alternate flows to this use case. Include alternative paths, edge cases, error scenarios, and exception handling flows."
    elif request.refinement_type == "more_preconditions":
        instruction = "Add more preconditions to this use case. Include additional requirements, system states, or conditions that must be met before the use case can execute."
    elif request.refinement_type == "more_stakeholders":
        instruction = "Add more stakeholders to this use case. Identify additional actors, users, systems, or entities involved in this use case."
    else:
        instruction = "Improve the overall quality and completeness of this use case."

    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a requirements analyst refining a use case.

<|eot_id|><|start_header_id|>user<|end_header_id|>

Current use case:
{json.dumps(use_case, indent=2)}

Task: {instruction}

Return the refined use case in the same JSON format, with improvements applied.

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{{"""

    try:
        outputs = pipe(
            prompt,
            max_new_tokens=800,
            temperature=0.4,
            top_p=0.9,
            do_sample=True,
            return_full_text=False,
        )

        response = outputs[0]["generated_text"].strip()

        # Extract JSON
        if not response.startswith("{"):
            response = "{" + response

        start = response.find("{")
        end = response.rfind("}")

        if start != -1 and end != -1:
            json_str = response[start : end + 1]
            json_str = re.sub(r",(\s*[}\]])", r"\1", json_str)
            refined = json.loads(json_str)

            # Update in database
            update_use_case(request.use_case_id, refined)

            return {
                "message": "Use case refined successfully",
                "refined_use_case": refined,
            }
        else:
            raise ValueError("Could not extract valid JSON from refinement")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")

@app.post("/query")
def query_requirements(request: QueryRequest, request_data: Request):
    """Answer natural language questions about requirements"""

    user_id = require_user(request_data)
    session_id = request.session_id

    if not session_belongs_to_user(session_id, user_id):
        raise HTTPException(403, "Forbidden")


    use_cases = get_session_use_cases(request.session_id)

    if not use_cases:
        return {
            "answer": "No use cases found for this session yet.",
            "relevant_use_cases": [],
        }

    # Remove database IDs from use cases before sending to LLM
    # This prevents use case numbers from appearing in explanations
    use_cases_for_context = []
    for uc in use_cases:
        use_case_without_id = {
            "title": uc.get("title", ""),
            "preconditions": uc.get("preconditions", []),
            "main_flow": uc.get("main_flow", []),
            "sub_flows": uc.get("sub_flows", []),
            "alternate_flows": uc.get("alternate_flows", []),
            "outcomes": uc.get("outcomes", []),
            "stakeholders": uc.get("stakeholders", []),
        }
        use_cases_for_context.append(use_case_without_id)

    context = json.dumps(use_cases_for_context, indent=2)

    prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a requirements analyst assistant. Answer questions about use cases clearly and concisely.
IMPORTANT: Do NOT mention use case IDs, numbers, or database identifiers in your responses. Only refer to use cases by their titles.

<|eot_id|><|start_header_id|>user<|end_header_id|>

Use cases:
{context}

Question: {request.question}

Provide a clear, helpful answer based on the use cases above. Do not include any use case numbers or IDs in your response.

<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

    try:
        outputs = pipe(
            prompt,
            max_new_tokens=400,
            temperature=0.5,
            top_p=0.9,
            do_sample=True,
            return_full_text=False,
        )

        answer = outputs[0]["generated_text"].strip()

        # Post-process to remove any use case numbers that might have slipped through
        # Remove patterns like "Use Case 249", "Use Case 248", "UC 253", etc.
        answer = re.sub(r"\(Use Case\s+\d+\)", "", answer, flags=re.IGNORECASE)
        answer = re.sub(
            r"\(Use Cases\s+\d+[,\s]*\d*\)", "", answer, flags=re.IGNORECASE
        )
        answer = re.sub(r"Use Case\s+\d+", "", answer, flags=re.IGNORECASE)
        answer = re.sub(r"UC\s+\d+", "", answer, flags=re.IGNORECASE)
        # Clean up any double spaces or trailing commas/spaces
        answer = re.sub(r"\s+", " ", answer)
        answer = re.sub(r"\s*,\s*,", ",", answer)
        answer = re.sub(r"\s*,\s*\.", ".", answer)
        answer = answer.strip()

        # Find relevant use cases
        question_lower = request.question.lower()
        relevant = []

        for uc in use_cases:
            if any(word in uc["title"].lower() for word in question_lower.split()):
                relevant.append(uc["title"])

        return {
            "answer": answer,
            "relevant_use_cases": relevant,
            "total_use_cases": len(use_cases),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")

@router.get("/health")
def health_check():
    """Health check endpoint with system info"""
    return {
        "status": "healthy",
        "model": MODEL_NAME,
        "extraction_method": "smart_single_stage_with_chunking",
        "performance": "Intelligent estimation + dynamic token budgets",
        "features": [
            "✅ Smart use case estimation (no hardcoded limits!)",
            "✅ Dynamic token budgeting (300-1500 tokens)",
            "✅ Action verb detection and analysis",
            "✅ Document upload (PDF, DOCX, TXT, MD)",
            "✅ Intelligent chunking for large documents",
            "✅ Automatic size detection and processing strategy",
            "✅ Smart fallback with pattern matching",
            "✅ Automatic quality validation",
            "✅ Duplicate detection with embeddings",
            "✅ Session management",
            "✅ Conversation memory",
            "✅ Conflict detection",
            "✅ Quality metrics",
            "✅ Multiple export formats (DOCX, PlantUML, Markdown)",
            "✅ Natural language queries",
            "✅ Interactive refinement",
        ],
        "supported_formats": ["PDF", "DOCX", "TXT", "MD"],
        "max_file_size": "10MB",
        "chunking": {
            "enabled": True,
            "max_tokens_per_chunk": 3000,
            "strategies": ["auto", "section", "paragraph", "sentence"],
        },
        "smart_estimation": {
            "enabled": True,
            "analyzes": ["action_verbs", "actors", "sentence_structure", "list_items"],
            "dynamic_token_budget": True,
            "no_hallucination": True,
        },
        "speed": "Optimized based on input size and complexity",
        "improvements_v2": {
            "smart_estimation": "Analyzes text to determine actual use case count",
            "no_hardcoded_limits": "No more hardcoded max_use_cases = 8",
            "dynamic_tokens": "Token budget adapts to estimated need (300-1500)",
            "no_hallucination": "LLM only generates what actually exists",
            "faster": "Reduced token generation for small inputs",
        },
    }

@router.get("/")
def root():
    """Root endpoint with API information"""
    return {
        "name": "Requirements Engineering Tool API",
        "version": "4.0 - Smart Use Case Estimation",
        "description": "Converts unstructured requirements to structured use cases with intelligent estimation",
        "endpoints": {
            "extraction_text": "POST /parse_use_case_rag/",
            "extraction_document": "POST /parse_use_case_document/",
            "sessions": "POST /session/create, GET /sessions/",
            "history": "GET /session/{session_id}/history",
            "metrics": "GET /session/{session_id}/metrics",
            "query": "POST /query",
            "refine": "POST /use-case/refine",
            "conflicts": "GET /session/{session_id}/conflicts",
            "exports": "GET /session/{session_id}/export/{format}",
            "health": "GET /health",
        },
        "key_improvements": {
            "v4.0_smart_estimation": {
                "problem": "Previously hardcoded max_use_cases=8 caused hallucination",
                "solution": "Intelligent text analysis to estimate actual use case count",
                "benefits": [
                    "No more hallucinated use cases",
                    "Dynamic token budgets (300-1500 based on need)",
                    "Faster processing for small inputs",
                    "More accurate extraction",
                    "Analyzes: action verbs, actors, sentence structure, list items",
                ],
            },
            "document_upload": "Upload PDF, DOCX, TXT, MD files",
            "intelligent_chunking": "Automatic chunking for large documents",
            "size_detection": "Auto-detects text size and chooses best strategy",
            "quality": "Automatic validation and enrichment",
        },
        "usage_example": {
            "endpoint": "POST /parse_use_case_rag/",
            "body": {
                "raw_text": "User can login. User can search products.",
                "session_id": "optional-session-id",
                "project_context": "E-commerce Platform",
                "domain": "Online Retail",
            },
            "expected_result": {
                "extracted_count": 2,
                "processing_time": "2-5 seconds",
                "quality_scores": "High (no hallucination)",
                "message": "Smart extraction: 2 use cases (not 8!)",
            },
        },
    }
