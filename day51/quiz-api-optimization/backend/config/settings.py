from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GEMINI_API_KEY: str = "AIzaSyDGswqDT4wQw_bd4WZtIgYAawRDZ0Gisn8"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    DATABASE_URL: str = "sqlite+aiosqlite:///./quiz_platform.db"
    CACHE_TTL: int = 3600
    COMPRESSION_MIN_SIZE: int = 1024
    ENABLE_COMPRESSION: bool = True
    ENABLE_CACHING: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
