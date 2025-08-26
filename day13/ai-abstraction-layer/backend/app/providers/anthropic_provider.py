import anthropic
from typing import Dict, Any, Optional
import time
from loguru import logger
from .base_provider import BaseProvider

class AnthropicProvider(BaseProvider):
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        super().__init__("anthropic")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        
    async def generate_text(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            options = options or {}
            
            response = self.client.messages.create(
                model=options.get('model', self.model),
                max_tokens=options.get('max_tokens', 1000),
                temperature=options.get('temperature', 0.7),
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_time = int((time.time() - start_time) * 1000)
            self.reset_error_count()
            
            return {
                "content": response.content[0].text if response.content else "",
                "provider": self.get_provider_name(),
                "model": self.model,
                "tokens_used": response.usage.output_tokens,
                "response_time": response_time,
                "metadata": {
                    "input_tokens": response.usage.input_tokens,
                    "stop_reason": response.stop_reason
                }
            }
            
        except Exception as error:
            self.increment_error_count()
            logger.error(f"Anthropic provider error: {error}")
            raise error
    
    async def is_healthy(self) -> bool:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "health check"}]
            )
            self.last_health_check = time.time()
            return True
        except Exception as error:
            logger.error(f"Anthropic health check failed: {error}")
            return False
    
    def get_model_name(self) -> str:
        return self.model
