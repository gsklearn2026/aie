import os
from typing import Dict, List, Optional, Any
from loguru import logger
from .provider_manager import ProviderManager
from ..providers.anthropic_provider import AnthropicProvider
from ..providers.mock_provider import MockProvider

class AIService:
    def __init__(self):
        self.provider_manager = ProviderManager()
        self.initialize_providers()
        
    def initialize_providers(self) -> None:
        # Add Anthropic provider if API key is available
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key and anthropic_key != "your_anthropic_key_here":
            anthropic_provider = AnthropicProvider(
                anthropic_key,
                os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
            )
            self.provider_manager.add_provider(anthropic_provider, True)
            logger.info("Initialized Anthropic provider")
        
        # Add mock providers for testing
        self.provider_manager.add_provider(MockProvider("mock-primary"), not anthropic_key)
        self.provider_manager.add_provider(MockProvider("mock-fallback"))
        
        logger.info("AI Service initialized with providers")
    
    async def generate_text(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        logger.info(f"Generating text for prompt: \"{prompt[:50]}{'...' if len(prompt) > 50 else ''}\"")
        
        try:
            response = await self.provider_manager.generate_text(prompt, options)
            logger.info(f"Text generated successfully using {response['provider']}")
            return response
        except Exception as error:
            logger.error(f"Text generation failed: {error}")
            raise error
    
    async def get_provider_health(self) -> List[Dict[str, Any]]:
        return self.provider_manager.get_health_status()
    
    def get_available_providers(self) -> List[str]:
        return self.provider_manager.get_provider_names()
