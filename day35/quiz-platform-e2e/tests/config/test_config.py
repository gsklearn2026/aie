"""E2E Test Configuration"""
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class TestConfig:
    """Test configuration settings"""
    
    # URLs
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"
    
    # Database
    test_db_url: str = "postgresql://test:test@localhost:5432/quiz_test"
    
    # AI Service
    gemini_api_key: Optional[str] = None
    
    # Browser settings
    browser: str = "chromium"
    headless: bool = True
    viewport_width: int = 1920
    viewport_height: int = 1080
    
    # Test timeouts
    default_timeout: int = 30000
    ai_response_timeout: int = 10000
    
    # Performance thresholds
    max_quiz_load_time: float = 3.0
    max_ai_generation_time: float = 5.0
    
    # Visual regression
    pixel_threshold: float = 0.2
    threshold: float = 0.2
    
    @classmethod
    def from_env(cls):
        """Load configuration from environment variables"""
        return cls(
            frontend_url=os.getenv("FRONTEND_URL", "http://localhost:3000"),
            backend_url=os.getenv("BACKEND_URL", "http://localhost:8000"),
            test_db_url=os.getenv("TEST_DB_URL", "postgresql://test:test@localhost:5432/quiz_test"),
            gemini_api_key=os.getenv("GEMINI_API_KEY"),
            browser=os.getenv("BROWSER", "chromium"),
            headless=os.getenv("HEADLESS", "true").lower() == "true"
        )

config = TestConfig.from_env()
