from functools import wraps
from backend.cache.redis_cache import cache_manager
import json

def cache_response(ttl: int = None, key_prefix: str = "api"):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_manager._generate_key(
                key_prefix, 
                func=func.__name__, 
                args=str(args), 
                kwargs=str(kwargs)
            )
            
            # Try to get from cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
                
            # Execute function
            result = await func(*args, **kwargs)
            
            # Store in cache
            await cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator
