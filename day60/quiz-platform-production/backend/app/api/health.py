from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.utils.database import get_db
from app.utils.redis_client import redis_client
import google.generativeai as genai
import os
import time

router = APIRouter()

@router.get("/health")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": time.time()
    }

@router.get("/health/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Detailed readiness check - critical dependencies must be healthy"""
    health_status = {
        "status": "ready",
        "checks": {}
    }
    critical_failed = False
    
    # Check database (critical)
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "not_ready"
        critical_failed = True
    
    # Check Redis (critical)
    try:
        await redis_client.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "not_ready"
        critical_failed = True
    
    # Check Gemini AI (non-critical - service can work without it using fallback)
    # Since we have a fallback system, we always show as healthy
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            health_status["checks"]["gemini_ai"] = "healthy (fallback mode - no API key)"
            return health_status
        
        genai.configure(api_key=api_key)
        # Try gemini-pro first as it usually has better quota
        models_to_try = ['gemini-pro', 'gemini-1.5-pro', 'gemini-2.0-flash-exp']
        health_check_passed = False
        
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("test")
                health_status["checks"]["gemini_ai"] = f"healthy ({model_name})"
                health_check_passed = True
                break
            except Exception:
                # Continue trying other models
                continue
        
        if not health_check_passed:
            # Fallback system is available, so service is healthy
            health_status["checks"]["gemini_ai"] = "healthy (fallback mode)"
    except Exception:
        # Fallback system is available, so service is healthy
        health_status["checks"]["gemini_ai"] = "healthy (fallback mode)"
        # Don't mark as not_ready for Gemini failures
    
    # Only return 503 if critical services (DB/Redis) are down
    if critical_failed:
        raise HTTPException(status_code=503, detail=health_status)
    
    return health_status

@router.get("/health/live")
async def liveness_check():
    """Liveness check - is the service running"""
    return {"status": "alive", "timestamp": time.time()}
