from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str = "postgresql://quiz_user:quiz_pass@localhost:5432/quiz_db"
    redis_url: str = "redis://localhost:6379/0"
    gemini_api_key: str = ""
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    
    class Config:
        env_file = ".env"

settings = Settings()
