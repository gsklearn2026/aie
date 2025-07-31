import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
from collections import deque

from app.services.difficulty_service import PerformanceWindow, ProgressiveDifficultyService

class TestPerformanceWindow:
    def test_empty_window_success_rate(self):
        window = PerformanceWindow()
        assert window.calculate_success_rate() == 0.7  # Default neutral rate
    
    def test_single_response(self):
        window = PerformanceWindow()
        window.add_response(True, 2000, 1.5)
        assert window.calculate_success_rate() > 0.7
    
    def test_momentum_calculation(self):
        window = PerformanceWindow()
        # Add responses showing improvement
        for i in range(6):
            is_correct = i >= 3  # First 3 wrong, last 3 correct
            window.add_response(is_correct, 2000, 1.0)
        
        momentum = window.calculate_momentum()
        assert momentum > 0  # Should show positive momentum

class TestProgressiveDifficultyService:
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    @pytest.fixture
    def mock_redis(self):
        redis_mock = AsyncMock()
        redis_mock.get.return_value = None
        redis_mock.setex = AsyncMock()
        return redis_mock
    
    @pytest.fixture
    def service(self, mock_db, mock_redis):
        return ProgressiveDifficultyService(mock_db, mock_redis)
    
    def test_calculate_next_difficulty_increase(self, service):
        # High success rate should increase difficulty
        current_difficulty = 2.0
        success_rate = 0.9  # High success
        momentum = 0.1  # Slight positive momentum
        
        new_difficulty = service.calculate_next_difficulty(current_difficulty, success_rate, momentum)
        assert new_difficulty > current_difficulty
    
    def test_calculate_next_difficulty_decrease(self, service):
        # Low success rate should decrease difficulty
        current_difficulty = 2.0
        success_rate = 0.4  # Low success
        momentum = -0.1  # Slight negative momentum
        
        new_difficulty = service.calculate_next_difficulty(current_difficulty, success_rate, momentum)
        assert new_difficulty < current_difficulty
    
    def test_difficulty_bounds(self, service):
        # Test minimum bound
        low_difficulty = service.calculate_next_difficulty(0.2, 0.0, -0.5)
        assert low_difficulty >= 0.1
        
        # Test maximum bound
        high_difficulty = service.calculate_next_difficulty(4.8, 1.0, 0.5)
        assert high_difficulty <= 5.0
    
    def test_max_difficulty_change_limit(self, service):
        # Large adjustment should be limited
        current_difficulty = 2.0
        new_difficulty = service.calculate_next_difficulty(current_difficulty, 0.0, -1.0)
        
        change = abs(new_difficulty - current_difficulty)
        assert change <= service.max_difficulty_change

@pytest.mark.asyncio
class TestAsyncMethods:
    @pytest.fixture
    def service(self):
        mock_db = Mock()
        mock_redis = AsyncMock()
        mock_redis.get.return_value = None
        mock_redis.setex = AsyncMock()
        return ProgressiveDifficultyService(mock_db, mock_redis)
    
    async def test_cache_performance_window(self, service):
        window = PerformanceWindow()
        window.add_response(True, 2000, 1.5)
        
        await service._cache_performance_window("test_key", window)
        service.redis.setex.assert_called_once()
