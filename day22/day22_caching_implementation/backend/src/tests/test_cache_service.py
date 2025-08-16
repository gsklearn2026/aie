import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from src.services.cache_service import CacheService

@pytest.fixture
def cache_service():
    return CacheService()

@pytest.fixture
def mock_redis_client():
    mock_client = AsyncMock()
    mock_client.get.return_value = None
    mock_client.set.return_value = True
    mock_client.invalidate_pattern.return_value = 5
    return mock_client

@pytest.mark.asyncio
async def test_cache_aside_pattern(cache_service, mock_redis_client):
    """Test cache-aside pattern with cache miss and set"""
    
    # Mock the fetch function
    async def mock_fetch_func(quiz_id):
        return {"id": quiz_id, "title": "Test Quiz"}
    
    with patch.object(cache_service, '_get_redis', return_value=mock_redis_client):
        # First call should be cache miss
        result = await cache_service.get_or_set(
            "test_key", 
            mock_fetch_func, 
            3600, 
            "quiz123"
        )
        
        # Verify cache get was called
        mock_redis_client.get.assert_called_once_with("test_key")
        
        # Verify cache set was called with fetched data
        mock_redis_client.set.assert_called_once_with(
            "test_key", 
            {"id": "quiz123", "title": "Test Quiz"}, 
            3600
        )
        
        assert result == {"id": "quiz123", "title": "Test Quiz"}

@pytest.mark.asyncio
async def test_cache_hit(cache_service, mock_redis_client):
    """Test cache hit scenario"""
    
    # Configure mock to return cached data
    cached_data = {"id": "quiz123", "title": "Cached Quiz"}
    mock_redis_client.get.return_value = cached_data
    
    async def mock_fetch_func(quiz_id):
        # This should not be called on cache hit
        pytest.fail("Fetch function should not be called on cache hit")
    
    with patch.object(cache_service, '_get_redis', return_value=mock_redis_client):
        result = await cache_service.get_or_set(
            "test_key", 
            mock_fetch_func, 
            3600, 
            "quiz123"
        )
        
        # Verify only get was called, not set
        mock_redis_client.get.assert_called_once_with("test_key")
        mock_redis_client.set.assert_not_called()
        
        assert result == cached_data

@pytest.mark.asyncio
async def test_quiz_cache_invalidation(cache_service, mock_redis_client):
    """Test quiz cache invalidation"""
    
    with patch.object(cache_service, '_get_redis', return_value=mock_redis_client):
        deleted_count = await cache_service.invalidate_quiz_cache("quiz123")
        
        # Should call invalidate_pattern for each pattern
        assert mock_redis_client.invalidate_pattern.call_count == 4
        assert deleted_count == 20  # 4 patterns * 5 keys each
