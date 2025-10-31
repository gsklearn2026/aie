from fastapi import APIRouter, Depends
from ...cache.redis_client import get_redis_client

router = APIRouter(tags=["cache"])

@router.get("/stats")
async def get_cache_stats():
    """Get cache performance statistics"""
    redis_client = await get_redis_client()
    stats = await redis_client.get_stats()
    
    return {
        "cache_performance": stats,
        "recommendations": {
            "hit_rate": "Target: >75%",
            "memory_usage": "Monitor growth trends",
            "connections": "Keep under 20 for this demo"
        }
    }

@router.post("/flush")
async def flush_cache():
    """Flush all cache (use with caution)"""
    redis_client = await get_redis_client()
    if redis_client.redis:
        await redis_client.redis.flushall()
        return {"message": "Cache flushed successfully"}
    return {"error": "Redis not connected"}

@router.get("/keys/{pattern}")
async def list_cache_keys(pattern: str = "*"):
    """List cache keys matching pattern"""
    redis_client = await get_redis_client()
    if redis_client.redis:
        keys = await redis_client.redis.keys(pattern)
        return {"keys": keys[:50], "total": len(keys)}  # Limit to 50 for display
    return {"keys": [], "total": 0}
