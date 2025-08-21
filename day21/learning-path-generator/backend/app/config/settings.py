from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    database_url: str = "sqlite:///./learning_paths.db"
    redis_url: str = "redis://localhost:6379"
    gemini_api_key: str = ""
    secret_key: str = "your-secret-key-here"
    
    class Config:
        env_file = ".env"

def get_settings():
    return Settings()
