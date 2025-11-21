from fastapi import APIRouter, status
from app.database import check_db_health
from app.cache import cache_manager
import psutil
from datetime import datetime

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "quiz-platform"
    }

@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """Deep health check - verify all dependencies"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Check database
    db_healthy = await check_db_health()
    health_status["checks"]["database"] = "healthy" if db_healthy else "unhealthy"
    
    # Check cache
    cache_healthy = await cache_manager.check_health()
    health_status["checks"]["cache"] = "healthy" if cache_healthy else "unhealthy"
    
    # Check system resources
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    disk_percent = psutil.disk_usage('/').percent
    
    health_status["checks"]["resources"] = {
        "cpu_usage": f"{cpu_percent}%",
        "memory_usage": f"{memory_percent}%",
        "disk_usage": f"{disk_percent}%"
    }
    
    # Determine overall status
    if not (db_healthy and cache_healthy):
        health_status["status"] = "unhealthy"
        return health_status
    
    if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
        health_status["status"] = "degraded"
    
    return health_status

@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """Liveness check - is the service running"""
    return {"status": "alive"}
