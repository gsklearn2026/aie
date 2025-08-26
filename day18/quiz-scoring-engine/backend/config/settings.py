from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    app_name: str = "Quiz Scoring Engine"
    app_version: str = "1.0.0"
    debug: bool = True
    
    # Database
    database_url: str = "sqlite:///./quiz_scoring.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Gemini AI
    gemini_api_key: Optional[str] = None
    
    # Scoring
    default_scoring_strategy: str = "weighted"
    cache_ttl: int = 3600
    
    class Config:
        env_file = ".env"

settings = Settings()
