"""End-to-end tests"""

import asyncio

import pytest

from src.question_service.core.question_generator import QuestionGenerator
from src.question_service.providers.mock_provider import MockAIProvider


@pytest.mark.asyncio
async def test_full_question_generation_flow(question_generator, job_manager):
    """Test complete question generation workflow"""
    job_id = "e2e-test-1"
    topic = "Machine Learning"

    # Create job
    await job_manager.create_job(job_id, {"topic": topic, "count": 3})

    # Process job
    await question_generator.process_job(job_id, topic, count=3)

    # Verify completion
    job_data = await job_manager.get_job(job_id)
    assert job_data["status"] == "completed"
    assert len(job_data.get("questions", [])) > 0


@pytest.mark.asyncio
async def test_retry_mechanism(question_generator, job_manager, ai_provider):
    """Test retry mechanism with failures"""
    job_id = "retry-test-1"
    topic = "Testing"

    # Mock provider to fail first call
    original_generate = ai_provider.generate_content
    call_count = 0

    async def failing_generate(prompt, **kwargs):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise Exception("Simulated failure")
        return await original_generate(prompt, **kwargs)

    ai_provider.generate_content = failing_generate

    # Create and process job
    await job_manager.create_job(job_id, {"topic": topic, "count": 2})
    await question_generator.process_job(job_id, topic, count=2)

    # Verify retry worked
    job_data = await job_manager.get_job(job_id)
    assert job_data["status"] == "completed"
    assert call_count == 2  # Failed once, succeeded on retry
