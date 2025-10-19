from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import google.generativeai as genai
import os

from ..core.database import get_db
from ..core.security import verify_token

router = APIRouter()
security = HTTPBearer()

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY", "your-gemini-api-key"))

async def get_current_user_from_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload

@router.get("/protected-test")
async def protected_endpoint(current_user = Depends(get_current_user_from_token)):
    return {
        "message": "This is a protected endpoint",
        "user_id": current_user.get("user_id"),
        "username": current_user.get("sub"),
        "role": current_user.get("role")
    }
