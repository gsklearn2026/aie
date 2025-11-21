from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Database
    database_url: str
    db_pool_size: int = 20
    db_max_overflow: int = 40
    
    # Redis
    redis_url: str
    redis_max_connections: int = 50
    
    # Gemini AI
    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash-exp"
    
    # Server
    port: int = 8000
    workers: int = 4
    cors_origins: str = "*"
    
    # Security
    force_https: bool = False
    hsts_enabled: bool = False
    
    # Auto-scaling
    min_instances: int = 2
    max_instances: int = 10
    scale_up_cpu_threshold: int = 70
    scale_down_cpu_threshold: int = 30
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()
