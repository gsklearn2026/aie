from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # Algorithm Parameters
    performance_window_size: int = 10
    optimal_success_rate: float = 0.85
    confidence_threshold: float = 0.7
    adaptation_sensitivity: float = 0.1
    
    # API Configuration
    anthropic_api_key: str = "your-anthropic-key"
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
