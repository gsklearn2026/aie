import re
from typing import Dict, Any
from src.models.errors import ErrorType, ErrorSeverity, ErrorContext
import structlog

logger = structlog.get_logger()

class ErrorClassifier:
    def __init__(self):
        self.classification_rules = {
            # AI Service Errors
            r"rate.?limit|quota.?exceeded|too.?many.?requests": {
                "type": ErrorType.RATE_LIMIT_ERROR,
                "severity": ErrorSeverity.MEDIUM,
                "recoverable": True,
                "user_message": "AI service is busy. Please try again in a moment."
            },
            r"gemini|openai|anthropic.*unavailable|service.?unavailable": {
                "type": ErrorType.AI_SERVICE_ERROR,
                "severity": ErrorSeverity.HIGH,
                "recoverable": True,
                "user_message": "AI service is temporarily unavailable. Trying alternative approach."
            },
            
            # Authentication Errors
            r"unauthorized|invalid.?token|authentication.?failed": {
                "type": ErrorType.AUTHENTICATION_ERROR,
                "severity": ErrorSeverity.MEDIUM,
                "recoverable": False,
                "user_message": "Please log in again to continue."
            },
            
            # Validation Errors
            r"validation.?error|invalid.?input|bad.?request": {
                "type": ErrorType.VALIDATION_ERROR,
                "severity": ErrorSeverity.LOW,
                "recoverable": False,
                "user_message": "Please check your input and try again."
            },
            
            # Network Errors
            r"connection.?timeout|network.?error|dns.?resolution": {
                "type": ErrorType.NETWORK_ERROR,
                "severity": ErrorSeverity.MEDIUM,
                "recoverable": True,
                "user_message": "Network issue detected. Retrying automatically."
            }
        }
    
    def classify_error(self, error: Exception, context: Dict[str, Any] = None) -> ErrorContext:
        error_message = str(error).lower()
        
        # Default classification
        error_type = ErrorType.SERVER_ERROR
        severity = ErrorSeverity.HIGH
        recoverable = False
        user_message = "An unexpected error occurred. Our team has been notified."
        
        # Apply classification rules
        for pattern, rules in self.classification_rules.items():
            if re.search(pattern, error_message):
                error_type = rules["type"]
                severity = rules["severity"]
                recoverable = rules["recoverable"]
                user_message = rules["user_message"]
                break
        
        # HTTP status code based classification
        if hasattr(error, 'status_code'):
            if 400 <= error.status_code < 500:
                error_type = ErrorType.CLIENT_ERROR
                severity = ErrorSeverity.LOW
            elif error.status_code >= 500:
                error_type = ErrorType.SERVER_ERROR
                severity = ErrorSeverity.HIGH
        
        return ErrorContext.create(
            error_type=error_type,
            message=str(error),
            severity=severity,
            recoverable=recoverable,
            user_facing_message=user_message,
            details=context or {}
        )
