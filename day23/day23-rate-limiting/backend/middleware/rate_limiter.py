import time
import json
from functools import wraps
from flask import request, jsonify, current_app, g
from typing import Dict, Tuple, Optional
import redis
import structlog

logger = structlog.get_logger()

class RateLimitConfig:
    """Rate limit configuration for different user tiers and endpoints"""
    
    TIERS = {
        'free': {'requests': 100, 'window': 3600},  # 100 requests per hour
        'premium': {'requests': 1000, 'window': 3600},  # 1000 requests per hour
        'admin': {'requests': 10, 'window': 60}  # 10 requests per minute for admin endpoints
    }
    
    ENDPOINT_LIMITS = {
        'ai_generate': {'requests': 5, 'window': 60},  # 5 AI generations per minute
        'quiz_submit': {'requests': 30, 'window': 300},  # 30 submissions per 5 minutes
        'quiz_list': {'requests': 200, 'window': 3600},  # 200 list requests per hour
        'status': {'requests': 10, 'window': 60}  # Protect status endpoint: 10 requests per minute
    }

class TokenBucket:
    """Token bucket algorithm implementation"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
    def is_allowed(self, key: str, max_tokens: int, refill_rate: float, window: int) -> Tuple[bool, Dict]:
        """
        Check if request is allowed using token bucket algorithm
        
        Args:
            key: Unique identifier for the bucket
            max_tokens: Maximum tokens in bucket
            refill_rate: Tokens added per second
            window: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, info_dict)
        """
        now = time.time()
        bucket_key = f"bucket:{key}"
        
        # Get current bucket state
        pipe = self.redis.pipeline()
        pipe.hmget(bucket_key, 'tokens', 'last_refill')
        pipe.ttl(bucket_key)
        bucket_data, ttl = pipe.execute()
        
        tokens = float(bucket_data[0]) if bucket_data[0] is not None else max_tokens
        last_refill = float(bucket_data[1]) if bucket_data[1] is not None else now
        
        # Calculate tokens to add based on time elapsed
        time_elapsed = now - last_refill
        tokens_to_add = time_elapsed * refill_rate
        tokens = min(max_tokens, tokens + tokens_to_add)
        
        # Check if request can be served
        if tokens >= 1:
            tokens -= 1
            allowed = True
        else:
            allowed = False
            
        # Update bucket state
        pipe = self.redis.pipeline()
        # Use hset with mapping (hmset is deprecated in redis-py)
        pipe.hset(bucket_key, mapping={
            'tokens': tokens,
            'last_refill': now
        })
        pipe.expire(bucket_key, window * 2)  # Keep bucket for 2x window
        pipe.execute()
        
        return allowed, {
            'allowed': allowed,
            'tokens_remaining': int(tokens),
            'reset_time': int(now + (max_tokens - tokens) / refill_rate),
            'retry_after': int((1 - tokens) / refill_rate) if not allowed else 0
        }

class RateLimiter:
    """Main rate limiter class"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.bucket = TokenBucket(redis_client)
        
    def get_user_tier(self, user_id: str) -> str:
        """Get user tier from Redis or default to free"""
        tier = self.redis.get(f"user_tier:{user_id}")
        return tier.decode() if tier else 'free'
    
    def get_rate_limit_key(self, user_id: str, endpoint: str = None) -> str:
        """Generate rate limit key"""
        if endpoint:
            return f"rate_limit:{user_id}:{endpoint}"
        return f"rate_limit:{user_id}"
    
    def check_rate_limit(self, user_id: str, endpoint: str = None) -> Tuple[bool, Dict]:
        """Check if request is within rate limits"""
        
        # Get user tier
        tier = self.get_user_tier(user_id)
        
        # Check endpoint-specific limits first
        if endpoint and endpoint in RateLimitConfig.ENDPOINT_LIMITS:
            config = RateLimitConfig.ENDPOINT_LIMITS[endpoint]
            key = self.get_rate_limit_key(user_id, endpoint)
            
            refill_rate = config['requests'] / config['window']
            allowed, info = self.bucket.is_allowed(
                key, config['requests'], refill_rate, config['window']
            )
            
            if not allowed:
                return False, info
        
        # Check general tier limits
        if tier in RateLimitConfig.TIERS:
            config = RateLimitConfig.TIERS[tier]
            key = self.get_rate_limit_key(user_id)
            
            refill_rate = config['requests'] / config['window']
            allowed, info = self.bucket.is_allowed(
                key, config['requests'], refill_rate, config['window']
            )
            
            # Add tier information
            info['tier'] = tier
            info['tier_limit'] = config['requests']
            info['window'] = config['window']
            
            return allowed, info
        
        # Default: allow request
        return True, {'allowed': True, 'tier': 'unknown'}

def rate_limit(endpoint: str = None):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user ID from request
            user_id = request.headers.get('X-User-ID', request.remote_addr)
            
            # Initialize rate limiter
            rate_limiter = RateLimiter(current_app.redis)
            
            # Check rate limit
            allowed, info = rate_limiter.check_rate_limit(user_id, endpoint)
            
            if not allowed:
                logger.warning(
                    "Rate limit exceeded",
                    user_id=user_id,
                    endpoint=endpoint,
                    info=info
                )
                
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Try again in {info.get("retry_after", 60)} seconds.',
                    'rate_limit_info': info
                })
                response.status_code = 429
                response.headers['X-RateLimit-Limit'] = str(info.get('tier_limit', 'unknown'))
                response.headers['X-RateLimit-Remaining'] = str(info.get('tokens_remaining', 0))
                response.headers['X-RateLimit-Reset'] = str(info.get('reset_time', 0))
                response.headers['Retry-After'] = str(info.get('retry_after', 60))
                
                return response
            
            # Store rate limit info in g for use in response headers
            g.rate_limit_info = info
            
            # Execute the original function
            result = f(*args, **kwargs)
            
            # Add rate limit headers to successful responses
            if hasattr(result, 'headers'):
                result.headers['X-RateLimit-Limit'] = str(info.get('tier_limit', 'unknown'))
                result.headers['X-RateLimit-Remaining'] = str(info.get('tokens_remaining', 0))
                result.headers['X-RateLimit-Reset'] = str(info.get('reset_time', 0))
            
            return result
        return decorated_function
    return decorator
