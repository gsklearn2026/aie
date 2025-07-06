import pytest
import asyncio
from app.providers.mock_provider import MockProvider

@pytest.mark.asyncio
async def test_mock_provider_generate_text():
    provider = MockProvider("test-mock")
    response = await provider.generate_text("test prompt")
    
    assert "Mock response to: \"test prompt\"" in response["content"]
    assert response["provider"] == "test-mock"
    assert response["model"] == "mock-model-v1"
    assert response["tokens_used"] > 0
    assert response["response_time"] > 0

@pytest.mark.asyncio
async def test_mock_provider_failure():
    provider = MockProvider("test-mock", should_fail=True)
    
    with pytest.raises(Exception) as excinfo:
        await provider.generate_text("test prompt")
    
    assert "Mock provider intentionally failed" in str(excinfo.value)
    assert provider.get_error_count() == 1

@pytest.mark.asyncio
async def test_mock_provider_health():
    provider = MockProvider("test-mock")
    assert await provider.is_healthy() is True
    
    provider.set_should_fail(True)
    assert await provider.is_healthy() is False
