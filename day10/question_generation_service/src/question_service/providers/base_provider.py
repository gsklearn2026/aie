"""Base AI provider interface"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class AIProvider(ABC):
    """Abstract base class for AI providers"""

    @abstractmethod
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using AI provider"""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check provider health"""
        pass
