#!/usr/bin/env python3
"""
AI Engineering Day 10: Question Generation Service
Complete Implementation Script with One-Click Setup

Usage: python setup_question_service.py [--docker] [--test] [--clean]
"""

import os
import sys
import subprocess
import json
import time
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import shutil
import signal

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def colored_print(message: str, color: str = Colors.OKBLUE):
    print(f"{color}{message}{Colors.ENDC}")

def success(message: str):
    colored_print(f"✅ {message}", Colors.OKGREEN)

def warning(message: str):
    colored_print(f"⚠️  {message}", Colors.WARNING)

def error(message: str):
    colored_print(f"❌ {message}", Colors.FAIL)

def info(message: str):
    colored_print(f"ℹ️  {message}", Colors.OKBLUE)

class JobStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class Question:
    id: str
    question: str
    difficulty: str
    topic: str
    generated_at: str

@dataclass
class JobResult:
    job_id: str
    status: JobStatus
    topic: str
    questions: List[Question]
    created_at: str
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0

class ProjectSetup:
    """Handles project structure creation and file generation"""
    
    def __init__(self, project_name: str = "question_generation_service"):
        self.project_name = project_name
        self.base_path = Path.cwd() / project_name
        self.files_created = []
        
    def create_structure(self):
        """Create complete project directory structure"""
        info("Creating project structure...")
        
        directories = [
            "src/question_service",
            "src/question_service/api",
            "src/question_service/core",
            "src/question_service/providers",
            "src/question_service/models",
            "tests/unit",
            "tests/integration",
            "tests/e2e",
            "docker",
            "scripts",
            "config",
            "docs",
            "monitoring"
        ]
        
        for dir_path in directories:
            full_path = self.base_path / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
            
        success("Project structure created")
        
    def create_requirements(self):
        """Generate requirements.txt with latest compatible versions"""
        requirements = """# Core Framework
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Async & Queue Management
redis==5.0.1
aioredis==2.0.1
celery==5.3.4
asyncio-mqtt==0.13.0

# Database
sqlalchemy==2.0.23
alembic==1.13.1
asyncpg==0.29.0
psycopg2-binary==2.9.9

# AI Providers
anthropic==0.7.8
aiohttp==3.9.1

# Monitoring & Logging
prometheus-client==0.19.0
structlog==23.2.0
rich==13.7.0

# Testing
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-mock==3.12.0
httpx==0.25.2
factory-boy==3.3.0

# Development
black==23.11.0
isort==5.12.0
mypy==1.7.1
pre-commit==3.6.0

# Deployment
gunicorn==21.2.0
docker==6.1.3
"""
        
        self._write_file("requirements.txt", requirements)
        
    def create_dockerfile(self):
        """Generate production-ready Dockerfile"""
        dockerfile = """FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \\
    && chown -R app:app /app
USER app

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

CMD ["uvicorn", "src.question_service.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        self._write_file("Dockerfile", dockerfile)
        
    def create_docker_compose(self):
        """Generate docker-compose for development"""
        compose = """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/questions
      - AI_PROVIDER=anthropic
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - redis
      - postgres
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=questions
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  worker:
    build: .
    command: celery -A src.question_service.core.tasks worker --loglevel=info
    environment:
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/questions
      - AI_PROVIDER=anthropic
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - redis
      - postgres
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    restart: unless-stopped

volumes:
  redis_data:
  postgres_data:
