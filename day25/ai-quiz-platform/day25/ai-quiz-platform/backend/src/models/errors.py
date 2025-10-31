from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

class ErrorType(str, Enum):
    CLIENT_ERROR = "client_error"
    SERVER_ERROR = "server_error"
    AI_SERVICE_ERROR = "ai_service_error"
    BUSINESS_LOGIC_ERROR = "business_logic_error"
    AUTHENTICATION_ERROR = "authentication_error"
    VALIDATION_ERROR = "validation_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    NETWORK_ERROR = "network_error"

class ErrorSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CircuitBreakerState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class ErrorContext(BaseModel):
    error_id: str
    timestamp: datetime
    error_type: ErrorType
    severity: ErrorSeverity
    message: str
    details: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_path: Optional[str] = None
    correlation_id: Optional[str] = None
    retry_count: int = 0
    recoverable: bool = True
    user_facing_message: Optional[str] = None

    @classmethod
    def create(cls, error_type: ErrorType, message: str, **kwargs):
        return cls(
            error_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            error_type=error_type,
            message=message,
            **kwargs
        )

class ErrorResponse(BaseModel):
    success: bool = False
    error_id: str
    message: str
    details: Optional[Dict[str, Any]] = None
    retry_after: Optional[int] = None
