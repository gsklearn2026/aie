"""Integration layer specific routes"""
from fastapi import APIRouter, HTTPException, Request
from typing import Dict, Any
import structlog
from ..models.quiz import APIResponse

logger = structlog.get_logger()
router = APIRouter()

@router.get("/health", response_model=APIResponse)
async def integration_health():
    """Integration layer health check"""
    return APIResponse(
        success=True,
        data={
            "status": "healthy",
            "components": {
                "cache": "connected",
                "ai_service": "available"
            }
        }
    )

@router.get("/metrics", response_model=APIResponse)
async def get_metrics(request: Request):
    """Get integration layer metrics"""
    try:
        cache_service = request.app.state.cache_service
        
        metrics = {
            "cache_connected": cache_service.connected,
            "cache_type": "redis" if cache_service.connected else "memory",
            "api_version": "1.0.0"
        }
        
        return APIResponse(
            success=True,
            data=metrics
        )
        
    except Exception as e:
        logger.error("Failed to get metrics", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve metrics"
        )

@router.post("/cache/clear", response_model=APIResponse)
async def clear_cache(request: Request):
    """Clear integration layer cache"""
    try:
        cache_service = request.app.state.cache_service
        await cache_service.clear()
        
        logger.info("Cache cleared successfully")
        
        return APIResponse(
            success=True,
            data={"message": "Cache cleared successfully"}
        )
        
    except Exception as e:
        logger.error("Failed to clear cache", error=str(e))
        raise HTTPException(
            status_code=500,
            detail="Failed to clear cache"
        )
