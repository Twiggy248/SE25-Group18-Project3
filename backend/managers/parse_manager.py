import json, time, sqlite3, torch
from typing import Optional

from sentence_transformers import util
from utilities.rag import build_memory_context
from use_case.use_case_validator import UseCaseValidator
from database.models import UseCaseSchema
from database.db import getDatabasePath
from database.managers import session_db_manager, usecase_db_manager
from utilities.use_case_utilities import compute_usecase_embedding, flatten_use_case
from managers.use_case_manager import extract_use_cases_single_stage
from utilities.chunking_strategy import DocumentChunker
from backend.utilities.llm.hf_llm_util import getEmbedder


embedder = getEmbedder()


# NOTE: Why Import project_context or domain if never used?
def parse_large_document_chunked(text: str, session_id: str, project_context: Optional[str] = None, domain: Optional[str] = None, filename: str = "document") -> dict:
    """
    Process large documents by chunking and extracting from each chunk
    NOW WITH SMART ESTIMATION PER CHUNK!
    """

    start_time = time.time()

    # Get memory context
    conversation_history = session_db_manager.get_conversation_history(session_id, limit=10)
    session_context = session_db_manager.get_session_context(session_id) or {}
    previous_use_cases = usecase_db_manager.get_use_case_by_session(session_id)

    memory_context = build_memory_context(
        conversation_history=conversation_history,
        session_context=session_context,
        previous_use_cases=previous_use_cases,
    )

    # Chunk the document
    chunks = DocumentChunker.chunk_document(text, strategy="auto")

    # Extract use cases from each chunk
    all_chunk_results = []
    chunk_summaries = []

    for i, chunk in enumerate(chunks, 1):

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

    # Merge results from all chunks
    merged_use_cases = DocumentChunker.merge_extracted_use_cases(all_chunk_results)

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
            validation_results.append(
                {
                    "title": uc_dict.get("title", "Unknown"),
                    "status": "error",
                    "reason": str(e),
                }
            )

    # Check for duplicates and store
    conn = sqlite3.connect(getDatabasePath())
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
                ),
            )
            conn.commit()
            conn.close()

            results.append({"status": "stored", "title": uc.title})
            stored_count += 1
        else:
            results.append({"status": "duplicate_skipped", "title": uc.title})

    total_time = time.time() - start_time

    # Store response
    session_db_manager.add_conversation_message(
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
