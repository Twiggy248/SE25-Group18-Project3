"""
Security.py
Contains the functions that are used to ensure security and session management for the API
"""


import sqlite3
import database.db as database
from fastapi import Request, HTTPException



def session_belongs_to_user(session_id: str, user_id: str) -> bool:
    db = sqlite3.connect(database.get_db_path())
    c = db.cursor()
    c.execute("SELECT 1 FROM sessions WHERE session_id = ? AND user_id = ?", (session_id, user_id))
    row = c.fetchone()
    db.close()
    return row is not None


def require_user(request: Request) -> str:
    uid = request.cookies.get("user_id")
    if not uid: 
        raise HTTPException(401, "Not authenticated")
    return uid