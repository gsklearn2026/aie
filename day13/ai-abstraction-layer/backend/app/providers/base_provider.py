from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
from loguru import logger

class BaseProvider(ABC):
    def __init__(self, name: str):
        self.name = name
        self.error_count = 0
        self.last_health_check = None
        
    @abstractmethod
    async def generate_text(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate text using the AI provider"""
        pass
    
    @abstractmethod
    async def is_healthy(self) -> bool:
        """Check if the provider is healthy and operational"""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get the model name used by this provider"""
        pass
    
    def get_provider_name(self) -> str:
        """Get the provider name"""
        return self.name
    
    def increment_error_count(self) -> None:
        """Increment error count for reliability metrics"""
        self.error_count += 1
        
    def reset_error_count(self) -> None:
        """Reset error count on successful operation"""
        self.error_count = 0
        
    def get_error_count(self) -> int:
        """Get current error count"""
        return self.error_count
