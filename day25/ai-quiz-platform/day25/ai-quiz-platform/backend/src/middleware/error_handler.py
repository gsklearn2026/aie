from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from src.models.errors import ErrorResponse, ErrorType, ErrorSeverity
from src.services.error_classifier import ErrorClassifier
from src.core.circuit_breaker import CircuitBreaker
import structlog
import traceback
import time

logger = structlog.get_logger()

class GlobalErrorHandler(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.error_classifier = ErrorClassifier()
        self.circuit_breakers = {}
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            return response
            
        except Exception as error:
            # Log the error with context
            correlation_id = request.headers.get("x-correlation-id", "unknown")
            user_id = getattr(request.state, "user_id", None)
            
            error_context = self.error_classifier.classify_error(
                error,
                context={
                    "request_path": str(request.url),
                    "method": request.method,
                    "user_id": user_id,
                    "correlation_id": correlation_id,
                    "processing_time": time.time() - start_time
                }
            )
            
            # Log structured error
            logger.error(
                "Request failed",
                error_id=error_context.error_id,
                error_type=error_context.error_type,
                message=error_context.message,
                path=str(request.url),
                user_id=user_id,
                correlation_id=correlation_id,
                stack_trace=traceback.format_exc()
            )
            
            # Determine appropriate HTTP status code
            status_code = self._get_status_code(error_context.error_type)
            
            # Create user-friendly response
            error_response = ErrorResponse(
                error_id=error_context.error_id,
                message=error_context.user_facing_message or "An error occurred",
                details={
                    "type": error_context.error_type,
                    "recoverable": error_context.recoverable
                } if error_context.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL] else None
            )
            
            return JSONResponse(
                status_code=status_code,
                content=error_response.dict()
            )
    
    def _get_status_code(self, error_type: ErrorType) -> int:
        status_map = {
            ErrorType.CLIENT_ERROR: 400,
            ErrorType.AUTHENTICATION_ERROR: 401,
            ErrorType.VALIDATION_ERROR: 400,
            ErrorType.RATE_LIMIT_ERROR: 429,
            ErrorType.AI_SERVICE_ERROR: 503,
            ErrorType.NETWORK_ERROR: 503,
            ErrorType.SERVER_ERROR: 500,
            ErrorType.BUSINESS_LOGIC_ERROR: 422
        }
        return status_map.get(error_type, 500)

# Custom exception handlers
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error_id="validation_error",
            message="Invalid input data",
            details={"validation_errors": exc.errors()}
        ).dict()
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_id="http_error",
            message=exc.detail,
            details={"status_code": exc.status_code}
        ).dict()
    )
