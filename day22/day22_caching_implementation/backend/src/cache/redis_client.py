import redis.asyncio as redis
import json
import structlog
from typing import Optional, Any, Dict
from ..config.settings import get_settings

logger = structlog.get_logger()
settings = get_settings()

class RedisClient:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.hit_count = 0
        self.miss_count = 0
    
    async def connect(self):
        self.redis = redis.from_url(
            settings.redis_url,
            encoding="utf8",
            decode_responses=True,
            max_connections=20
        )
        await self.redis.ping()
        logger.info("Redis connected successfully")
    
    async def get(self, key: str) -> Optional[Any]:
        if not self.redis:
            await self.connect()
        
        try:
            value = await self.redis.get(key)
            if value:
                self.hit_count += 1
                logger.debug("Cache hit", key=key)
                return json.loads(value)
            else:
                self.miss_count += 1
                logger.debug("Cache miss", key=key)
                return None
        except Exception as e:
            logger.error("Redis get error", key=key, error=str(e))
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        if not self.redis:
            await self.connect()
        
        try:
            ttl = ttl or settings.cache_default_ttl
            await self.redis.setex(key, ttl, json.dumps(value, default=str))
            logger.debug("Cache set", key=key, ttl=ttl)
            return True
        except Exception as e:
            logger.error("Redis set error", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        if not self.redis:
            await self.connect()
        
        try:
            result = await self.redis.delete(key)
            logger.debug("Cache delete", key=key, deleted=bool(result))
            return bool(result)
        except Exception as e:
            logger.error("Redis delete error", key=key, error=str(e))
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        if not self.redis:
            await self.connect()
        
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info("Pattern invalidated", pattern=pattern, count=deleted)
                return deleted
            return 0
        except Exception as e:
            logger.error("Pattern invalidation error", pattern=pattern, error=str(e))
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        if not self.redis:
            await self.connect()
        
        info = await self.redis.info()
        hit_rate = self.hit_count / (self.hit_count + self.miss_count) if (self.hit_count + self.miss_count) > 0 else 0
        
        return {
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": f"{hit_rate:.2%}",
            "connected_clients": info.get("connected_clients", 0),
            "used_memory_human": info.get("used_memory_human", "0B"),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0)
        }

# Global redis client instance
_redis_client = RedisClient()

async def get_redis_client() -> RedisClient:
    if not _redis_client.redis:
        await _redis_client.connect()
    return _redis_client
