import pytest
import asyncio
from unittest.mock import Mock, patch
from src.services.error_classifier import ErrorClassifier
from src.core.circuit_breaker import CircuitBreaker
from src.core.retry_handler import RetryHandler
from src.models.errors import ErrorType, ErrorSeverity

class TestErrorClassifier:
    def setup_method(self):
        self.classifier = ErrorClassifier()
    
    def test_rate_limit_classification(self):
        error = Exception("Rate limit exceeded")
        context = self.classifier.classify_error(error)
        
        assert context.error_type == ErrorType.RATE_LIMIT_ERROR
        assert context.severity == ErrorSeverity.MEDIUM
        assert context.recoverable == True
        assert "AI service is busy" in context.user_facing_message
    
    def test_authentication_error_classification(self):
        error = Exception("Authentication failed")
        context = self.classifier.classify_error(error)
        
        assert context.error_type == ErrorType.AUTHENTICATION_ERROR
        assert context.recoverable == False
        assert "log in again" in context.user_facing_message

class TestCircuitBreaker:
    def setup_method(self):
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=1)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_failures(self):
        async def failing_function():
            raise Exception("Service unavailable")
        
        # Trigger failures to open circuit
        for _ in range(3):
            with pytest.raises(Exception):
                await self.circuit_breaker.call(failing_function)
        
        # Circuit should be open now
        assert self.circuit_breaker.state.value == "open"
        
        # Should raise exception without calling function
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            await self.circuit_breaker.call(failing_function)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_recovers(self):
        async def sometimes_failing_function():
            if hasattr(sometimes_failing_function, 'call_count'):
                sometimes_failing_function.call_count += 1
            else:
                sometimes_failing_function.call_count = 1
            
            if sometimes_failing_function.call_count <= 3:
                raise Exception("Service unavailable")
            return "success"
        
        # Trigger failures to open circuit
        for _ in range(3):
            with pytest.raises(Exception):
                await self.circuit_breaker.call(sometimes_failing_function)
        
        # Wait for recovery timeout
        await asyncio.sleep(1.1)
        
        # Should succeed and close circuit
        result = await self.circuit_breaker.call(sometimes_failing_function)
        assert result == "success"
        assert self.circuit_breaker.state.value == "closed"

class TestRetryHandler:
    @pytest.mark.asyncio
    async def test_retry_for_rate_limit_errors(self):
        call_count = 0
        
        async def rate_limited_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Rate limit exceeded")
            return "success"
        
        result = await RetryHandler.execute_with_retry(
            rate_limited_function,
            ErrorType.RATE_LIMIT_ERROR,
            max_attempts=3
        )
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_no_retry_for_client_errors(self):
        call_count = 0
        
        async def client_error_function():
            nonlocal call_count
            call_count += 1
            raise Exception("Bad request")
        
        with pytest.raises(Exception):
            await RetryHandler.execute_with_retry(
                client_error_function,
                ErrorType.CLIENT_ERROR,
                max_attempts=3
            )
        
        # Should only be called once (no retry)
        assert call_count == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
