import uuid
import sqlite3
from datetime import datetime
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from backend.database.db import (create_session, get_conversation_history, get_latest_summary,
                get_session_context, get_session_title, get_session_use_cases, 
                update_session_context, get_db_path)
from utilities.exports import export_to_docx, export_to_markdown
from backend.database.models import SessionRequest
from backend.api.router import require_user

router = APIRouter(
    prefix="/session",
    tags=["session"],
)

def session_belongs_to_user(session_id: str, user_id: str) -> bool:
    db = sqlite3.connect(get_db_path())
    c = db.cursor()
    c.execute("SELECT 1 FROM sessions WHERE session_id = ? AND user_id = ?", (session_id, user_id))
    row = c.fetchone()
    db.close()
    return row is not None


@router.post("/create")
def create_or_get_session(request: SessionRequest, request_obj: Request):
    """Create a new session or retrieve existing session info"""
    user_id = require_user(request_obj)
    session_id = request.session_id or str(uuid.uuid4())

    create_session(
        session_id=session_id,
        user_id=user_id,
        project_context=request.project_context or "",
        domain=request.domain or "",
    )

    return {
        "session_id": session_id,
        "context": get_session_context(session_id),
        "message": "Session created/retrieved successfully",
    }


@router.post("/update")
def update_session(request_data: SessionRequest, request: Request):
    """Update session context as conversation progresses"""
    user_id = require_user(request)

    if not request.session_id:
        raise HTTPException(status_code=400, detail="session_id is required")
    
    if not session_belongs_to_user(request_data.session_id, user_id):
        raise HTTPException(403, "Forbidden")

    update_session_context(
        session_id=request_data.session_id,
        project_context=request_data.project_context,
        domain=request_data.domain,
    )

    return {"message": "Session updated", "session_id": request_data.session_id}


@router.get("/{session_id}/title")
def get_session_title_endpoint(session_id: str, request:Request):
    """Get session title"""
    user_id = require_user(request)
    if not session_belongs_to_user(session_id, user_id):
        raise HTTPException(403, "Forbidden")

    title = get_session_title(session_id)
    if title is None:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"session_id": session_id, "session_title": title}


@router.get("/{session_id}/history")
def get_session_history(request: Request, session_id: str, limit: int = 10):
    """Get conversation history for a session"""
    user_id = require_user(request)
    if not session_belongs_to_user(session_id, user_id):
        raise HTTPException(403, "Forbidden")

    history = get_conversation_history(session_id, limit)
    context = get_session_context(session_id)
    use_cases = get_session_use_cases(session_id)
    summary = get_latest_summary(session_id)

    return {
        "session_id": session_id,
        "conversation_history": history,
        "session_context": context,
        "generated_use_cases": use_cases,
        "summary": summary,
    }

@router.get("s/")
def list_sessions(request: Request):
    """List all active sessions with stored titles"""
    user_id = require_user(request)
    
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()


    c.execute(
        """
        SELECT session_id, project_context, domain, session_title, created_at, last_active
        FROM sessions
        WHERE user_id = ?
        ORDER BY last_active DESC
    """, (user_id,)
    )

    rows = c.fetchall()
    conn.close()

    # Return sessions with stored titles
    sessions= []
    for row in rows:
        sessions.append(
            {
                "session_id": row[0],
                "session_title": row[3] or "New Session",
                "project_context": row[1] or "",
                "domain": row[2] or "",
                "created_at": row[4],
                "last_active": row[5],
            }
        )

    return {"sessions": sessions}


@router.get("/{session_id}/export")
def export_session(session_id: str, request: Request):
    """Export all session data for backup or analysis"""
    user_id = require_user(request)
    if not session_belongs_to_user(session_id, user_id):
        raise HTTPException(403, "Forbidden")

    conversation = get_conversation_history(session_id, limit=1000)
    context = get_session_context(session_id)
    use_cases = get_session_use_cases(session_id)
    summary = get_latest_summary(session_id)

    return {
        "session_id": session_id,
        "exported_at": str(datetime.now()),
        "session_context": context,
        "conversation_history": conversation,
        "use_cases": use_cases,
        "latest_summary": summary,
    }

@router.get("/{session_id}/export/docx")
def export_docx_endpoint(session_id: str, request: Request):
    """Export use cases to Word document"""

    user_id = require_user(request)
    if not session_belongs_to_user(session_id, user_id):
        raise HTTPException(403, "Forbidden")


    use_cases = get_session_use_cases(session_id)
    session_context = get_session_context(session_id)

    if not use_cases:
        raise HTTPException(
            status_code=404, detail="No use cases found for this session"
        )

    try:
        file_path = export_to_docx(use_cases, session_context, session_id)
        return FileResponse(
            file_path,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            filename=f"use_cases_{session_id}.docx",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/{session_id}/export/markdown")
def export_markdown_endpoint(session_id: str, request:Request):
    """Export as Markdown document"""

    user_id = require_user(request)
    if not session_belongs_to_user(session_id, user_id):
        raise HTTPException(403, "Forbidden")


    use_cases = get_session_use_cases(session_id)
    session_context = get_session_context(session_id)

    if not use_cases:
        raise HTTPException(
            status_code=404, detail="No use cases found for this session"
        )

    try:
        file_path = export_to_markdown(use_cases, session_context, session_id)
        return FileResponse(
            file_path, media_type="text/markdown", filename=f"use_cases_{session_id}.md"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.delete("/{session_id}")
def clear_session(session_id: str, request:Request):
    """Clear all data for a specific session"""
    user_id = require_user(request)
    if not session_belongs_to_user(session_id, user_id):
        raise HTTPException(403, "Forbidden")


    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Delete session data
    c.execute("DELETE FROM conversation_history WHERE session_id = ?", (session_id,))
    c.execute("DELETE FROM use_cases WHERE session_id = ?", (session_id,))
    c.execute("DELETE FROM session_summaries WHERE session_id = ?", (session_id,))
    c.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))

    conn.commit()
    conn.close()

    return {"message": f"Session {session_id} cleared successfully"}
