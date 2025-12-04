# -----------------------------------------------------------------------------
# File: db.py
# Description: Database operations and session management for ReqEngine -
#              handles SQLite database interactions, session CRUD operations.
# Author: Pradyumna Chacham, Caleb Twigg
# Date: November 2025
# -----------------------------------------------------------------------------

import os
import sqlite3

db_path = os.path.join(os.path.dirname(__file__), "requirements.db")

def migrate_db(reset: bool = False):
    """
    Handle database migrations. If reset=True, drop and recreate tables.
    """

    # Optionally reset database
    if reset:
        try:
            os.remove(db_path)
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
            """)

        # Check if session_title column exists
        try:
            c.execute("SELECT session_title FROM sessions LIMIT 1")
        except sqlite3.OperationalError:
            c.execute("ALTER TABLE sessions ADD COLUMN session_title TEXT")

        # Check if user_id column exists 
        try: 
            c.execute("SELECT user_id FROM sessions LIMIT 1")
        except sqlite3.OperationalError: 
            c.execute("ALTER TABLE sessions ADD COLUMN user_id TEXT")

        try:
            c.execute("SELECT preferences FROM users LIMIT 1")
        except sqlite3.OperationalError:
            c.execute("ALTER TABLE users ADD COLUMN preferences TEXT")

        # Update existing NULL session_title values
        c.execute(
            """
            UPDATE sessions 
            SET session_title = 'New Session' 
            WHERE session_title IS NULL
            """)

        conn.commit()

    except Exception as e:
        conn.rollback()
    finally:
        conn.close()

def init_db():
    """Initialize database with use_cases, sessions, and conversation_history tables"""
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
        """)

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
        """)

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
        """)

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
        """)

    # Create indexes for faster lookups
    c.execute("CREATE INDEX IF NOT EXISTS idx_use_cases_session_id ON use_cases(session_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_use_cases_title ON use_cases(title)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_conversation_session_id ON conversation_history(session_id)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_conversation_timestamp ON conversation_history(timestamp)")
    c.execute("CREATE INDEX IF NOT EXISTS idx_summaries_session_id ON session_summaries(session_id)")

    # Users Table 

    c.execute("""
              CREATE TABLE IF NOT EXISTS users (
              id TEXT PRIMARY KEY, 
              email TEXT UNIQUE,
              name TEXT, 
              picture TEXT,
              preferences TEXT
              )
              """)

    conn.commit()
    conn.close()

def setDatabasePath(new_path: str):
    global db_path
    db_path = new_path

def getDatabasePath() -> str:
    return db_path