import time
import uuid
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Dict, Any
import json

logger = structlog.get_logger()

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Extract user context
        user_id = request.headers.get("X-User-ID", "anonymous")
        session_id = request.headers.get("X-Session-ID", "unknown")
        
        # Start timer
        start_time = time.perf_counter()
        
        # Add context to request
        request.state.request_id = request_id
        request.state.user_id = user_id
        request.state.session_id = session_id
        
        # Log request start
        await self._log_request_start(request, request_id, user_id, session_id)
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate timing
            process_time = time.perf_counter() - start_time
            
            # Log request completion
            await self._log_request_complete(
                request, response, request_id, user_id, session_id, process_time
            )
            
            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.perf_counter() - start_time
            await self._log_request_error(
                request, e, request_id, user_id, session_id, process_time
            )
            raise
    
    async def _log_request_start(self, request: Request, request_id: str, 
                                user_id: str, session_id: str):
        logger.info(
            "Request started",
            event="request_start",
            request_id=request_id,
            user_id=user_id,
            session_id=session_id,
            method=request.method,
            url=str(request.url),
            user_agent=request.headers.get("User-Agent"),
            ip_address=request.client.host if request.client else None
        )
    
    async def _log_request_complete(self, request: Request, response: Response,
                                  request_id: str, user_id: str, session_id: str,
                                  process_time: float):
        logger.info(
            "Request completed",
            event="request_complete",
            request_id=request_id,
            user_id=user_id,
            session_id=session_id,
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time_ms=round(process_time * 1000, 2)
        )
    
    async def _log_request_error(self, request: Request, error: Exception,
                               request_id: str, user_id: str, session_id: str,
                               process_time: float):
        logger.error(
            "Request failed",
            event="request_error",
            request_id=request_id,
            user_id=user_id,
            session_id=session_id,
            method=request.method,
            url=str(request.url),
            error_type=type(error).__name__,
            error_message=str(error),
            process_time_ms=round(process_time * 1000, 2)
        )
