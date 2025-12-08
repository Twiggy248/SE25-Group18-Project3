import sqlite3, json
from fastapi import APIRouter, Request

from ..security import require_user
from ...database.db import getDatabasePath
from ...database.models import UserPreferences

# API Calls for user start with /user and get routed here
router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@router.post("/preferences")
def save_user_preferences(preferences: UserPreferences, request: Request):
    """Save user theme preferences to database"""
    user_id = require_user(request)
    
    db = sqlite3.connect(getDatabasePath())
    c = db.cursor()
    
    # Store preferences as JSON
    preferences_json = json.dumps({
        "darkMode": preferences.darkMode,
        "stakeholderColorMode": preferences.stakeholderColorMode,
        "stakeholderColors": preferences.stakeholderColors
    })
    
    # Update or insert preferences
    c.execute("""
        UPDATE users 
        SET preferences = ?
        WHERE id = ?
    """, (preferences_json, user_id))
    
    db.commit()
    db.close()
    
    return {
        "success": True,
        "message": "Preferences saved successfully"
    }


@router.get("/preferences")
def get_user_preferences(request: Request):
    """Retrieve user theme preferences from database"""
    user_id = require_user(request)
    
    db = sqlite3.connect(getDatabasePath())
    c = db.cursor()
    
    c.execute("SELECT preferences FROM users WHERE id = ?", (user_id,))
    row = c.fetchone()
    db.close()
    
    if not row or not row[0]:
        # Return default preferences if none exist
        return {
            "darkMode": False,
            "stakeholderColorMode": False,
            "stakeholderColors": {
                'customer': 'blue',
                'admin': 'purple',
                'administrator': 'purple',
                'user': 'green',
                'system': 'orange',
                'application': 'orange',
                'platform': 'orange',
                'manager': 'red',
                'employee': 'teal',
                'staff': 'teal',
                'member': 'cyan',
                'visitor': 'gray',
                'guest': 'gray',
                'buyer': 'indigo',
                'seller': 'pink',
                'vendor': 'pink',
                'supplier': 'pink',
                'student': 'yellow',
                'teacher': 'indigo',
                'instructor': 'indigo',
                'patient': 'blue',
                'doctor': 'red',
                'nurse': 'teal'
            }
        }
    
    preferences = json.loads(row[0])
    return preferences
