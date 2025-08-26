import pytest
import time
from unittest.mock import Mock, patch
from backend.middleware.rate_limiter import RateLimiter, TokenBucket, RateLimitConfig

class TestTokenBucket:
    def test_token_bucket_allows_requests_within_limit(self):
        # Mock Redis
        redis_mock = Mock()
        redis_mock.pipeline.return_value.hmget.return_value = [None, None]
        redis_mock.pipeline.return_value.ttl.return_value = -1
        redis_mock.pipeline.return_value.execute.return_value = [[None, None], -1]
        
        bucket = TokenBucket(redis_mock)
        
        allowed, info = bucket.is_allowed('test_key', 10, 1.0, 60)
        
        assert allowed == True
        assert info['tokens_remaining'] >= 0
    
    def test_token_bucket_denies_when_no_tokens(self):
        # Mock Redis with no tokens and recent refill to prevent token regeneration
        redis_mock = Mock()
        current_time = time.time()
        # Set last_refill to current time so no tokens are regenerated
        redis_mock.pipeline.return_value.hmget.return_value = [0, current_time]
        redis_mock.pipeline.return_value.ttl.return_value = 30
        redis_mock.pipeline.return_value.execute.return_value = [[0, current_time], 30]
        
        bucket = TokenBucket(redis_mock)
        
        # Mock time.time to return the same value to prevent token regeneration
        with patch('time.time', return_value=current_time):
            allowed, info = bucket.is_allowed('test_key', 10, 1.0, 60)
        
        assert allowed == False
        assert info['retry_after'] > 0

class TestRateLimiter:
    def test_rate_limiter_checks_user_tier(self):
        redis_mock = Mock()
        redis_mock.get.return_value = b'premium'
        
        rate_limiter = RateLimiter(redis_mock)
        tier = rate_limiter.get_user_tier('user123')
        
        assert tier == 'premium'
    
    def test_rate_limiter_defaults_to_free_tier(self):
        redis_mock = Mock()
        redis_mock.get.return_value = None
        
        rate_limiter = RateLimiter(redis_mock)
        tier = rate_limiter.get_user_tier('user123')
        
        assert tier == 'free'

class TestRateLimitConfig:
    def test_tier_configurations(self):
        assert 'free' in RateLimitConfig.TIERS
        assert 'premium' in RateLimitConfig.TIERS
        assert 'admin' in RateLimitConfig.TIERS
        
        assert RateLimitConfig.TIERS['free']['requests'] == 100
        assert RateLimitConfig.TIERS['premium']['requests'] == 1000
    
    def test_endpoint_configurations(self):
        assert 'ai_generate' in RateLimitConfig.ENDPOINT_LIMITS
        assert 'quiz_submit' in RateLimitConfig.ENDPOINT_LIMITS
        
        assert RateLimitConfig.ENDPOINT_LIMITS['ai_generate']['requests'] == 5
