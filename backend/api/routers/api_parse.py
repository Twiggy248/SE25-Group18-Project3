import json, sqlite3, time, uuid, torch
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, Request
from sentence_transformers import util

from ..security import require_user

from ...utilities.llm.hf_llm_util import getEmbedder
from ...database.managers import session_db_manager, usecase_db_manager
from ...utilities.document_parser import extract_text_from_file, get_text_stats, validate_file_size
from ...utilities.rag import build_memory_context
from ...use_case.use_case_validator import UseCaseValidator
from ...database.models import UseCaseSchema, InputText
from ...database.db import getDatabasePath
from ...managers.session_manager import generate_session_title
from ...managers.use_case_manager import get_smart_max_use_cases, extract_use_cases_batch, extract_use_cases_single_stage
from ...utilities.use_case_utilities import flatten_use_case, compute_usecase_embedding
from ...managers.parse_manager import parse_large_document_chunked

"""
api_parse.py
Handles any Parsing Use Case API Calls
"""

embedder = getEmbedder()

router = APIRouter(
    prefix="/parse_use_case_",
    tags=["parse_use_case_"],
)

@router.post("rag/")
def parse_use_case_fast(request: InputText, request_data: Request):
    """
    SMART EXTRACTION with intelligent use case estimation
    - Auto-detects number of use cases in text
    - Adapts token budget dynamically
    - No more hardcoded max_use_cases = 8!
    - Handles any size: tiny to very large
    """

    # NOTE: Why is a uuid being generated?
    session_id = request.session_id or str(uuid.uuid4())
    user_id = require_user(request_data)

    # Smart session handling
    existing_context = session_db_manager.get_session_context(session_id)

    if existing_context is None:
        # Generate a title for new session using LLM
        session_title = generate_session_title(request.raw_text, use_llm=True)

        # Session doesn't exist - create it with provided context and title
        session_db_manager.create_session(
            session_id=session_id,
            user_id=user_id,
            project_context=request.project_context or "",
            domain=request.domain or "",
            session_title=session_title)
        
    else:
        # Session exists - only update context if NEW values are provided
        # Don't update the session title if it already exists (prevents overwriting file upload titles)
        update_needed = False

        if request.project_context and request.project_context != existing_context.get("project_context"):
            update_needed = True

        if request.domain and request.domain != existing_context.get("domain"):
            update_needed = True

        if update_needed:
            session_db_manager.update_session_context(
                session_id=session_id,
                project_context=request.project_context or None,
                domain=request.domain or None) # Don't update session_title here to preserve file upload titles

    # Store user input in conversation history
    session_db_manager.add_conversation_message(session_id, "user", request.raw_text, {"type": "requirement_input"})

    # Check text size and decide processing strategy
    stats = get_text_stats(request.raw_text)

    # Decide processing strategy
    if stats["size_category"] in ["tiny", "small", "medium"]:
        # Small/medium text - process directly with smart estimation

        # Get memory context
        conversation_history = session_db_manager.get_conversation_history(session_id, limit=10)
        session_context = session_db_manager.get_session_context(session_id) or {}
        previous_use_cases = usecase_db_manager.get_use_case_by_session(session_id)

        memory_context = build_memory_context(conversation_history, session_context, previous_use_cases)

        start_time = time.time()

        # Get text stats and estimate
        max_use_cases_estimate = get_smart_max_use_cases(request.raw_text)

        # Choose extraction strategy based on size
        if stats["estimated_tokens"] > 300 and max_use_cases_estimate >= 4:
            use_cases_raw = extract_use_cases_batch(request.raw_text, memory_context, max_use_cases_estimate)
        else:
            use_cases_raw = extract_use_cases_single_stage(
                request.raw_text, memory_context
            )

        if not use_cases_raw:
            return {"message": "No use cases could be extracted",
                    "session_id": session_id,
                    "results": [],
                    "validation_results": []}

        # Validate and store
        all_use_cases = []
        validation_results = []

        for uc_dict in use_cases_raw:
            try:
                # Validate
                is_valid, issues = UseCaseValidator.validate(uc_dict)
                quality_score = UseCaseValidator.calculate_quality_score(uc_dict)

                # Flatten
                flat = flatten_use_case(uc_dict)
                all_use_cases.append(UseCaseSchema(**flat))

                validation_results.append(
                    {   "title": flat["title"],
                        "status": "valid" if is_valid else "valid_with_warnings",
                        "issues": issues,
                        "quality_score": quality_score})

            except Exception as e:
                validation_results.append(
                    {   "title": uc_dict.get("title", "Unknown"),
                        "status": "error",
                        "reason": str(e)})

        # Check for duplicates
        conn = sqlite3.connect(getDatabasePath())
        c = conn.cursor()
        c.execute("SELECT title, main_flow FROM use_cases WHERE session_id = ?", (session_id,))
        existing_rows = c.fetchall()
        conn.close()

        existing_texts = [
            f"{row[0]} {' '.join(json.loads(row[1]))}"
            for row in existing_rows
            if row[1]
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

            if not is_duplicate:
                conn = sqlite3.connect(getDatabasePath())
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
                    ))

                # Get the inserted ID
                use_case_id = c.lastrowid
                conn.commit()
                conn.close()

                # NEW CODE - Return FULL use case details
                results.append(
                    {"status": "stored",
                     "id": use_case_id,
                     "title": uc.title,
                     "preconditions": uc.preconditions,
                     "main_flow": uc.main_flow,
                     "sub_flows": uc.sub_flows,
                     "alternate_flows": uc.alternate_flows,
                     "outcomes": uc.outcomes,
                     "stakeholders": uc.stakeholders})
                stored_count += 1
            else:
                # NEW CODE - Return full details even for duplicates
                results.append(
                    {"status": "duplicate_skipped",
                     "title": uc.title,
                     "preconditions": uc.preconditions,
                     "main_flow": uc.main_flow,
                     "sub_flows": uc.sub_flows,
                     "alternate_flows": uc.alternate_flows,
                     "outcomes": uc.outcomes,
                     "stakeholders": uc.stakeholders})

        total_time = time.time() - start_time

        # Determine extraction method used
        extraction_method = (
            "batch_extraction" if max_use_cases_estimate >= 4 else "single_stage"
        )

        # Store response
        session_db_manager.add_conversation_message(
            session_id=session_id,
            role="assistant",
            content=f"Smart extraction: {len(use_cases_raw)} use cases in {total_time:.1f}s",
            metadata={"use_cases": results,
                     "validation_results": validation_results,
                     "extraction_method": extraction_method,
                     "processing_time": total_time})

        return {
            "message": f"Smart extraction: {len(use_cases_raw)} use cases in {total_time:.1f}s",
            "session_id": session_id,
            "extracted_count": len(use_cases_raw),
            "stored_count": stored_count,
            "duplicate_count": len(use_cases_raw) - stored_count,
            "processing_time_seconds": round(total_time, 1),
            "speed_per_use_case": round(
                total_time / len(use_cases_raw) if use_cases_raw else 0, 1
            ),
            "results": results,
            "validation_results": validation_results,
            "extraction_method": extraction_method,
        }

    else:
        # Large text - use chunked processing
        return parse_large_document_chunked(request.raw_text, session_id, request.project_context, request.domain, "text_input")


