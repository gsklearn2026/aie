from typing import Dict, List, Optional, Any
import time
from loguru import logger
from ..providers.base_provider import BaseProvider

class ProviderHealth:
    def __init__(self, provider: str, is_healthy: bool = True, error_count: int = 0):
        self.provider = provider
        self.is_healthy = is_healthy
        self.last_checked = time.time()
        self.response_time = None
        self.error_count = error_count

class ProviderManager:
    def __init__(self):
        self.providers: Dict[str, BaseProvider] = {}
        self.health_status: Dict[str, ProviderHealth] = {}
        self.primary_provider = None
        
    def add_provider(self, provider: BaseProvider, is_primary: bool = False) -> None:
        name = provider.get_provider_name()
        self.providers[name] = provider
        self.health_status[name] = ProviderHealth(name)
        
        if is_primary or not self.primary_provider:
            self.primary_provider = name
            
        logger.info(f"Added provider: {name} (primary: {is_primary})")
    
    async def generate_text(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        available_providers = await self.get_healthy_providers()
        
        if not available_providers:
            raise Exception("No healthy providers available")
        
        # Try primary provider first if healthy
        if self.primary_provider and self.primary_provider in available_providers:
            try:
                response = await self.call_provider(self.primary_provider, prompt, options)
                logger.info(f"Successfully used primary provider: {self.primary_provider}")
                return response
            except Exception as error:
                logger.warning(f"Primary provider {self.primary_provider} failed, trying fallback")
                await self.update_health_status(self.primary_provider, False)
        
        # Try fallback providers
        for provider_name in available_providers:
            if provider_name == self.primary_provider:
                continue
                
            try:
                response = await self.call_provider(provider_name, prompt, options)
                logger.info(f"Successfully used fallback provider: {provider_name}")
                return response
            except Exception as error:
                logger.warning(f"Provider {provider_name} failed: {error}")
                await self.update_health_status(provider_name, False)
        
        raise Exception("All providers failed")
    
    async def call_provider(self, provider_name: str, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        provider = self.providers.get(provider_name)
        if not provider:
            raise Exception(f"Provider {provider_name} not found")
        
        response = await provider.generate_text(prompt, options)
        await self.update_health_status(provider_name, True, response["response_time"])
        return response
    
    async def get_healthy_providers(self) -> List[str]:
        healthy_providers = []
        
        for name, provider in self.providers.items():
            try:
                is_healthy = await provider.is_healthy()
                await self.update_health_status(name, is_healthy)
                
                if is_healthy:
                    healthy_providers.append(name)
            except Exception as error:
                logger.error(f"Health check failed for {name}: {error}")
                await self.update_health_status(name, False)
        
        return healthy_providers
    
    async def update_health_status(self, provider_name: str, is_healthy: bool, response_time: Optional[int] = None) -> None:
        current_status = self.health_status.get(provider_name)
        if not current_status:
            return
        
        current_status.is_healthy = is_healthy
        current_status.last_checked = time.time()
        current_status.response_time = response_time
        current_status.error_count = 0 if is_healthy else current_status.error_count + 1
    
    def get_health_status(self) -> List[Dict[str, Any]]:
        return [
            {
                "provider": status.provider,
                "is_healthy": status.is_healthy,
                "last_checked": status.last_checked,
                "response_time": status.response_time,
                "error_count": status.error_count
            }
            for status in self.health_status.values()
        ]
    
    def get_provider_names(self) -> List[str]:
        return list(self.providers.keys())
