"""AI provider factory"""

import os
from typing import Dict, Type

from .anthropic_provider import AnthropicProvider
from .base_provider import AIProvider
from .mock_provider import MockAIProvider


class AIProviderFactory:
    """Factory for creating AI providers"""

    _providers: Dict[str, Type[AIProvider]] = {
        "mock": MockAIProvider,
        "anthropic": AnthropicProvider,
        "claude": AnthropicProvider,  # Alias for anthropic
    }

    @classmethod
    def create_provider(cls, provider_type: str, **kwargs) -> AIProvider:
        """Create AI provider instance"""
        provider_type = provider_type.lower()

        if provider_type not in cls._providers:
            raise ValueError(f"Unknown provider type: {provider_type}")

        provider_class = cls._providers[provider_type]

        if provider_type in ["anthropic", "claude"]:
            api_key = kwargs.get("api_key") or os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("Anthropic API key required")
            return provider_class(api_key=api_key, **kwargs)
        else:
            return provider_class(**kwargs)

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[AIProvider]):
        """Register new provider type"""
        cls._providers[name] = provider_class
