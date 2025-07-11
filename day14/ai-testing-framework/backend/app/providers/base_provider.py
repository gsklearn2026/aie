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
        pass
    
    @abstractmethod
    async def is_healthy(self) -> bool:
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        pass
    
    def get_provider_name(self) -> str:
        return self.name
    
    def increment_error_count(self) -> None:
        self.error_count += 1
        
    def reset_error_count(self) -> None:
        self.error_count = 0
        
    def get_error_count(self) -> int:
        return self.error_count
