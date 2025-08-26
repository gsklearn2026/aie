"""Unit tests for job manager"""

from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from src.question_service.core.job_manager import JobManager


@pytest.mark.asyncio
async def test_create_job(job_manager, redis_client):
    """Test job creation"""
    job_id = "test-job-1"
    job_data = {"topic": "Python", "count": 5}

    result = await job_manager.create_job(job_id, job_data)

    assert result is True
    redis_client.hset.assert_called()
    redis_client.lpush.assert_called()


@pytest.mark.asyncio
async def test_update_job_status(job_manager, redis_client):
    """Test job status update"""
    job_id = "test-job-1"

    result = await job_manager.update_job_status(job_id, "processing")

    assert result is True
    redis_client.hset.assert_called()


@pytest.mark.asyncio
async def test_schedule_retry(job_manager, redis_client):
    """Test retry scheduling"""
    job_id = "test-job-1"

    await job_manager.schedule_retry(job_id, 60)

    redis_client.zadd.assert_called()


@pytest.mark.asyncio
async def test_cancel_job(job_manager, redis_client):
    """Test job cancellation"""
    job_id = "test-job-1"

    result = await job_manager.cancel_job(job_id)

    assert result is True
    redis_client.lrem.assert_called()
    redis_client.zrem.assert_called()
