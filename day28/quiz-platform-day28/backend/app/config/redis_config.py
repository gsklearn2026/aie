import redis
import os

# Redis configuration
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

def get_redis():
    return redis.from_url(REDIS_URL, decode_responses=True)

# Redis client instance
redis_client = get_redis()
