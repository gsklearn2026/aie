import redis.asyncio as redis
import os

redis_client = redis.from_url(
    os.getenv("REDIS_URL", "redis://redis:6379"),
    encoding="utf-8",
    decode_responses=True
)
