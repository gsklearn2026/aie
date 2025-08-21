from typing import Optional, Any, List, Dict, Callable
import structlog
from ..cache.redis_client import get_redis_client
from ..config.settings import get_settings

logger = structlog.get_logger()
settings = get_settings()

class CacheService:
    def __init__(self):
        self.redis_client = None
    
    async def _get_redis(self):
        if not self.redis_client:
            self.redis_client = await get_redis_client()
        return self.redis_client
    
    async def get_or_set(
        self, 
        key: str, 
        fetch_func: Callable, 
        ttl: int = None,
        *args, 
        **kwargs
    ) -> Any:
        """Cache-aside pattern implementation"""
        redis = await self._get_redis()
        
        # Try to get from cache first
        cached_value = await redis.get(key)
        if cached_value is not None:
            return cached_value
        
        # Cache miss - fetch from source
        fresh_value = await fetch_func(*args, **kwargs)
        
        # Set in cache for next time
        if fresh_value is not None:
            await redis.set(key, fresh_value, ttl)
        
        return fresh_value
    
    async def invalidate_quiz_cache(self, quiz_id: str):
        """Invalidate all cache entries related to a quiz"""
        redis = await self._get_redis()
        patterns = [
            f"quiz:{quiz_id}",
            f"quiz:{quiz_id}:*",
            f"user_progress:*:{quiz_id}",
            f"leaderboard:{quiz_id}:*"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            deleted = await redis.invalidate_pattern(pattern)
            total_deleted += deleted
        
        logger.info("Quiz cache invalidated", quiz_id=quiz_id, deleted_keys=total_deleted)
        return total_deleted
    
    async def cache_quiz(self, quiz_id: str, quiz_data: Dict) -> bool:
        """Cache quiz data with appropriate TTL"""
        redis = await self._get_redis()
        key = f"quiz:{quiz_id}"
        return await redis.set(key, quiz_data, settings.cache_quiz_ttl)
    
    async def cache_user_progress(self, user_id: str, quiz_id: str, progress_data: Dict) -> bool:
        """Cache user progress data"""
        redis = await self._get_redis()
        key = f"user_progress:{user_id}:{quiz_id}"
        return await redis.set(key, progress_data, settings.cache_user_progress_ttl)
    
    async def cache_leaderboard(self, quiz_id: str, leaderboard_data: List) -> bool:
        """Cache leaderboard data"""
        redis = await self._get_redis()
        key = f"leaderboard:{quiz_id}:top10"
        return await redis.set(key, leaderboard_data, settings.cache_leaderboard_ttl)
    
    async def cache_learning_path(self, user_id: str, path_data: Dict) -> bool:
        """Cache AI-generated learning path"""
        redis = await self._get_redis()
        key = f"learning_path:{user_id}"
        return await redis.set(key, path_data, settings.cache_learning_path_ttl)

# Global cache service instance
cache_service = CacheService()
