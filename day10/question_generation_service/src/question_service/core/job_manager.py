"""Job management with Redis-based queuing and state tracking"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import redis.asyncio as redis
import structlog

logger = structlog.get_logger()


class JobManager:
    """Manages job lifecycle, state, and persistence"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.job_prefix = "job:"
        self.job_list = "jobs:pending"
        self.retry_list = "jobs:retry"

    async def initialize(self):
        """Initialize job manager"""
        await self.redis.ping()
        logger.info("Job manager initialized")

    async def create_job(self, job_id: str, job_data: Dict[str, Any]) -> bool:
        """Create new job"""
        job_key = f"{self.job_prefix}{job_id}"

        job_record = {
            "job_id": job_id,
            "status": "pending",
            "created_at": datetime.utcnow().isoformat(),
            "retry_count": 0,
            **job_data,
        }

        pipe = self.redis.pipeline()
        pipe.hset(
            job_key,
            mapping={
                k: json.dumps(v) if isinstance(v, (dict, list)) else str(v)
                for k, v in job_record.items()
            },
        )
        pipe.lpush(self.job_list, job_id)
        pipe.expire(job_key, 86400)  # 24 hour TTL

        await pipe.execute()

        logger.info("Job created", job_id=job_id)
        return True

    async def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job data"""
        job_key = f"{self.job_prefix}{job_id}"

        job_data = await self.redis.hgetall(job_key)

        if not job_data:
            return None

        # Parse JSON fields
        parsed_data = {}
        for key, value in job_data.items():
            try:
                parsed_data[key] = json.loads(value)
            except (json.JSONDecodeError, TypeError):
                parsed_data[key] = value

        return parsed_data

    async def update_job_status(self, job_id: str, status: str, **kwargs) -> bool:
        """Update job status and metadata"""
        job_key = f"{self.job_prefix}{job_id}"

        updates = {"status": status}
        updates.update(kwargs)

        if status in ["completed", "failed"]:
            updates["completed_at"] = datetime.utcnow().isoformat()

        formatted_updates = {
            k: json.dumps(v) if isinstance(v, (dict, list)) else str(v)
            for k, v in updates.items()
        }

        result = await self.redis.hset(job_key, mapping=formatted_updates)

        logger.info("Job status updated", job_id=job_id, status=status)
        return result > 0

    async def increment_retry_count(self, job_id: str) -> int:
        """Increment retry count and return new value"""
        job_key = f"{self.job_prefix}{job_id}"
        return await self.redis.hincrby(job_key, "retry_count", 1)

    async def schedule_retry(self, job_id: str, delay_seconds: int = 60):
        """Schedule job for retry"""
        retry_time = datetime.utcnow() + timedelta(seconds=delay_seconds)

        await self.redis.zadd(self.retry_list, {job_id: retry_time.timestamp()})

        await self.update_job_status(job_id, "retrying")

        logger.info("Job scheduled for retry", job_id=job_id, delay=delay_seconds)

    async def get_ready_retries(self) -> List[str]:
        """Get jobs ready for retry"""
        now = datetime.utcnow().timestamp()

        ready_jobs = await self.redis.zrangebyscore(self.retry_list, 0, now)

        if ready_jobs:
            # Remove from retry list
            await self.redis.zrem(self.retry_list, *ready_jobs)

        return ready_jobs

    async def list_jobs(
        self, status: Optional[str] = None, limit: int = 10, offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List jobs with optional filtering"""
        # For simplicity, get all job keys and filter
        pattern = f"{self.job_prefix}*"
        job_keys = []

        async for key in self.redis.scan_iter(match=pattern):
            job_keys.append(key)

        jobs = []
        for key in job_keys[offset : offset + limit]:
            job_data = await self.redis.hgetall(key)
            if job_data:
                parsed_data = {}
                for k, v in job_data.items():
                    try:
                        parsed_data[k] = json.loads(v)
                    except (json.JSONDecodeError, TypeError):
                        parsed_data[k] = v

                if not status or parsed_data.get("status") == status:
                    jobs.append(parsed_data)

        return jobs

    async def cancel_job(self, job_id: str) -> bool:
        """Cancel job"""
        job_key = f"{self.job_prefix}{job_id}"

        exists = await self.redis.exists(job_key)
        if not exists:
            return False

        await self.update_job_status(job_id, "cancelled")

        # Remove from queues
        await self.redis.lrem(self.job_list, 0, job_id)
        await self.redis.zrem(self.retry_list, job_id)

        logger.info("Job cancelled", job_id=job_id)
        return True
