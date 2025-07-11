import asyncio
import random
import time
from typing import Dict, Any, Optional
from .base_provider import BaseProvider

class MockProvider(BaseProvider):
    def __init__(self, name: str = "mock", should_fail: bool = False):
        super().__init__(name)
        self.should_fail = should_fail
        self.response_delay = 0.1
        
    async def generate_text(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        start_time = time.time()
        
        if self.should_fail:
            self.increment_error_count()
            raise Exception("Mock provider intentionally failed")
        
        await asyncio.sleep(self.response_delay)
        
        response_time = int((time.time() - start_time) * 1000)
        self.reset_error_count()
        
        return {
            "content": f"Mock response to: \"{prompt[:50]}{'...' if len(prompt) > 50 else ''}\"",
            "provider": self.get_provider_name(),
            "model": "mock-model-v1",
            "tokens_used": random.randint(50, 150),
            "response_time": response_time,
            "metadata": {"mock_response": True}
        }
    
    async def is_healthy(self) -> bool:
        return not self.should_fail
    
    def get_model_name(self) -> str:
        return "mock-model-v1"
    
    def set_should_fail(self, should_fail: bool) -> None:
        self.should_fail = should_fail
        
    def set_response_delay(self, delay: float) -> None:
        self.response_delay = delay
