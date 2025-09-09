"""Application configuration management."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    # API Configuration
    api_host: str = Field(default="localhost")
    api_port: int = Field(default=8000)
    api_version: str = Field(default="v1")
    debug: bool = Field(default=False)

    # AI Configuration
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-1.5-flash")

    # Database
    database_url: str = Field(default="sqlite:///./quiz.db")
    test_database_url: str = Field(default="sqlite:///./test_quiz.db")

    # Testing
    coverage_threshold: int = Field(default=80)

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


settings = Settings()
