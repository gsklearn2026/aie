import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://quiz_user:quiz_password@localhost:5432/quiz_platform"
    BACKUP_DATABASE_URL: str = "postgresql://backup_user:backup_password@localhost:5432/quiz_backup"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Backup intervals (seconds)
    HOT_BACKUP_INTERVAL: int = 300  # 5 minutes
    WARM_BACKUP_INTERVAL: int = 3600  # 1 hour
    COLD_BACKUP_INTERVAL: int = 86400  # 24 hours
    
    # Retention
    BACKUP_RETENTION_DAYS: int = 30
    
    # Storage
    BACKUP_STORAGE_PATH: str = "./backups"
    
    # Monitoring
    PROMETHEUS_PORT: int = 8001
    METRICS_ENABLED: bool = True
    
    # AI
    GEMINI_API_KEY: str = "your_gemini_api_key_here"
    
    # AWS S3 (optional)
    aws_s3_bucket: str = "quiz-platform-backups"
    aws_region: str = "us-west-2"
    
    class Config:
        env_file = ".env"
        extra = "allow"
