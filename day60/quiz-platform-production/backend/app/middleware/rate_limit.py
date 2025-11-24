from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.redis_client import redis_client
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path.startswith("/health") or request.url.path == "/metrics":
            return await call_next(request)
        
        client_ip = request.client.host
        key = f"rate_limit:{client_ip}"
        
        try:
            current = await redis_client.get(key)
            if current and int(current) > 100:  # 100 requests per minute
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            pipe = redis_client.pipeline()
            pipe.incr(key)
            pipe.expire(key, 60)
            await pipe.execute()
        except Exception as e:
            # If Redis fails, allow request through (fail open)
            pass
        
        response = await call_next(request)
        return response
