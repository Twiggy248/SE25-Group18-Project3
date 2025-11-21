# -----------------------------------------------------------------------------
# File: db.py
# Description: Database operations and session management for ReqEngine -
#              handles SQLite database interactions, session CRUD operations.
# Author: Pradyumna Chacham
# Date: November 2025
# Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
# License: MIT License - see LICENSE file in the root directory.
# -----------------------------------------------------------------------------

import json
import os
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional


def get_db_path():
    return os.path.join(os.path.dirname(__file__), "requirements.db")


def migrate_db(reset: bool = False):
    """
    Handle database migrations. If reset=True, drop and recreate tables.
    """
    db_path = get_db_path()

    # Optionally reset database
    if reset:
        try:
            os.remove(db_path)
            print(f"Removed existing database: {db_path}")
        except FileNotFoundError:
            pass
        init_db()  # Recreate tables
        return

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    try:
        # Ensure sessions table exists
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT,
                project_context TEXT,
                domain TEXT,
                user_preferences TEXT,
                session_title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Check if session_title column exists
        try:
            c.execute("SELECT session_title FROM sessions LIMIT 1")
        except sqlite3.OperationalError:
            print("Adding session_title column to sessions table...")
            c.execute("ALTER TABLE sessions ADD COLUMN session_title TEXT")

        # Check if user_id column exists 
        try: 
            c.execute("SELECT user_id FROM sessions LIMIT 1")
        except sqlite3.OperationalError: 
            print("Adding user_id column to sessions table...")
            c.execute("ALTER TABLE sessions ADD COLUMN user_id TEXT")
        
        try:
            c.execute("SELECT preferences FROM users LIMIT 1")
        except sqlite3.OperationalError:
            print("Adding preferences column to users table...")
            c.execute("ALTER TABLE users ADD COLUMN preferences TEXT")

        # Update existing NULL session_title values
        c.execute(
            """
            UPDATE sessions 
            SET session_title = 'New Session' 
            WHERE session_title IS NULL
        """
        )

        conn.commit()
        print("Database migration completed successfully")

    except Exception as e:
        print(f"Migration error: {str(e)}")
        conn.rollback()
    finally:
        conn.close()


def init_db():
    """Initialize database with use_cases, sessions, and conversation_history tables"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Enable WAL mode for better concurrency and performance
    c.execute("PRAGMA journal_mode=WAL")
    c.execute("PRAGMA synchronous=NORMAL")
    c.execute("PRAGMA cache_size=10000")
    c.execute("PRAGMA temp_store=MEMORY")

    # Original use_cases table with session_id
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS use_cases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            title TEXT NOT NULL,
            preconditions TEXT,
            main_flow TEXT,
            sub_flows TEXT,
            alternate_flows TEXT,
            outcomes TEXT,
            stakeholders TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Sessions table - tracks each chat window/session
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            user_id TEXT,
            project_context TEXT,
            domain TEXT,
            user_preferences TEXT,
            session_title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )

    # Conversation history table - stores all interactions
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS conversation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            metadata TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    """
    )

    # Session summaries - periodic summaries of long conversations
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS session_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            summary TEXT NOT NULL,
            key_concepts TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    """
    )

    # Create indexes for faster lookups
    c.execute(
        "CREATE INDEX IF NOT EXISTS idx_use_cases_session_id ON use_cases(session_id)"
    )
    c.execute("CREATE INDEX IF NOT EXISTS idx_use_cases_title ON use_cases(title)")
    c.execute(
        "CREATE INDEX IF NOT EXISTS idx_conversation_session_id ON conversation_history(session_id)"
    )
    c.execute(
        "CREATE INDEX IF NOT EXISTS idx_conversation_timestamp ON conversation_history(timestamp)"
    )
    c.execute(
        "CREATE INDEX IF NOT EXISTS idx_summaries_session_id ON session_summaries(session_id)"
    )

    # Users Table 

    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY, 
            email TEXT UNIQUE,
            name TEXT, 
            picture TEXT,
            preferences TEXT
        )
    """
    )

    conn.commit()
    conn.close()


def create_session(
    session_id: str,
    user_id: str,
    project_context: str = "",
    domain: str = "",
    session_title: str = "New Session",
):
    """Create a new session or update existing one"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute(
        """
        INSERT INTO sessions (session_id, user_id, project_context, domain, user_preferences, session_title)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(session_id) DO UPDATE SET
            last_active = CURRENT_TIMESTAMP
    """,
        (session_id, user_id, project_context, domain, json.dumps({}), session_title),
    )

    conn.commit()
    conn.close()


def update_session_context(
    session_id: str,
    project_context: str = None,
    domain: str = None,
    preferences: dict = None,
    session_title: str = None,
):
    """Update session context as conversation progresses"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
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


def add_conversation_message(
    session_id: str, role: str, content: str, metadata: dict = None
):
    """Add a message to conversation history"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
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
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
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


def get_session_title(session_id: str) -> Optional[str]:
    """Get session title"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
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
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
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


def get_session_use_cases(session_id: str) -> List[Dict]:
    """Get all use cases generated in this session"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute(
        """
        SELECT id, title, preconditions, main_flow, sub_flows, 
               alternate_flows, outcomes, stakeholders
        FROM use_cases
        WHERE session_id = ?
        ORDER BY created_at DESC
    """,
        (session_id,),
    )

    rows = c.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "title": row[1],
            "preconditions": json.loads(row[2]) if row[2] else [],
            "main_flow": json.loads(row[3]) if row[3] else [],
            "sub_flows": json.loads(row[4]) if row[4] else [],
            "alternate_flows": json.loads(row[5]) if row[5] else [],
            "outcomes": json.loads(row[6]) if row[6] else [],
            "stakeholders": json.loads(row[7]) if row[7] else [],
        }
        for row in rows
    ]


def get_use_case_by_id(use_case_id: int) -> Optional[Dict]:
    """Get a specific use case by ID"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    c.execute(
        """
        SELECT id, session_id, title, preconditions, main_flow, sub_flows,
               alternate_flows, outcomes, stakeholders
        FROM use_cases
        WHERE id = ?
    """,
        (use_case_id,),
    )

    row = c.fetchone()
    conn.close()

    if row:
        return {
            "id": row[0],
            "session_id": row[1],
            "title": row[2],
            "preconditions": json.loads(row[3]) if row[3] else [],
            "main_flow": json.loads(row[4]) if row[4] else [],
            "sub_flows": json.loads(row[5]) if row[5] else [],
            "alternate_flows": json.loads(row[6]) if row[6] else [],
            "outcomes": json.loads(row[7]) if row[7] else [],
            "stakeholders": json.loads(row[8]) if row[8] else [],
        }
    return None


def update_use_case(use_case_id: int, updated_data: Dict) -> bool:
    """Update a use case with new data"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # First check if the use case exists
    c.execute("SELECT COUNT(*) FROM use_cases WHERE id = ?", (use_case_id,))
    count = c.fetchone()[0]

    if count == 0:
        conn.close()
        return False

    try:
        c.execute(
            """
            UPDATE use_cases
            SET title = ?,
                preconditions = ?,
                main_flow = ?,
                sub_flows = ?,
                alternate_flows = ?,
                outcomes = ?,
                stakeholders = ?
            WHERE id = ?
        """,
            (
                updated_data.get("title", ""),
                json.dumps(updated_data.get("preconditions", [])),
                json.dumps(updated_data.get("main_flow", [])),
                json.dumps(updated_data.get("sub_flows", [])),
                json.dumps(updated_data.get("alternate_flows", [])),
                json.dumps(updated_data.get("outcomes", [])),
                json.dumps(updated_data.get("stakeholders", [])),
                use_case_id,
            ),
        )
        conn.commit()
        conn.close()
        return c.rowcount > 0
    except Exception as e:
        conn.close()
        print(f"Error updating use case: {e}")
        return False


def add_session_summary(session_id: str, summary: str, key_concepts: List[str]):
    """Add a summary of conversation progress"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
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
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
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
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
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
