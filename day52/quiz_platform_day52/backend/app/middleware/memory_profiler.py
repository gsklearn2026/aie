from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
import tracemalloc
import psutil
import time
from typing import Callable
from app.services.memory_tracker import MemoryTracker

class MemoryProfilerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.tracker = MemoryTracker()
        tracemalloc.start()

    async def dispatch(self, request: Request, call_next: Callable):
        # Snapshot before request
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        snapshot_before = tracemalloc.take_snapshot()
        start_time = time.time()
        
        # Process request
        response = await call_next(request)
        
        # Snapshot after request
        snapshot_after = tracemalloc.take_snapshot()
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        duration = time.time() - start_time
        
        # Calculate diff
        memory_diff = memory_after - memory_before
        top_stats = snapshot_after.compare_to(snapshot_before, 'lineno')
        
        # Track metrics
        endpoint = f"{request.method} {request.url.path}"
        self.tracker.record_request(
            endpoint=endpoint,
            memory_before=memory_before,
            memory_after=memory_after,
            memory_diff=memory_diff,
            duration=duration,
            top_allocations=[(str(stat), stat.size_diff / 1024) for stat in top_stats[:5]]
        )
        
        # Add headers
        response.headers["X-Memory-Used-MB"] = f"{memory_after:.2f}"
        response.headers["X-Memory-Diff-MB"] = f"{memory_diff:.2f}"
        response.headers["X-Duration-MS"] = f"{duration * 1000:.2f}"
        
        return response
