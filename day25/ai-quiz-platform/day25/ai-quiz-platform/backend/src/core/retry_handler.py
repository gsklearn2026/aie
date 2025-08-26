import asyncio
import random
from typing import Callable, Any, Type
from tenacity import (
    retry, stop_after_attempt, wait_exponential_jitter,
    retry_if_exception_type, before_sleep_log
)
from src.models.errors import ErrorType
import structlog

logger = structlog.get_logger()

class RetryHandler:
    @staticmethod
    def get_retry_decorator(error_type: ErrorType, max_attempts: int = 3):
        """Get appropriate retry decorator based on error type"""
        
        if error_type == ErrorType.RATE_LIMIT_ERROR:
            return retry(
                stop=stop_after_attempt(max_attempts),
                wait=wait_exponential_jitter(initial=1, max=60, jitter=10),
                retry=retry_if_exception_type((Exception,)),
                before_sleep=before_sleep_log(logger, "warning")
            )
        
        elif error_type == ErrorType.NETWORK_ERROR:
            return retry(
                stop=stop_after_attempt(max_attempts),
                wait=wait_exponential_jitter(initial=0.5, max=10),
                retry=retry_if_exception_type((Exception,)),
                before_sleep=before_sleep_log(logger, "info")
            )
        
        elif error_type == ErrorType.AI_SERVICE_ERROR:
            return retry(
                stop=stop_after_attempt(max_attempts),
                wait=wait_exponential_jitter(initial=2, max=30),
                retry=retry_if_exception_type((Exception,)),
                before_sleep=before_sleep_log(logger, "warning")
            )
        
        else:
            # No retry for client errors, auth errors, etc.
            return lambda func: func

    @staticmethod
    async def execute_with_retry(
        func: Callable,
        error_type: ErrorType,
        max_attempts: int = 3,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with appropriate retry logic"""
        
        if error_type in [ErrorType.CLIENT_ERROR, ErrorType.AUTHENTICATION_ERROR, ErrorType.VALIDATION_ERROR]:
            # No retry for these error types
            return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
        
        retry_decorator = RetryHandler.get_retry_decorator(error_type, max_attempts)
        
        if asyncio.iscoroutinefunction(func):
            @retry_decorator
            async def wrapped():
                return await func(*args, **kwargs)
            return await wrapped()
        else:
            @retry_decorator
            def wrapped():
                return func(*args, **kwargs)
            return wrapped()
