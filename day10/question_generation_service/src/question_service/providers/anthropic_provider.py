"""Anthropic Claude provider implementation"""

import asyncio
from typing import Any, Dict

import anthropic

from .base_provider import AIProvider


class AnthropicProvider(AIProvider):
    """Anthropic Claude provider"""

    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.model = model

    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using Anthropic Claude API"""
        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", 1000),
                temperature=kwargs.get("temperature", 0.7),
                messages=[{"role": "user", "content": prompt}],
            )

            return response.content[0].text

        except Exception as e:
            raise Exception(f"Anthropic API error: {e}")

    async def health_check(self) -> bool:
        """Check Anthropic API health"""
        try:
            await self.client.messages.create(
                model=self.model,
                max_tokens=1,
                messages=[{"role": "user", "content": "Test"}],
            )
            return True
        except:
            return False
