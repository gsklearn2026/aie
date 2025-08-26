from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    anthropic_api_key: str = "your-anthropic-api-key"
    gemini_api_key: str = "AIzaSyCbEp7_ZL5CuXGk30R4yQR-0_m4wIAEIvw"
    redis_url: str = "redis://localhost:6379"
    database_url: str = "postgresql://user:password@localhost/quiz_platform"
    cache_ttl: int = 3600  # 1 hour
    max_request_size: int = 1024 * 1024  # 1MB
    debug: bool = False
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra environment variables

settings = Settings()
