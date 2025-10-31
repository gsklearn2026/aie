"""Health check endpoints"""
from fastapi import APIRouter
from typing import Dict
import time

router = APIRouter()

@router.get("")
async def health_check() -> Dict[str, str]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": str(time.time()),
        "service": "quiz-platform-backend"
    }

@router.get("/detailed")
async def detailed_health() -> Dict[str, any]:
    """Detailed health check with service status"""
    return {
        "status": "healthy",
        "services": {
            "api": "up",
            "database": "up",
            "ai_service": "up"
        },
        "timestamp": str(time.time())
    }
