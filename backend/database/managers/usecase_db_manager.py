import sqlite3, json
from typing import List, Dict, Optional
from database.db import getDatabasePath

"""
usecase_db_manager.py
Handles any Database Operations involving Use Cases
"""

def get_use_case_by_session(session_id: str) -> List[Dict]:
    """Get all use cases generated in this session"""
    conn = sqlite3.connect(getDatabasePath())
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
    conn = sqlite3.connect(getDatabasePath())
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
    conn = sqlite3.connect(getDatabasePath())
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
