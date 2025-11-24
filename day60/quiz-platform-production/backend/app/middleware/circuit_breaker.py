from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import time
from collections import defaultdict
from threading import Lock

class CircuitBreakerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, failure_threshold=5, timeout=30):
        super().__init__(app)
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failures = defaultdict(int)
        self.last_failure_time = defaultdict(float)
        self.circuit_open = defaultdict(bool)
        self.lock = Lock()
    
    async def dispatch(self, request: Request, call_next):
        endpoint = request.url.path
        
        # Check if circuit is open
        with self.lock:
            if self.circuit_open[endpoint]:
                if time.time() - self.last_failure_time[endpoint] > self.timeout:
                    # Try to close circuit (half-open state)
                    self.circuit_open[endpoint] = False
                    self.failures[endpoint] = 0
                else:
                    # Circuit still open
                    return JSONResponse(
                        status_code=503,
                        content={"detail": "Service temporarily unavailable - circuit breaker open"}
                    )
        
        try:
            response = await call_next(request)
            
            # Reset failure count on success
            if response.status_code < 500:
                with self.lock:
                    self.failures[endpoint] = 0
            else:
                self._record_failure(endpoint)
            
            return response
        except Exception as e:
            self._record_failure(endpoint)
            raise
    
    def _record_failure(self, endpoint):
        with self.lock:
            self.failures[endpoint] += 1
            self.last_failure_time[endpoint] = time.time()
            
            if self.failures[endpoint] >= self.failure_threshold:
                self.circuit_open[endpoint] = True
