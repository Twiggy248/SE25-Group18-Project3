import sqlite3, json
from database.db import getDatabasePath
from typing import List, Dict, Optional

def create_session(session_id: str, user_id: str, project_context: str = "", domain: str = "", session_title: str = "New Session"):
    """Create a new session or update existing one"""
    conn = sqlite3.connect(getDatabasePath())
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO sessions (session_id, user_id, project_context, domain, user_preferences, session_title)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            last_active = CURRENT_TIMESTAMP
        """,
        (session_id, user_id, project_context, domain, json.dumps({}), session_title))

    conn.commit()
    conn.close()

def update_session_context(session_id: str, project_context: str = None, domain: str = None, preferences: dict = None, session_title: str = None):
    """Update session context as conversation progresses"""
    conn = sqlite3.connect(getDatabasePath())
    c = conn.cursor()

    updates = []
    params = []

    if project_context is not None:
        updates.append("project_context = ?")
        params.append(project_context)
    if domain is not None:
        updates.append("domain = ?")
        params.append(domain)
    if preferences is not None:
        updates.append("user_preferences = ?")
        params.append(json.dumps(preferences))
    if session_title is not None:
        updates.append("session_title = ?")
        params.append(session_title)

    if updates:
        updates.append("last_active = CURRENT_TIMESTAMP")
        params.append(session_id)

        query = f"UPDATE sessions SET {', '.join(updates)} WHERE session_id = ?"
        c.execute(query, params)
        conn.commit()

    conn.close()

def get_session_title(session_id: str) -> Optional[str]:
    """Get session title"""
    conn = sqlite3.connect(getDatabasePath())
    c = conn.cursor()

    c.execute(
        """
        SELECT session_title
        FROM sessions
        WHERE session_id = ?
    """,
        (session_id,),
    )

    row = c.fetchone()
    conn.close()

    if row:
        return row[0] or "New Session"
    return None

def get_session_context(session_id: str) -> Optional[Dict]:
    """Get accumulated context for a session"""
    conn = sqlite3.connect(getDatabasePath())
    c = conn.cursor()

    c.execute(
        """
        SELECT project_context, domain, user_preferences, session_title
        FROM sessions
        WHERE session_id = ?
    """,
        (session_id,),
    )

    row = c.fetchone()
    conn.close()

    if row:
        return {
            "project_context": row[0] or "",
            "domain": row[1] or "",
            "user_preferences": json.loads(row[2]) if row[2] else {},
            "session_title": row[3] or "New Session",
        }
    return None

def add_session_summary(session_id: str, summary: str, key_concepts: List[str]):
    """Add a summary of conversation progress"""
    conn = sqlite3.connect(getDatabasePath())
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO session_summaries (session_id, summary, key_concepts)
        VALUES (?, ?, ?)
        """,
        (session_id, summary, json.dumps(key_concepts)),
    )

    conn.commit()
    conn.close()

def get_latest_summary(session_id: str) -> Optional[Dict]:
    """Get the most recent summary for a session"""
    conn = sqlite3.connect(getDatabasePath())
    c = conn.cursor()

    c.execute(
        """
        SELECT summary, key_concepts, created_at
        FROM session_summaries
        WHERE session_id = ?
        ORDER BY created_at DESC
        LIMIT 1
        """,
        (session_id,),
    )

    row = c.fetchone()
    conn.close()

    if row:
        return {
            "summary": row[0],
            "key_concepts": json.loads(row[1]) if row[1] else [],
            "created_at": row[2],
        }
    return None

def clean_new_session_titles():
    """Remove 'New Session' titles and update with better defaults"""
    conn = sqlite3.connect(getDatabasePath())
    c = conn.cursor()

    try:
        # First, get all sessions with "New Session" title
        c.execute(
            """
            SELECT session_id, project_context, domain
            FROM sessions
            WHERE session_title = 'New Session' OR session_title IS NULL
            """
        )
        sessions = c.fetchall()

        for session in sessions:
            session_id, project_context, domain = session
            # Use project context or domain as title if available
            new_title = None
            if project_context:
                new_title = project_context
            elif domain:
                new_title = domain
            else:
                new_title = f"Session {session_id[:8]}"

            # Update the session title
            c.execute(
                """
                UPDATE sessions
                SET session_title = ?
                WHERE session_id = ?
                """,
                (new_title, session_id),
            )

        conn.commit()
        print(f"Updated {len(sessions)} session titles")
        return len(sessions)
    except Exception as e:
        print(f"Error cleaning session titles: {e}")
        conn.rollback()
        return 0
    finally:
        conn.close()

def add_conversation_message(session_id: str, role: str, content: str, metadata: dict = None):
    """Add a message to conversation history"""
    conn = sqlite3.connect(getDatabasePath())
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO conversation_history (session_id, role, content, metadata)
        VALUES (?, ?, ?, ?)
        """,
        (session_id, role, content, json.dumps(metadata or {})),
    )

    # Update session last_active
    c.execute(
        """
        UPDATE sessions SET last_active = CURRENT_TIMESTAMP WHERE session_id = ?
        """,
        (session_id,),
    )

    conn.commit()
    conn.close()

def get_conversation_history(session_id: str, limit: int = 10) -> List[Dict]:
    """Retrieve recent conversation history for a session"""
    conn = sqlite3.connect(getDatabasePath())
    conn.row_factory = sqlite3.Row  # Enable row factory for named columns
    c = conn.cursor()

    c.execute(
        """
        SELECT id, role, content, metadata, timestamp
        FROM conversation_history
        WHERE session_id = ?
        ORDER BY id ASC
        LIMIT ?
        """,
        (session_id, limit),
    )

    rows = c.fetchall()
    conn.close()

    return [
        {
            "id": row["id"],
            "role": row["role"],
            "content": row["content"],
            "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
            "timestamp": row["timestamp"],
        }
        for row in rows
    ]

def delete_session_by_id(session_id: str):
    conn = sqlite3.connect(getDatabasePath())
    c = conn.cursor()

    # Delete session data
    c.execute("DELETE FROM conversation_history WHERE session_id = ?", (session_id,))
    c.execute("DELETE FROM use_cases WHERE session_id = ?", (session_id,))
    c.execute("DELETE FROM session_summaries WHERE session_id = ?", (session_id,))
    c.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))

    conn.commit()
    conn.close()

def get_user_sessions(user_id: str) -> list:
    conn = sqlite3.connect(getDatabasePath())
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

    return rows