@router.post("document/")
async def parse_use_case_from_document(request: Request, file: UploadFile = File(...), session_id: Optional[str] = Form(None), project_context: Optional[str] = Form(None), domain: Optional[str] = Form(None)):
    """
    Extract use cases from uploaded document (PDF, DOCX, TXT, MD)
    Handles documents of any size with intelligent chunking and smart estimation
    """

    # Validate file size (10MB max)
    validate_file_size(file, max_size_mb=10)

    # Extract text from document
    # NOTE: Why is it catching an error then re-throwing an error?
    try:
        extracted_text, file_type = extract_text_from_file(file)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to extract text: {str(e)}")

    # Get text statistics
    stats = get_text_stats(extracted_text)

    # Create/get session - ENHANCED with better debugging
    # NOTE: Why is session id being generated by uuid if it doesn't exist???????
    if session_id is None:
        session_id = str(uuid.uuid4())

    # Check if session exists
    existing_context = session_db_manager.get_session_context(session_id)
    
    if existing_context is None:
        # Generate session title from extracted content (not just filename)
        session_title = generate_session_title(extracted_text, use_llm=True)
        
        session_db_manager.create_session(
            session_id=session_id,
            user_id=require_user(request),
            project_context=project_context or "",
            domain=domain or "",
            session_title=session_title)
    else:
        # EXISTING SESSION: Don't overwrite the session title or context         
        # Only update if new values provided
        if project_context or domain:
            session_db_manager.update_session_context(
                session_id=session_id,
                project_context=project_context,
                domain=domain) # CRITICAL: Don't update session_title here

    # Store document upload in conversation history
    session_db_manager.add_conversation_message(
        session_id=session_id,
        role="user",
        content=f"Uploaded document: {file.filename}",
        metadata={
            "type": "document_upload",
            "filename": file.filename,
            "file_type": file_type,
            "stats": stats,
        })

    # Process based on document size
    if stats["size_category"] in ["tiny", "small", "medium"]:
        # Small document - process directly with smart estimation

        # Use existing parsing logic
        request_data = InputText(
            raw_text=extracted_text,
            session_id=session_id,
            project_context=project_context,
            domain=domain,
        )

        return parse_use_case_fast(request_data)

    else:
        # Large document - use chunking with smart estimation per chunk
        return parse_large_document_chunked(extracted_text, session_id, project_context, domain, file.filename)
