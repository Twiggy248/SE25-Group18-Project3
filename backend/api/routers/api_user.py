import os, requests, sqlite3
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse, JSONResponse 
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from database.db import db_path

# --- Google OAuth --- 
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8000/auth/callback"

# API Calls for user start with /user and get routed here
router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.get("/google")
def auth_google():
    """
    Login with a Google Account
    """
    url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        "?response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=openid%20email%20profile"
        "&access_type=offline"
        "&prompt=consent"
    )

    return RedirectResponse(url)

@router.get("/callback")
def auth_callback(code: str):
    """
    Authentication callback for logging in with Google
    """

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code, 
        "client_id": CLIENT_ID, 
        "client_secret": CLIENT_SECRET, 
        "redirect_uri": REDIRECT_URI, 
        "grant_type": "authorization_code"
    }

    token_res = requests.post(token_url, data=data).json()

    if "id_token" not in token_res: 
        raise HTTPException(status_code=400, detail="Invalid token exchange")
    
    #verifying Google ID token 
    try: 
        idinfo = id_token.verify_oauth2_token(
            token_res["id_token"], 
            google_requests.Request(), 
            CLIENT_ID
        )
    except Exception: 
        raise HTTPException(400, "Invalid ID token")
    
    google_sub = idinfo["sub"]
    email = idinfo.get("email")
    name = idinfo.get("name")
    picture = idinfo.get("picture")

    db = sqlite3.connect(db_path)
    c = db.cursor()

    c.execute("SELECT id FROM users WHERE id = ?", (google_sub, ))
    user = c.fetchone()

    if not user: 
        c.execute(
            "INSERT INTO users (id, email, name, picture) VALUES (?, ?, ?, ?)", 
            (google_sub, email, name, picture)
        )

        db.commit()
    
    db.close()

    #store user_id in session cookie 
    response = RedirectResponse(url="http://localhost:5173")
    response.set_cookie("user_id", google_sub, httponly=True)

    return response


@router.get("/me")
def auth_me(request: Request):
    """
    Get current user information
    """
    uid = request.cookies.get("user_id")

    if not uid: 
        return JSONResponse({"authenticated": False})
    
    db = sqlite3.connect(db_path)
    c = db.cursor()

    c.execute("SELECT id, email, name, picture FROM users WHERE id = ?", (uid,))
    user = c.fetchone()

    if not user: 
        return JSONResponse({"authenticated": False})
    
    return{
        "authenticated": True, 
        "id": user[0], 
        "email": user[1], 
        "name": user[2], 
        "picture": user[3],
    }

@router.post("/logout")
def logout_user(response: Response):
    """
    Logout current user
    """

    response.delete_cookie("user_id")
    return {"success": True}
