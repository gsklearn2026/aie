from fastapi import Request
import time
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware

class PerformanceMonitorMiddleware(BaseHTTPMiddleware):
    """Middleware to track API performance"""
    
    def __init__(self, app, stats=None):
        super().__init__(app)
        self.request_stats = stats["request_stats"] if stats else []
    
    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        
        # Log slow requests
        if duration > 0.5:  # 500ms threshold
            print(f"SLOW REQUEST: {request.method} {request.url.path} - {duration:.3f}s")
        
        # Store stats
        self.request_stats.append({
            'path': request.url.path,
            'method': request.method,
            'duration': duration,
            'timestamp': start_time
        })
        
        # Keep only last 1000 requests
        if len(self.request_stats) > 1000:
            self.request_stats[:] = self.request_stats[-1000:]
        
        # Add performance header
        response.headers["X-Response-Time"] = f"{duration:.3f}s"
        
        return response
    
    def get_stats(self):
        """Get performance statistics"""
        if not self.request_stats:
            return {
                'total_requests': 0,
                'avg_response_time': 0.0,
                'max_response_time': 0.0,
                'min_response_time': 0.0,
                'slow_requests': 0
            }
        
        durations = [r['duration'] for r in self.request_stats]
        return {
            'total_requests': len(self.request_stats),
            'avg_response_time': sum(durations) / len(durations),
            'max_response_time': max(durations),
            'min_response_time': min(durations),
            'slow_requests': len([d for d in durations if d > 0.5])
        }
