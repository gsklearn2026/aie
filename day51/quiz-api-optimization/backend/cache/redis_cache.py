import redis.asyncio as redis
import json
import hashlib
from typing import Optional, Any
from backend.config.settings import settings

class CacheManager:
    def __init__(self):
        self.redis_client = None
        
    async def connect(self):
        self.redis_client = await redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True
        )
        
    async def disconnect(self):
        if self.redis_client:
            await self.redis_client.close()
            
    def _generate_key(self, prefix: str, **kwargs) -> str:
        key_data = json.dumps(kwargs, sort_keys=True)
        key_hash = hashlib.md5(key_data.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
        
    async def get(self, key: str) -> Optional[Any]:
        if not self.redis_client:
            return None
        try:
            value = await self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Cache get error: {e}")
            return None
            
    async def set(self, key: str, value: Any, ttl: int = None):
        if not self.redis_client:
            return
        try:
            ttl = ttl or settings.CACHE_TTL
            await self.redis_client.setex(
                key, 
                ttl, 
                json.dumps(value, default=str)
            )
        except Exception as e:
            print(f"Cache set error: {e}")
            
    async def delete(self, key: str):
        if self.redis_client:
            await self.redis_client.delete(key)
            
    async def get_stats(self) -> dict:
        if not self.redis_client:
            return {}
        try:
            info = await self.redis_client.info("stats")
            return {
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": self._calculate_hit_rate(info)
            }
        except:
            return {}
            
    def _calculate_hit_rate(self, info: dict) -> float:
        hits = info.get("keyspace_hits", 0)
        misses = info.get("keyspace_misses", 0)
        total = hits + misses
        return round((hits / total * 100) if total > 0 else 0, 2)

cache_manager = CacheManager()
