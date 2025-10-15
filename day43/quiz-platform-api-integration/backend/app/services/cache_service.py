"""Cache service with Redis backend"""
import json
import asyncio
from typing import Optional, Any, Dict
import redis.asyncio as redis
import structlog
from ..core.config import settings

logger = structlog.get_logger()

class CacheService:
    """Async Redis cache service"""
    
    def __init__(self):
        self.redis_client: Optional[redis.Redis] = None
        self.connected = False
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self.redis_client.ping()
            self.connected = True
            logger.info("Cache service connected to Redis")
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))
            # Use in-memory cache as fallback
            self._memory_cache: Dict[str, Any] = {}
            self.connected = False
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis_client:
            await self.redis_client.close()
            self.connected = False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if self.connected and self.redis_client:
                value = await self.redis_client.get(key)
                if value:
                    return json.loads(value)
            else:
                # Fallback to memory cache
                return self._memory_cache.get(key)
        except Exception as e:
            logger.warning("Cache get failed", key=key, error=str(e))
        return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        """Set value in cache"""
        try:
            serialized = json.dumps(value, default=str)
            if self.connected and self.redis_client:
                await self.redis_client.setex(
                    key, 
                    ttl or settings.CACHE_TTL, 
                    serialized
                )
            else:
                # Fallback to memory cache
                self._memory_cache[key] = value
                # Simple TTL simulation
                if ttl:
                    asyncio.create_task(self._expire_key(key, ttl))
            return True
        except Exception as e:
            logger.warning("Cache set failed", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key from cache"""
        try:
            if self.connected and self.redis_client:
                await self.redis_client.delete(key)
            else:
                self._memory_cache.pop(key, None)
            return True
        except Exception as e:
            logger.warning("Cache delete failed", key=key, error=str(e))
            return False
    
    async def clear(self) -> bool:
        """Clear all cache"""
        try:
            if self.connected and self.redis_client:
                await self.redis_client.flushdb()
            else:
                self._memory_cache.clear()
            return True
        except Exception as e:
            logger.warning("Cache clear failed", error=str(e))
            return False
    
    async def _expire_key(self, key: str, ttl: int):
        """Expire key after TTL (memory cache fallback)"""
        await asyncio.sleep(ttl)
        self._memory_cache.pop(key, None)
