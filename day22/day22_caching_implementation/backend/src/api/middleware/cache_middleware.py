from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time
import structlog

logger = structlog.get_logger()

class CacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Add cache headers for static content
        response = await call_next(request)
        
        # Add timing header
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Add cache-related headers
        if request.url.path.startswith("/api/v1/quiz/"):
            response.headers["X-Cache-Strategy"] = "cache-aside"
            response.headers["Cache-Control"] = "public, max-age=300"  # 5 minutes browser cache
        
        return response
