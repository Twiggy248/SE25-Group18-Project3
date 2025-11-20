import main
import json
import sqlite3
import time
from typing import Optional

import torch
from sentence_transformers import util
from backend.database.db import (add_conversation_message,
                get_conversation_history, get_db_path,
                get_session_context, get_session_use_cases)
from backend.utilities.rag import build_memory_context
from use_case.use_case_validator import UseCaseValidator
from backend.database.models import UseCaseSchema
from backend.utilities.use_case_utilities import compute_usecase_embedding, flatten_use_case
from use_case_manager import extract_use_cases_single_stage

def parse_large_document_chunked(text: str, session_id: str, project_context: Optional[str] = None, domain: Optional[str] = None, filename: str = "document") -> dict:
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
    chunks = main.chunker.chunk_document(text, strategy="auto")

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
    merged_use_cases = main.chunker.merge_extracted_use_cases(all_chunk_results)

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
        main.embedder.encode(existing_texts, convert_to_tensor=True)
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
