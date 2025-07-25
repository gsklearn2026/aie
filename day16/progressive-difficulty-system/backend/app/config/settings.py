from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings for Progressive Difficulty System"""
    
    # Redis Configuration
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_db: int = 0
    
    # Algorithm Parameters
    performance_window_size: int = 10  # Number of recent responses to consider
    optimal_success_rate: float = 0.75  # Target success rate (75%)
    confidence_threshold: float = 0.6  # Minimum confidence for decisions
    adaptation_sensitivity: float = 0.1  # How quickly to adapt difficulty
    
    # API Configuration
    api_title: str = "Progressive Difficulty Algorithm"
    api_version: str = "1.0.0"
    api_description: str = "Adaptive learning difficulty management system"
    
    # CORS Configuration
    cors_origins: list = ["http://localhost:3000"]
    
    # Logging
    log_level: str = "INFO"
    
    # Cache Configuration
    cache_ttl: int = 3600  # 1 hour in seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
_settings = None

def get_settings() -> Settings:
    """Get application settings singleton"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings 