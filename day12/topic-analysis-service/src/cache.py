import json
import time
from typing import Any, Optional, Dict
import structlog
import redis.asyncio as redis

logger = structlog.get_logger()

class CacheManager:
    """Redis-based cache manager for topic analysis results"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "errors": 0
        }
    
    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached value"""
        try:
            cached_data = await self.redis.get(key)
            if cached_data:
                self.stats["hits"] += 1
                logger.debug("Cache hit", key=key)
                return json.loads(cached_data)
            else:
                self.stats["misses"] += 1
                logger.debug("Cache miss", key=key)
                return None
        except Exception as e:
            self.stats["errors"] += 1
            logger.error("Cache get failed", key=key, error=str(e))
            return None
    
    async def set(self, key: str, value: Dict[str, Any], ttl: int = 3600) -> bool:
        """Set cached value with TTL"""
        try:
            serialized_value = json.dumps(value, default=str)
            await self.redis.setex(key, ttl, serialized_value)
            self.stats["sets"] += 1
            logger.debug("Cache set", key=key, ttl=ttl)
            return True
        except Exception as e:
            self.stats["errors"] += 1
            logger.error("Cache set failed", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete cached value"""
        try:
            result = await self.redis.delete(key)
            logger.debug("Cache delete", key=key, deleted=bool(result))
            return bool(result)
        except Exception as e:
            self.stats["errors"] += 1
            logger.error("Cache delete failed", key=key, error=str(e))
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Clear cache entries matching pattern"""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info("Cache pattern cleared", pattern=pattern, deleted=deleted)
                return deleted
            return 0
        except Exception as e:
            self.stats["errors"] += 1
            logger.error("Cache pattern clear failed", pattern=pattern, error=str(e))
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            info = await self.redis.info("memory")
            return {
                **self.stats,
                "memory_usage": info.get("used_memory_human", "Unknown"),
                "total_keys": await self.redis.dbsize(),
                "timestamp": time.time()
            }
        except Exception as e:
            logger.error("Failed to get cache stats", error=str(e))
            return self.stats
