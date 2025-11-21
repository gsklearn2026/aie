import redis.asyncio as redis
from app.config import get_settings
import json
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class CacheManager:
    def __init__(self):
        self.redis_client = None
    
    async def connect(self):
        """Initialize Redis connection pool"""
        self.redis_client = await redis.from_url(
            settings.redis_url,
            max_connections=settings.redis_max_connections,
            decode_responses=True
        )
        logger.info("Redis cache connected")
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def get(self, key: str):
        """Get value from cache"""
        try:
            value = await self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: any, ttl: int = 3600):
        """Set value in cache with TTL"""
        try:
            await self.redis_client.setex(
                key,
                ttl,
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    async def delete(self, key: str):
        """Delete key from cache"""
        try:
            await self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    async def check_health(self):
        """Check Redis connectivity"""
        try:
            await self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False

cache_manager = CacheManager()