"""
        self._write_file("docker-compose.yml", compose)
        
    def create_main_app(self):
        """Generate FastAPI application with async handlers"""
        main_app = '''"""FastAPI application with async question generation endpoints"""

import asyncio
import uuid
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import redis.asyncio as redis
import structlog

from ..core.question_generator import QuestionGenerator
from ..core.job_manager import JobManager
from ..models.schemas import JobSubmission, JobResponse, QuestionResponse
from ..providers.ai_provider import AIProviderFactory

logger = structlog.get_logger()

# Global instances
redis_client: Optional[redis.Redis] = None
job_manager: Optional[JobManager] = None
question_generator: Optional[QuestionGenerator] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global redis_client, job_manager, question_generator
    
    # Startup
    logger.info("Starting Question Generation Service...")
    
    redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
    ai_provider = AIProviderFactory.create_provider(
        os.getenv("AI_PROVIDER", "anthropic")
    )
    
    job_manager = JobManager(redis_client)
    question_generator = QuestionGenerator(ai_provider, job_manager)
    
    await job_manager.initialize()
    
    logger.info("Service started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    if redis_client:
        await redis_client.close()

app = FastAPI(
    title="Question Generation Service",
    description="Asynchronous AI-powered question generation with retry logic",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        await redis_client.ping()
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unavailable")

@app.post("/questions/generate", response_model=JobResponse)
async def generate_questions(
    submission: JobSubmission,
    background_tasks: BackgroundTasks
):
    """Submit question generation job"""
    job_id = str(uuid.uuid4())
    
    try:
        # Queue job for processing
        await job_manager.create_job(job_id, submission.dict())
        
        # Start background processing
        background_tasks.add_task(
            question_generator.process_job,
            job_id,
            submission.topic,
            submission.count,
            submission.difficulty
        )
        
        logger.info("Job queued", job_id=job_id, topic=submission.topic)
        
        return JobResponse(
            job_id=job_id,
            status="pending",
            message="Job queued for processing"
        )
        
    except Exception as e:
        logger.error("Failed to queue job", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to queue job")

@app.get("/questions/jobs/{job_id}", response_model=QuestionResponse)
async def get_job_status(job_id: str):
    """Get job status and results"""
    try:
        job_data = await job_manager.get_job(job_id)
        
        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")
            
        return QuestionResponse(**job_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get job", job_id=job_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve job")

@app.websocket("/questions/jobs/{job_id}/status")
async def websocket_job_status(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time job status updates"""
    await websocket.accept()
    
    try:
        while True:
            job_data = await job_manager.get_job(job_id)
            
            if job_data:
                await websocket.send_json(job_data)
                
                # Close connection if job is completed
                if job_data["status"] in ["completed", "failed", "cancelled"]:
                    break
                    
            await asyncio.sleep(1)
            
    except Exception as e:
        logger.error("WebSocket error", job_id=job_id, error=str(e))
    finally:
        await websocket.close()

