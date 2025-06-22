"""Pytest configuration and fixtures"""

import asyncio
from unittest.mock import AsyncMock

import pytest
import redis.asyncio as redis

from src.question_service.core.job_manager import JobManager
from src.question_service.core.question_generator import QuestionGenerator
from src.question_service.providers.mock_provider import MockAIProvider


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def redis_client():
    """Mock Redis client for testing"""
    mock_redis = AsyncMock(spec=redis.Redis)
    mock_redis.ping.return_value = True
    mock_redis.hset.return_value = 1
    mock_redis.hgetall.return_value = {}
    mock_redis.exists.return_value = True
    yield mock_redis


@pytest.fixture
async def job_manager(redis_client):
    """Job manager fixture"""
    manager = JobManager(redis_client)
    await manager.initialize()
    return manager


@pytest.fixture
def ai_provider():
    """AI provider fixture"""
    return MockAIProvider()


@pytest.fixture
async def question_generator(ai_provider, job_manager):
    """Question generator fixture"""
    return QuestionGenerator(ai_provider, job_manager)
