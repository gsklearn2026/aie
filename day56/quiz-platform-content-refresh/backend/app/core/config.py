from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/quiz_content"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/quiz_content"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Gemini AI
    GEMINI_API_KEY: str = "AIzaSyDGswqDT4wQw_bd4WZtIgYAawRDZ0Gisn8"
    
    # Content Refresh Settings
    FRESHNESS_THRESHOLD: float = 40.0
    REFRESH_BATCH_SIZE: int = 10
    MAX_REFRESH_RETRIES: int = 3
    
    # Scheduler Settings
    FRESHNESS_SCAN_HOURS: int = 6
    STALE_PROCESS_HOUR: int = 2
    
    # Alert Thresholds
    ALERT_QUEUE_DEPTH: int = 100
    ALERT_ROLLBACK_RATE: float = 0.15
    ALERT_REFRESH_TIME_P95: int = 300
    ALERT_STALE_CONTENT_PCT: float = 0.2
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