@app.get("/questions/jobs", response_model=List[QuestionResponse])
async def list_jobs(
    status: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
):
    """List jobs with optional filtering"""
    try:
        jobs = await job_manager.list_jobs(status, limit, offset)
        return [QuestionResponse(**job) for job in jobs]
    except Exception as e:
        logger.error("Failed to list jobs", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list jobs")

@app.delete("/questions/jobs/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a job"""
    try:
        success = await job_manager.cancel_job(job_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Job not found")
            
        return {"message": "Job cancelled successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to cancel job", job_id=job_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to cancel job")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''
        self._write_file("src/question_service/api/main.py", main_app)
        self._write_file("src/question_service/api/__init__.py", "")
        
    def create_core_modules(self):
        """Generate core business logic modules"""
        
        # Job Manager
        job_manager = '''"""Job management with Redis-based queuing and state tracking"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
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
            **job_data
        }
        
        pipe = self.redis.pipeline()
        pipe.hset(job_key, mapping={k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) 
                                   for k, v in job_record.items()})
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
            
        formatted_updates = {k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) 
                           for k, v in updates.items()}
        
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
        
        await self.redis.zadd(
            self.retry_list,
            {job_id: retry_time.timestamp()}
        )
        
        await self.update_job_status(job_id, "retrying")
        
        logger.info("Job scheduled for retry", job_id=job_id, delay=delay_seconds)
        
    async def get_ready_retries(self) -> List[str]:
        """Get jobs ready for retry"""
        now = datetime.utcnow().timestamp()
        
        ready_jobs = await self.redis.zrangebyscore(
            self.retry_list, 0, now
        )
        
        if ready_jobs:
            # Remove from retry list
            await self.redis.zrem(self.retry_list, *ready_jobs)
            
        return ready_jobs
        
    async def list_jobs(self, status: Optional[str] = None, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """List jobs with optional filtering"""
        # For simplicity, get all job keys and filter
        pattern = f"{self.job_prefix}*"
        job_keys = []
        
        async for key in self.redis.scan_iter(match=pattern):
            job_keys.append(key)
            
        jobs = []
        for key in job_keys[offset:offset + limit]:
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
'''
        
        # Question Generator
        question_generator = '''"""Core question generation logic with retry mechanism"""

import asyncio
import json
from datetime import datetime
from typing import List, Optional
import structlog

from ..providers.ai_provider import AIProvider
from .job_manager import JobManager

logger = structlog.get_logger()

class QuestionGenerator:
    """Handles AI-powered question generation with retry logic"""
    
    MAX_RETRIES = 3
    RETRY_DELAYS = [5, 15, 45]  # Exponential backoff in seconds
    
    def __init__(self, ai_provider: AIProvider, job_manager: JobManager):
        self.ai_provider = ai_provider
        self.job_manager = job_manager
        
    async def process_job(self, job_id: str, topic: str, count: int = 5, difficulty: str = "medium"):
        """Process question generation job with retry logic"""
        logger.info("Processing job", job_id=job_id, topic=topic)
        
        await self.job_manager.update_job_status(job_id, "processing")
        
        retry_count = 0
        
        while retry_count <= self.MAX_RETRIES:
            try:
                # Generate questions
                questions = await self._generate_questions(topic, count, difficulty)
                
                # Store results
                await self.job_manager.update_job_status(
                    job_id, 
                    "completed",
                    questions=questions,
                    question_count=len(questions)
                )
                
                logger.info("Job completed successfully", job_id=job_id, count=len(questions))
                return
                
            except Exception as e:
                retry_count += 1
                error_msg = str(e)
                
                logger.error("Job processing failed", 
                           job_id=job_id, 
                           error=error_msg, 
                           retry_count=retry_count)
                
                await self.job_manager.increment_retry_count(job_id)
                
                if retry_count <= self.MAX_RETRIES:
                    delay = self.RETRY_DELAYS[min(retry_count - 1, len(self.RETRY_DELAYS) - 1)]
                    await self.job_manager.schedule_retry(job_id, delay)
                    await asyncio.sleep(delay)
                else:
                    # Max retries exceeded
                    await self.job_manager.update_job_status(
                        job_id, 
                        "failed",
                        error_message=error_msg,
                        retry_count=retry_count
                    )
                    break
                    
    async def _generate_questions(self, topic: str, count: int, difficulty: str) -> List[dict]:
        """Generate questions using AI provider"""
        prompt = self._build_prompt(topic, count, difficulty)
        
        response = await self.ai_provider.generate_content(prompt)
        
        questions = self._parse_questions(response, topic, difficulty)
        
        if len(questions) < count:
            logger.warning("Generated fewer questions than requested", 
                         expected=count, actual=len(questions))
                         
        return questions[:count]
        
    def _build_prompt(self, topic: str, count: int, difficulty: str) -> str:
        """Build AI prompt for question generation"""
        return f"""Generate {count} {difficulty} level questions about "{topic}".

Requirements:
- Questions should be clear and specific
- Appropriate for {difficulty} difficulty level
- Cover different aspects of the topic
- Return as JSON array with format: {{"question": "...", "type": "multiple_choice|short_answer|essay"}}

Please provide exactly {count} questions in valid JSON format.

Topic: {topic}
Count: {count}
Difficulty: {difficulty}

Generate the questions as a JSON array:"""

    def _parse_questions(self, response: str, topic: str, difficulty: str) -> List[dict]:
        """Parse AI response into structured questions"""
        try:
            # Try to extract JSON from response
            response = response.strip()
            
            # Find JSON array in response
            start_idx = response.find('[')
            end_idx = response.rfind(']') + 1
            
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response[start_idx:end_idx]
                questions_data = json.loads(json_str)
            else:
                # Fallback: parse as lines
                lines = [line.strip() for line in response.split('\\n') if line.strip()]
                questions_data = [{"question": line, "type": "short_answer"} for line in lines[:10]]
                
            # Format questions
            questions = []
            for i, q_data in enumerate(questions_data):
                if isinstance(q_data, str):
                    q_data = {"question": q_data, "type": "short_answer"}
                    
                question = {
                    "id": f"q_{i+1}",
                    "question": q_data.get("question", "").strip(),
                    "type": q_data.get("type", "short_answer"),
                    "difficulty": difficulty,
                    "topic": topic,
                    "generated_at": datetime.utcnow().isoformat()
                }
                
                if question["question"]:
                    questions.append(question)
                    
            return questions
            
        except Exception as e:
            logger.error("Failed to parse questions", error=str(e), response=response[:200])
            raise ValueError(f"Failed to parse AI response: {e}")
'''
        
        self._write_file("src/question_service/core/job_manager.py", job_manager)
        self._write_file("src/question_service/core/question_generator.py", question_generator)
        self._write_file("src/question_service/core/__init__.py", "")
        
    def create_ai_providers(self):
        """Generate AI provider interfaces and implementations"""
        
        # Base provider interface
        base_provider = '''"""Base AI provider interface"""

from abc import ABC, abstractmethod
from typing import Dict, Any

class AIProvider(ABC):
    """Abstract base class for AI providers"""
    
    @abstractmethod
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate content using AI provider"""
        pass
        
    @abstractmethod
    async def health_check(self) -> bool:
        """Check provider health"""
        pass
'''

        # Mock provider for testing
        mock_provider = '''"""Mock AI provider for testing and development"""

import asyncio
import random
import json
from typing import Dict, Any

from .base_provider import AIProvider

class MockAIProvider(AIProvider):
    """Mock provider that generates sample questions"""
    
    SAMPLE_QUESTIONS = {
        "python": [
            "What is the difference between list and tuple in Python?",
            "Explain Python's GIL (Global Interpreter Lock)",
            "How do decorators work in Python?",
            "What are Python generators and when would you use them?",
            "Explain the difference between __str__ and __repr__ methods"
        ],
        "javascript": [
            "What is the difference between let, const, and var?",
            "Explain event bubbling and capturing in JavaScript",
            "What are closures and how do they work?",
            "Describe the difference between == and === operators",
            "How does the 'this' keyword work in JavaScript?"
        ],
        "general": [
            "What are the main principles of object-oriented programming?",
            "Explain the concept of algorithm complexity (Big O notation)",
            "What is the difference between stack and heap memory?",
            "Describe common software design patterns",
            "What are the principles of RESTful API design?"
        ]
    }
    
    async def generate_content(self, prompt: str, **kwargs) -> str:
        """Generate mock questions based on prompt"""
        # Simulate API delay
        await asyncio.sleep(random.uniform(0.5, 2.0))
        
        # Simulate occasional failures
        if random.random() < 0.1:  # 10% failure rate
            raise Exception("Mock API timeout")
            
        # Extract topic from prompt
        topic = "general"
        prompt_lower = prompt.lower()
        
        for key in self.SAMPLE_QUESTIONS:
            if key in prompt_lower:
                topic = key
                break
                
        # Get random questions
        available_questions = self.SAMPLE_QUESTIONS[topic]
        selected_questions = random.sample(
            available_questions, 
            min(5, len(available_questions))
        )
        
        # Format as JSON that Claude typically produces
        questions = [
            {
                "question": q,
                "type": random.choice(["multiple_choice", "short_answer", "essay"]),
                "explanation": f"This question tests understanding of {topic.lower()} concepts."
            }
            for q in selected_questions
        ]
        
        return json.dumps(questions, indent=2)
        
    async def health_check(self) -> bool:
        """Mock health check"""
        return True
'''

        # Anthropic provider
        anthropic_provider = '''"""Anthropic Claude provider implementation"""

import anthropic
from typing import Dict, Any
import asyncio

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
                messages=[{"role": "user", "content": prompt}]
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
                messages=[{"role": "user", "content": "Test"}]
            )
            return True
        except:
            return False
'''

        # Provider factory
        provider_factory = '''"""AI provider factory"""

import os
from typing import Dict, Type

from .base_provider import AIProvider
from .mock_provider import MockAIProvider
from .anthropic_provider import AnthropicProvider

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
'''
        
        self._write_file("src/question_service/providers/base_provider.py", base_provider)
        self._write_file("src/question_service/providers/mock_provider.py", mock_provider)
        self._write_file("src/question_service/providers/anthropic_provider.py", anthropic_provider)
        self._write_file("src/question_service/providers/ai_provider.py", provider_factory)
        self._write_file("src/question_service/providers/__init__.py", "")
        
    def create_models(self):
        """Generate Pydantic models and schemas"""
        schemas = '''"""Pydantic models for API requests and responses"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class JobSubmission(BaseModel):
    """Request model for job submission"""
    topic: str = Field(..., description="Topic for question generation")
    count: int = Field(5, ge=1, le=20, description="Number of questions to generate")
    difficulty: str = Field("medium", description="Question difficulty level")
    context: Optional[str] = Field(None, description="Additional context")
    
class JobResponse(BaseModel):
    """Response model for job submission"""
    job_id: str
    status: str
    message: str
    
class Question(BaseModel):
    """Individual question model"""
    id: str
    question: str
    type: str
    difficulty: str
    topic: str
    generated_at: str
    
class QuestionResponse(BaseModel):
    """Response model for job status and results"""
    job_id: str
    status: str
    topic: Optional[str] = None
    questions: List[Question] = []
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    question_count: int = 0
    
class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None
'''
        
        self._write_file("src/question_service/models/schemas.py", schemas)
        self._write_file("src/question_service/models/__init__.py", "")
        
    def create_tests(self):
        """Generate comprehensive test suite"""
        
        # Test configuration
        conftest = '''"""Pytest configuration and fixtures"""

import pytest
import asyncio
from unittest.mock import AsyncMock
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
'''

        # Unit tests for job manager
        test_job_manager = '''"""Unit tests for job manager"""

import pytest
from unittest.mock import AsyncMock
from datetime import datetime

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
'''

        # Integration tests
        test_integration = '''"""Integration tests for question generation service"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from src.question_service.api.main import app

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)

def test_health_endpoint(client):
    """Test health check endpoint"""
    with patch('src.question_service.api.main.redis_client') as mock_redis:
        mock_redis.ping = AsyncMock(return_value=True)
        
        response = client.get("/health")
        
        assert response.status_code == 200
        assert "healthy" in response.json()["status"]

def test_generate_questions_endpoint(client):
    """Test question generation endpoint"""
    with patch('src.question_service.api.main.job_manager') as mock_manager:
        mock_manager.create_job = AsyncMock(return_value=True)
        
        response = client.post("/questions/generate", json={
            "topic": "Python programming",
            "count": 5,
            "difficulty": "medium"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"

def test_get_job_status_endpoint(client):
    """Test job status endpoint"""
    with patch('src.question_service.api.main.job_manager') as mock_manager:
        mock_manager.get_job = AsyncMock(return_value={
            "job_id": "test-123",
            "status": "completed",
            "questions": []
        })
        
        response = client.get("/questions/jobs/test-123")
        
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "test-123"
        assert data["status"] == "completed"

def test_get_job_not_found(client):
    """Test job not found"""
    with patch('src.question_service.api.main.job_manager') as mock_manager:
        mock_manager.get_job = AsyncMock(return_value=None)
        
        response = client.get("/questions/jobs/nonexistent")
        
        assert response.status_code == 404
'''

        # E2E tests
        test_e2e = '''"""End-to-end tests"""

import pytest
import asyncio
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
'''
        
        self._write_file("tests/conftest.py", conftest)
        self._write_file("tests/unit/test_job_manager.py", test_job_manager)
        self._write_file("tests/integration/test_api.py", test_integration)
        self._write_file("tests/e2e/test_full_flow.py", test_e2e)
        self._write_file("tests/__init__.py", "")
        self._write_file("tests/unit/__init__.py", "")
        self._write_file("tests/integration/__init__.py", "")
        self._write_file("tests/e2e/__init__.py", "")
        
    def create_scripts(self):
        """Generate build, test, and deployment scripts"""
        
        # Build script
        build_script = '''#!/bin/bash
# Build script for question generation service

set -e

echo "🔨 Building Question Generation Service..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Code formatting
echo "🎨 Formatting code..."
black src/ tests/
isort src/ tests/

# Type checking
echo "🔍 Type checking..."
mypy src/

# Lint
echo "🧹 Linting..."
flake8 src/ tests/ --max-line-length=88 --ignore=E203,W503

echo "✅ Build completed successfully!"
'''

        # Test script
        test_script = '''#!/bin/bash
# Test script for question generation service

set -e

echo "🧪 Running tests..."

# Unit tests
echo "🔬 Running unit tests..."
pytest tests/unit/ -v --cov=src/question_service --cov-report=term-missing

# Integration tests
echo "🔗 Running integration tests..."
pytest tests/integration/ -v

# E2E tests
echo "🌐 Running E2E tests..."
pytest tests/e2e/ -v

echo "✅ All tests passed!"
'''

        # Deploy script
        deploy_script = '''#!/bin/bash
# Deployment script

set -e

MODE=${1:-local}

echo "🚀 Deploying in $MODE mode..."

if [ "$MODE" = "docker" ]; then
    echo "🐳 Building Docker image..."
    docker build -t question-service .
    
    echo "🐳 Starting services with Docker Compose..."
    docker-compose up -d
    
    echo "⏳ Waiting for services to be ready..."
    sleep 10
    
    echo "🔍 Checking service health..."
    curl -f http://localhost:8000/health || exit 1
    
else
    echo "🏃 Starting Redis..."
    redis-server --daemonize yes
    
    echo "🗄️ Starting PostgreSQL..."
    # Note: Assumes PostgreSQL is already installed and configured
    
    echo "🌐 Starting application..."
    uvicorn src.question_service.api.main:app --host 0.0.0.0 --port 8000 --reload &
    
    # Set environment for Anthropic
    export AI_PROVIDER=anthropic
    export ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY:-"your-anthropic-api-key-here"}
    
    echo "⏳ Waiting for application to start..."
    sleep 5
    
    echo "🔍 Checking application health..."
    curl -f http://localhost:8000/health || exit 1
fi

echo "✅ Deployment completed successfully!"
'''

        self._write_file("scripts/build.sh", build_script)
        self._write_file("scripts/test.sh", test_script)
        self._write_file("scripts/deploy.sh", deploy_script)
        
        # Make scripts executable
        for script in ["build.sh", "test.sh", "deploy.sh"]:
            script_path = self.base_path / "scripts" / script
            if script_path.exists():
                script_path.chmod(0o755)
                
    def create_monitoring(self):
        """Generate monitoring and performance benchmarking"""
        
        benchmark_script = '''"""Performance benchmarking for question generation service"""

import asyncio
import time
import statistics
from typing import List
import httpx
import json

class PerformanceBenchmark:
    """Benchmark question generation service performance"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient()
        
    async def benchmark_question_generation(self, 
                                           topics: List[str], 
                                           concurrent_requests: int = 10) -> dict:
        """Benchmark question generation with concurrent requests"""
        print(f"🚀 Starting benchmark with {concurrent_requests} concurrent requests...")
        
        tasks = []
        for i in range(concurrent_requests):
            topic = topics[i % len(topics)]
            tasks.append(self._generate_questions_with_timing(topic, i))
            
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # Process results
        successful_results = [r for r in results if not isinstance(r, Exception)]
        failed_results = [r for r in results if isinstance(r, Exception)]
        
        if successful_results:
            response_times = [r['response_time'] for r in successful_results]
            generation_times = [r['generation_time'] for r in successful_results 
                              if r['generation_time'] is not None]
            
            stats = {
                "total_requests": concurrent_requests,
                "successful_requests": len(successful_results),
                "failed_requests": len(failed_results),
                "total_time": total_time,
                "requests_per_second": len(successful_results) / total_time,
                "average_response_time": statistics.mean(response_times),
                "median_response_time": statistics.median(response_times),
                "min_response_time": min(response_times),
                "max_response_time": max(response_times),
            }
            
            if generation_times:
                stats.update({
                    "average_generation_time": statistics.mean(generation_times),
                    "median_generation_time": statistics.median(generation_times),
                })
                
        else:
            stats = {
                "total_requests": concurrent_requests,
                "successful_requests": 0,
                "failed_requests": len(failed_results),
                "error": "All requests failed"
            }
            
        return stats
        
    async def _generate_questions_with_timing(self, topic: str, request_id: int) -> dict:
        """Generate questions and measure timing"""
        start_time = time.time()
        
        # Submit job
        response = await self.client.post(f"{self.base_url}/questions/generate", 
                                        json={"topic": topic, "count": 3})
        
        if response.status_code != 200:
            raise Exception(f"Failed to submit job: {response.status_code}")
            
        job_data = response.json()
        job_id = job_data["job_id"]
        
        # Poll for completion
        generation_start = time.time()
        while True:
            status_response = await self.client.get(f"{self.base_url}/questions/jobs/{job_id}")
            
            if status_response.status_code != 200:
                raise Exception(f"Failed to get job status: {status_response.status_code}")
                
            status_data = status_response.json()
            
            if status_data["status"] == "completed":
                generation_time = time.time() - generation_start
                break
            elif status_data["status"] == "failed":
                raise Exception(f"Job failed: {status_data.get('error_message', 'Unknown error')}")
                
            await asyncio.sleep(0.1)
            
        response_time = time.time() - start_time
        
        return {
            "request_id": request_id,
            "job_id": job_id,
            "topic": topic,
            "response_time": response_time,
            "generation_time": generation_time,
            "question_count": len(status_data.get("questions", []))
        }
        
    async def health_check_benchmark(self, requests: int = 100) -> dict:
        """Benchmark health check endpoint"""
        print(f"🏥 Benchmarking health check with {requests} requests...")
        
        tasks = [self._health_check_request() for _ in range(requests)]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        successful = len([r for r in results if not isinstance(r, Exception)])
        failed = len([r for r in results if isinstance(r, Exception)])
        
        return {
            "total_requests": requests,
            "successful_requests": successful,
            "failed_requests": failed,
            "total_time": total_time,
            "requests_per_second": successful / total_time,
        }
        
    async def _health_check_request(self):
        """Single health check request"""
        response = await self.client.get(f"{self.base_url}/health")
        if response.status_code != 200:
            raise Exception(f"Health check failed: {response.status_code}")
        return response.json()
        
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

async def run_benchmarks():
    """Run all benchmarks"""
    benchmark = PerformanceBenchmark()
    
    try:
        # Test topics
        topics = [
            "Python programming",
            "Machine Learning",
            "Web Development",
            "Data Structures",
            "Software Engineering"
        ]
        
        print("🔥 Performance Benchmark Results")
        print("=" * 50)
        
        # Health check benchmark
        health_stats = await benchmark.health_check_benchmark(100)
        print(f"Health Check: {health_stats['requests_per_second']:.2f} req/s")
        
        # Question generation benchmark
        gen_stats = await benchmark.benchmark_question_generation(topics, 5)
        print(f"Question Generation:")
        print(f"  - Success Rate: {gen_stats['successful_requests']}/{gen_stats['total_requests']}")
        print(f"  - Avg Response Time: {gen_stats.get('average_response_time', 0):.2f}s")
        print(f"  - Throughput: {gen_stats.get('requests_per_second', 0):.2f} req/s")
        
        return gen_stats
        
    finally:
        await benchmark.close()

if __name__ == "__main__":
    asyncio.run(run_benchmarks())
'''

        self._write_file("monitoring/benchmark.py", benchmark_script)
        
    def _write_file(self, path: str, content: str):
        """Write content to file and track for cleanup"""
        full_path = self.base_path / path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, 'w') as f:
            f.write(content)
            
        self.files_created.append(full_path)
        
    def cleanup(self):
        """Remove all created files and directories"""
        if self.base_path.exists():
            shutil.rmtree(self.base_path)
            success(f"Cleaned up project directory: {self.base_path}")

class ServiceRunner:
    """Handles service execution and testing"""
    
    def __init__(self, project_path: Path):
        self.project_path = project_path
        self.processes = []
        
    async def run_tests(self):
        """Execute test suite"""
        info("Running test suite...")
        
        # Change to project directory
        original_dir = os.getcwd()
        os.chdir(self.project_path)
        
        try:
            # Install dependencies
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                error(f"Failed to install dependencies: {result.stderr}")
                return False
                
            # Run tests
            result = subprocess.run([
                sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                success("All tests passed!")
                print(result.stdout)
                return True
            else:
                error("Some tests failed:")
                print(result.stdout)
                print(result.stderr)
                return False
                
        except Exception as e:
            error(f"Test execution failed: {e}")
            return False
        finally:
            os.chdir(original_dir)
            
    def run_local_service(self):
        """Run service locally"""
        info("Starting local service...")
        
        original_dir = os.getcwd()
        os.chdir(self.project_path)
        
        try:
            # Start Redis (if not running)
            subprocess.run(["redis-server", "--daemonize", "yes"], 
                         capture_output=True)
            
            # Start the service
            process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", 
                "src.question_service.api.main:app",
                "--host", "0.0.0.0", "--port", "8000", "--reload"
            ])
            
            self.processes.append(process)
            
            # Wait for service to start
            time.sleep(3)
            
            # Health check
            import requests
            response = requests.get("http://localhost:8000/health", timeout=5)
            
            if response.status_code == 200:
                success("Service started successfully!")
                info("Service running at http://localhost:8000")
                info("API docs at http://localhost:8000/docs")
                return True
            else:
                error("Service health check failed")
                return False
                
        except Exception as e:
            error(f"Failed to start service: {e}")
            return False
        finally:
            os.chdir(original_dir)
            
    def run_docker_service(self):
        """Run service with Docker"""
        info("Starting service with Docker...")
        
        original_dir = os.getcwd()
        os.chdir(self.project_path)
        
        try:
            # Build and start with docker-compose
            result = subprocess.run([
                "docker-compose", "up", "-d", "--build"
            ], capture_output=True, text=True)
            
            if result.returncode != 0:
                error(f"Docker compose failed: {result.stderr}")
                return False
                
            # Wait for services
            time.sleep(10)
            
            # Health check
            import requests
            response = requests.get("http://localhost:8000/health", timeout=10)
            
            if response.status_code == 200:
                success("Docker service started successfully!")
                return True
            else:
                error("Docker service health check failed")
                return False
                
        except Exception as e:
            error(f"Docker deployment failed: {e}")
            return False
        finally:
            os.chdir(original_dir)
            
    async def run_benchmark(self):
        """Run performance benchmark"""
        info("Running performance benchmark...")
        
        original_dir = os.getcwd()
        os.chdir(self.project_path)
        
        try:
            # Run benchmark
            result = subprocess.run([
                sys.executable, "monitoring/benchmark.py"
            ], capture_output=True, text=True)
            
            print(result.stdout)
            
            if result.returncode == 0:
                success("Benchmark completed successfully!")
                return True
            else:
                error("Benchmark failed:")
                print(result.stderr)
                return False
                
        except Exception as e:
            error(f"Benchmark failed: {e}")
            return False
        finally:
            os.chdir(original_dir)
            
    def cleanup(self):
        """Stop all running processes"""
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                
        # Stop Docker services if running
        try:
            subprocess.run([
                "docker-compose", "down"
            ], capture_output=True, cwd=self.project_path)
        except:
            pass

def main():
    """Main entry point with command line argument handling"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Question Generation Service Setup")
    parser.add_argument("--docker", action="store_true", help="Use Docker deployment")
    parser.add_argument("--test", action="store_true", help="Run tests only")
    parser.add_argument("--clean", action="store_true", help="Clean up project")
    parser.add_argument("--benchmark", action="store_true", help="Run benchmark")
    
    args = parser.parse_args()
    
    project_setup = ProjectSetup()
    
    if args.clean:
        project_setup.cleanup()
        return
        
    try:
        colored_print("🚀 AI Engineering Day 10: Question Generation Service", Colors.HEADER)
        colored_print("=" * 60, Colors.HEADER)
        
        # Create project structure
        project_setup.create_structure()
        project_setup.create_requirements()
        project_setup.create_dockerfile()
        project_setup.create_docker_compose()
        project_setup.create_main_app()
        project_setup.create_core_modules()
        project_setup.create_ai_providers()
        project_setup.create_models()
        project_setup.create_tests()
        project_setup.create_scripts()
        project_setup.create_monitoring()
        
        success("Project structure created successfully!")
        
        # Create service runner
        runner = ServiceRunner(project_setup.base_path)
        
        if args.test:
            # Run tests only
            asyncio.run(runner.run_tests())
        elif args.benchmark:
            # Run benchmark only (assumes service is running)
            asyncio.run(runner.run_benchmark())
        elif args.docker:
            # Docker deployment
            if runner.run_docker_service():
                info("Service is running. Press Ctrl+C to stop.")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    info("Stopping service...")
        else:
            # Local deployment
            if runner.run_local_service():
                # Run tests
                if asyncio.run(runner.run_tests()):
                    # Run benchmark
                    asyncio.run(runner.run_benchmark())
                    
                info("Service is running. Press Ctrl+C to stop.")
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    info("Stopping service...")
                    
    except KeyboardInterrupt:
        warning("Setup interrupted by user")
    except Exception as e:
        error(f"Setup failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        try:
            runner.cleanup()
        except:
            pass
            
        colored_print("Setup completed!", Colors.OKGREEN)

if __name__ == "__main__":
    main()