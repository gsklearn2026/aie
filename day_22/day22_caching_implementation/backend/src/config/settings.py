from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379"
    gemini_api_key: str = "your-gemini-api-key"
    cache_default_ttl: int = 3600  # 1 hour
    cache_quiz_ttl: int = 3600     # 1 hour
    cache_user_progress_ttl: int = 1800  # 30 minutes
    cache_leaderboard_ttl: int = 300     # 5 minutes
    cache_learning_path_ttl: int = 86400 # 24 hours
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
