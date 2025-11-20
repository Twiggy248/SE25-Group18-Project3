from fastapi import FastAPI, Request, HTTPException
from api_routers import api_session, api_user

app = FastAPI()

app.include_router(api_session.router)
app.include_router(api_user.router)

def require_user(request: Request) -> str:
    uid = request.cookies.get("user_id")
    if not uid: 
        raise HTTPException(401, "Not authenticated")
    return uid
