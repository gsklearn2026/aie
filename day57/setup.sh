#!/bin/bash

# Day 57: Production Environment Setup - Automated Implementation Script
# This script creates a complete production-ready infrastructure with auto-scaling,
# load balancing, health monitoring, and multi-environment configuration

set -e

echo "=================================================="
echo "Day 57: Production Environment Setup"
echo "Creating production-ready Quiz Platform infrastructure"
echo "=================================================="

# Create project structure
PROJECT_ROOT="quiz_platform_production"
mkdir -p $PROJECT_ROOT
cd $PROJECT_ROOT

echo "Creating directory structure..."
mkdir -p backend/app/routers backend/app/models backend/app/services backend/tests
mkdir -p frontend/src/components frontend/src/services frontend/public
mkdir -p nginx/ssl nginx/conf.d
mkdir -p monitoring/prometheus monitoring/grafana
mkdir -p scripts configs/environments

# Create environment configuration files
echo "Creating environment configurations..."

cat > configs/environments/.env.development <<'EOF'
# Development Environment
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# Database
DATABASE_URL=postgresql://quizuser:quizpass@localhost:5432/quizdb
DB_POOL_SIZE=5
DB_MAX_OVERFLOW=10

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_MAX_CONNECTIONS=10

# Gemini AI
GEMINI_API_KEY=AIzaSyDGswqDT4wQw_bd4WZtIgYAawRDZ0Gisn8
GEMINI_MODEL=gemini-2.0-flash-exp

# Server
PORT=8000
WORKERS=2
CORS_ORIGINS=http://localhost:3000

# Monitoring
ENABLE_METRICS=false
EOF

cat > configs/environments/.env.staging <<'EOF'
# Staging Environment  
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://quizuser:quizpass@postgres:5432/quizdb
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=40

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_MAX_CONNECTIONS=50

# Gemini AI
GEMINI_API_KEY=AIzaSyDGswqDT4wQw_bd4WZtIgYAawRDZ0Gisn8
GEMINI_MODEL=gemini-2.0-flash-exp

# Server
PORT=8000
WORKERS=4
CORS_ORIGINS=http://localhost:3000,https://staging.quizplatform.com

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
EOF

cat > configs/environments/.env.production <<'EOF'
# Production Environment
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING

# Database
DATABASE_URL=postgresql://quizuser:quizpass@postgres:5432/quizdb
DB_POOL_SIZE=50
DB_MAX_OVERFLOW=100

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_MAX_CONNECTIONS=100

# Gemini AI
GEMINI_API_KEY=AIzaSyDGswqDT4wQw_bd4WZtIgYAawRDZ0Gisn8
GEMINI_MODEL=gemini-2.0-flash-exp

# Server
PORT=8000
WORKERS=8
CORS_ORIGINS=https://quizplatform.com

# Security
FORCE_HTTPS=true
HSTS_ENABLED=true

# Auto-scaling
MIN_INSTANCES=2
MAX_INSTANCES=10
SCALE_UP_CPU_THRESHOLD=70
SCALE_DOWN_CPU_THRESHOLD=30

# Monitoring
ENABLE_METRICS=true
METRICS_PORT=9090
ALERT_EMAIL=ops@quizplatform.com
EOF

# Backend implementation
echo "Creating backend application..."

cat > backend/requirements.txt <<'EOF'
fastapi==0.115.0
uvicorn[standard]==0.32.0
sqlalchemy==2.0.36
asyncpg==0.30.0
psycopg2-binary==2.9.10
redis==5.2.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.12
google-generativeai==0.8.3
prometheus-client==0.21.0
python-dotenv==1.0.1
pydantic==2.10.2
pydantic-settings==2.6.1
httpx==0.27.2
pytest==8.3.3
pytest-asyncio==0.24.0
EOF

cat > backend/app/__init__.py <<'EOF'
"""Quiz Platform Production Backend"""
__version__ = "1.0.0"
EOF

cat > backend/app/config.py <<'EOF'
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Environment
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Database
    database_url: str
    db_pool_size: int = 20
    db_max_overflow: int = 40
    
    # Redis
    redis_url: str
    redis_max_connections: int = 50
    
    # Gemini AI
    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash-exp"
    
    # Server
    port: int = 8000
    workers: int = 4
    cors_origins: str = "*"
    
    # Security
    force_https: bool = False
    hsts_enabled: bool = False
    
    # Auto-scaling
    min_instances: int = 2
    max_instances: int = 10
    scale_up_cpu_threshold: int = 70
    scale_down_cpu_threshold: int = 30
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()
EOF

cat > backend/app/database.py <<'EOF'
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import pool
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

# Create async engine with connection pooling
engine = create_async_engine(
    settings.database_url.replace("postgresql://", "postgresql+asyncpg://"),
    poolclass=pool.QueuePool,
    pool_size=settings.db_pool_size,
    max_overflow=settings.db_max_overflow,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=settings.debug
)

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    """Dependency for getting database sessions"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database initialized successfully")

async def check_db_health():
    """Check database connectivity"""
    try:
        async with async_session_maker() as session:
            await session.execute("SELECT 1")
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return False
EOF

cat > backend/app/cache.py <<'EOF'
import redis.asyncio as redis
from app.config import get_settings
import json
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class CacheManager:
    def __init__(self):
        self.redis_client = None
    
    async def connect(self):
        """Initialize Redis connection pool"""
        self.redis_client = await redis.from_url(
            settings.redis_url,
            max_connections=settings.redis_max_connections,
            decode_responses=True
        )
        logger.info("Redis cache connected")
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def get(self, key: str):
        """Get value from cache"""
        try:
            value = await self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: any, ttl: int = 3600):
        """Set value in cache with TTL"""
        try:
            await self.redis_client.setex(
                key,
                ttl,
                json.dumps(value)
            )
        except Exception as e:
            logger.error(f"Cache set error: {e}")
    
    async def delete(self, key: str):
        """Delete key from cache"""
        try:
            await self.redis_client.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
    
    async def check_health(self):
        """Check Redis connectivity"""
        try:
            await self.redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False

cache_manager = CacheManager()
EOF

cat > backend/app/monitoring.py <<'EOF'
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
import time
import psutil
import logging

logger = logging.getLogger(__name__)

# Metrics
request_count = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

request_duration = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

active_requests = Gauge(
    'http_requests_active',
    'Number of active HTTP requests'
)

cpu_usage = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)

memory_usage = Gauge(
    'system_memory_usage_percent',
    'System memory usage percentage'
)

db_connections = Gauge(
    'database_connections_active',
    'Active database connections'
)

cache_hits = Counter(
    'cache_hits_total',
    'Total cache hits'
)

cache_misses = Counter(
    'cache_misses_total',
    'Total cache misses'
)

ai_requests = Counter(
    'ai_requests_total',
    'Total AI generation requests',
    ['status']
)

ai_request_duration = Histogram(
    'ai_request_duration_seconds',
    'AI request latency'
)

class MetricsMiddleware:
    """Middleware to track request metrics"""
    
    async def __call__(self, request, call_next):
        active_requests.inc()
        start_time = time.time()
        
        response = await call_next(request)
        
        duration = time.time() - start_time
        active_requests.dec()
        
        request_count.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        
        request_duration.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        return response

def update_system_metrics():
    """Update system resource metrics"""
    try:
        cpu_usage.set(psutil.cpu_percent())
        memory_usage.set(psutil.virtual_memory().percent)
    except Exception as e:
        logger.error(f"Failed to update system metrics: {e}")

async def get_metrics():
    """Generate Prometheus metrics"""
    update_system_metrics()
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
EOF

cat > backend/app/health.py <<'EOF'
from fastapi import APIRouter, status
from app.database import check_db_health
from app.cache import cache_manager
import psutil
from datetime import datetime

router = APIRouter()

@router.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "quiz-platform"
    }

@router.get("/health/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """Deep health check - verify all dependencies"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    # Check database
    db_healthy = await check_db_health()
    health_status["checks"]["database"] = "healthy" if db_healthy else "unhealthy"
    
    # Check cache
    cache_healthy = await cache_manager.check_health()
    health_status["checks"]["cache"] = "healthy" if cache_healthy else "unhealthy"
    
    # Check system resources
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    disk_percent = psutil.disk_usage('/').percent
    
    health_status["checks"]["resources"] = {
        "cpu_usage": f"{cpu_percent}%",
        "memory_usage": f"{memory_percent}%",
        "disk_usage": f"{disk_percent}%"
    }
    
    # Determine overall status
    if not (db_healthy and cache_healthy):
        health_status["status"] = "unhealthy"
        return health_status
    
    if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
        health_status["status"] = "degraded"
    
    return health_status

@router.get("/health/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """Liveness check - is the service running"""
    return {"status": "alive"}
EOF

cat > backend/app/models/quiz.py <<'EOF'
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.database import Base

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(100), index=True)
    difficulty = Column(String(50), index=True)
    questions = Column(JSONB, nullable=False)
    total_questions = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True, index=True)
    
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "difficulty": self.difficulty,
            "questions": self.questions,
            "total_questions": self.total_questions,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active
        }
EOF

cat > backend/app/services/ai_service.py <<'EOF'
import google.generativeai as genai
from app.config import get_settings
from app.monitoring import ai_requests, ai_request_duration
import time
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

genai.configure(api_key=settings.gemini_api_key)

class AIService:
    def __init__(self):
        self.model = genai.GenerativeModel(settings.gemini_model)
    
    async def generate_quiz(self, topic: str, num_questions: int = 5):
        """Generate quiz questions using AI"""
        start_time = time.time()
        
        try:
            prompt = f"""Generate {num_questions} multiple-choice quiz questions about {topic}.
            
Return a JSON array with this exact structure:
[
  {{
    "question": "question text",
    "options": ["option1", "option2", "option3", "option4"],
    "correct_answer": 0,
    "explanation": "why this is correct"
  }}
]

Make questions challenging but fair. Include detailed explanations."""
            
            response = self.model.generate_content(prompt)
            duration = time.time() - start_time
            
            ai_requests.labels(status="success").inc()
            ai_request_duration.observe(duration)
            
            # Parse response
            import json
            text = response.text
            # Clean markdown code blocks if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            questions = json.loads(text.strip())
            return questions
            
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            ai_requests.labels(status="error").inc()
            raise
EOF

cat > backend/app/routers/quiz.py <<'EOF'
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.cache import cache_manager
from app.models.quiz import Quiz
from app.services.ai_service import AIService
from app.monitoring import cache_hits, cache_misses
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/api/v1/quizzes", tags=["quizzes"])
ai_service = AIService()

class QuizCreate(BaseModel):
    topic: str
    num_questions: int = 5
    difficulty: str = "medium"
    category: Optional[str] = None

class QuizResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    category: Optional[str]
    difficulty: str
    questions: list
    total_questions: int
    created_at: str

@router.post("/generate", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def generate_quiz(
    quiz_data: QuizCreate,
    db: AsyncSession = Depends(get_db)
):
    """Generate a new quiz using AI"""
    try:
        # Generate questions
        questions = await ai_service.generate_quiz(
            quiz_data.topic,
            quiz_data.num_questions
        )
        
        # Create quiz record
        quiz = Quiz(
            title=f"{quiz_data.topic} Quiz",
            description=f"AI-generated quiz about {quiz_data.topic}",
            category=quiz_data.category or quiz_data.topic,
            difficulty=quiz_data.difficulty,
            questions=questions,
            total_questions=len(questions)
        )
        
        db.add(quiz)
        await db.commit()
        await db.refresh(quiz)
        
        # Cache the quiz
        await cache_manager.set(f"quiz:{quiz.id}", quiz.to_dict(), ttl=3600)
        
        return quiz.to_dict()
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate quiz: {str(e)}"
        )

@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get quiz by ID with caching"""
    # Check cache first
    cache_key = f"quiz:{quiz_id}"
    cached_quiz = await cache_manager.get(cache_key)
    
    if cached_quiz:
        cache_hits.inc()
        return cached_quiz
    
    cache_misses.inc()
    
    # Fetch from database
    result = await db.execute(
        select(Quiz).where(Quiz.id == quiz_id, Quiz.is_active == True)
    )
    quiz = result.scalar_one_or_none()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    quiz_dict = quiz.to_dict()
    await cache_manager.set(cache_key, quiz_dict, ttl=3600)
    
    return quiz_dict

@router.get("/", response_model=List[QuizResponse])
async def list_quizzes(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List quizzes with pagination and filtering"""
    query = select(Quiz).where(Quiz.is_active == True)
    
    if category:
        query = query.where(Quiz.category == category)
    
    query = query.offset(skip).limit(limit).order_by(Quiz.created_at.desc())
    
    result = await db.execute(query)
    quizzes = result.scalars().all()
    
    return [quiz.to_dict() for quiz in quizzes]
EOF

cat > backend/app/main.py <<'EOF'
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import sys

from app.config import get_settings
from app.database import init_db
from app.cache import cache_manager
from app.monitoring import MetricsMiddleware, get_metrics
from app.health import router as health_router
from app.routers import quiz

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info(f"Starting Quiz Platform - Environment: {settings.environment}")
    
    # Initialize database
    await init_db()
    
    # Connect to Redis
    await cache_manager.connect()
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    await cache_manager.disconnect()
    logger.info("Application shutdown complete")

# Create FastAPI application
app = FastAPI(
    title="Quiz Platform API",
    description="Production-ready Quiz Platform with AI generation",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)
app.middleware("http")(MetricsMiddleware())

# Add routers
app.include_router(health_router)
app.include_router(quiz.router)

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    if settings.enable_metrics:
        return await get_metrics()
    return JSONResponse({"error": "Metrics disabled"}, status_code=404)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Quiz Platform API",
        "version": "1.0.0",
        "environment": settings.environment,
        "status": "running"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error" if not settings.debug else str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        workers=settings.workers,
        log_level=settings.log_level.lower()
    )
EOF

# Frontend implementation
echo "Creating frontend application..."

cat > frontend/package.json <<'EOF'
{
  "name": "quiz-platform-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "axios": "^1.7.7",
    "@mui/material": "^6.1.0",
    "@mui/icons-material": "^6.1.0",
    "@emotion/react": "^11.13.3",
    "@emotion/styled": "^11.13.0",
    "recharts": "^2.12.7",
    "react-scripts": "5.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": ["react-app"]
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  }
}
EOF

cat > frontend/public/index.html <<'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Production-ready Quiz Platform" />
    <title>Quiz Platform - Production</title>
</head>
<body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
</body>
</html>
EOF

cat > frontend/src/config.js <<'EOF'
const config = {
  development: {
    apiUrl: 'http://localhost:8000'
  },
  staging: {
    apiUrl: 'http://localhost:8001'
  },
  production: {
    apiUrl: 'https://api.quizplatform.com'
  }
};

const environment = process.env.REACT_APP_ENV || 'development';
export default config[environment];
EOF

cat > frontend/src/services/api.js <<'EOF'
import axios from 'axios';
import config from '../config';

const api = axios.create({
  baseURL: config.apiUrl,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error('API Error:', error.response.data);
    } else if (error.request) {
      console.error('Network Error:', error.message);
    }
    return Promise.reject(error);
  }
);

export const quizService = {
  generateQuiz: async (data) => {
    const response = await api.post('/api/v1/quizzes/generate', data);
    return response.data;
  },
  
  getQuiz: async (id) => {
    const response = await api.get(`/api/v1/quizzes/${id}`);
    return response.data;
  },
  
  listQuizzes: async (params = {}) => {
    const response = await api.get('/api/v1/quizzes/', { params });
    return response.data;
  }
};

export const healthService = {
  checkHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  },
  
  checkReadiness: async () => {
    const response = await api.get('/health/ready');
    return response.data;
  }
};

export default api;
EOF

cat > frontend/src/components/Dashboard.js <<'EOF'
import React, { useState, useEffect } from 'react';
import {
  Container, Paper, Typography, Grid, Card, CardContent,
  Button, TextField, CircularProgress, Alert, Chip, Box
} from '@mui/material';
import {
  Speed as SpeedIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Storage as StorageIcon
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { quizService, healthService } from '../services/api';

function Dashboard() {
  const [health, setHealth] = useState(null);
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [topic, setTopic] = useState('');
  const [metrics, setMetrics] = useState([]);

  useEffect(() => {
    fetchHealth();
    fetchQuizzes();
    const interval = setInterval(fetchHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchHealth = async () => {
    try {
      const data = await healthService.checkReadiness();
      setHealth(data);
      
      // Update metrics
      setMetrics(prev => [...prev, {
        time: new Date().toLocaleTimeString(),
        status: data.status === 'healthy' ? 100 : 0
      }].slice(-20));
    } catch (err) {
      console.error('Health check failed:', err);
    }
  };

  const fetchQuizzes = async () => {
    try {
      const data = await quizService.listQuizzes({ limit: 10 });
      setQuizzes(data);
    } catch (err) {
      console.error('Failed to fetch quizzes:', err);
    }
  };

  const handleGenerateQuiz = async () => {
    if (!topic.trim()) {
      setError('Please enter a topic');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      await quizService.generateQuiz({
        topic: topic,
        num_questions: 5,
        difficulty: 'medium'
      });
      setTopic('');
      fetchQuizzes();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate quiz');
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    if (status === 'healthy') return 'success';
    if (status === 'degraded') return 'warning';
    return 'error';
  };

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h3" gutterBottom>
        Production Dashboard
      </Typography>

      {/* Health Status */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography color="textSecondary" gutterBottom>
                  System Status
                </Typography>
                {health?.status === 'healthy' ? <CheckIcon color="success" /> : <ErrorIcon color="error" />}
              </Box>
              <Typography variant="h5">
                {health?.status || 'Unknown'}
              </Typography>
              <Chip 
                label={health?.status || 'Checking'}
                color={getStatusColor(health?.status)}
                size="small"
                sx={{ mt: 1 }}
              />
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography color="textSecondary" gutterBottom>
                  Database
                </Typography>
                <StorageIcon color="primary" />
              </Box>
              <Typography variant="h5">
                {health?.checks?.database || 'N/A'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Typography color="textSecondary" gutterBottom>
                  Cache
                </Typography>
                <SpeedIcon color="primary" />
              </Box>
              <Typography variant="h5">
                {health?.checks?.cache || 'N/A'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                CPU Usage
              </Typography>
              <Typography variant="h5">
                {health?.checks?.resources?.cpu_usage || 'N/A'}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Metrics Chart */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          System Health Timeline
        </Typography>
        <ResponsiveContainer width="100%" height={200}>
          <LineChart data={metrics}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="time" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="status" stroke="#4caf50" name="Health %" />
          </LineChart>
        </ResponsiveContainer>
      </Paper>

      {/* Quiz Generation */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Generate New Quiz
        </Typography>
        <Box display="flex" gap={2} alignItems="center">
          <TextField
            fullWidth
            label="Topic"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g., Python Programming"
            disabled={loading}
          />
          <Button
            variant="contained"
            onClick={handleGenerateQuiz}
            disabled={loading}
            sx={{ minWidth: 120 }}
          >
            {loading ? <CircularProgress size={24} /> : 'Generate'}
          </Button>
        </Box>
        {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
      </Paper>

      {/* Quiz List */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Recent Quizzes ({quizzes.length})
        </Typography>
        <Grid container spacing={2}>
          {quizzes.map((quiz) => (
            <Grid item xs={12} md={6} key={quiz.id}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6">{quiz.title}</Typography>
                  <Typography color="textSecondary" variant="body2">
                    {quiz.description}
                  </Typography>
                  <Box mt={1}>
                    <Chip label={quiz.category} size="small" sx={{ mr: 1 }} />
                    <Chip label={quiz.difficulty} size="small" color="primary" sx={{ mr: 1 }} />
                    <Chip label={`${quiz.total_questions} questions`} size="small" />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Paper>
    </Container>
  );
}

export default Dashboard;
EOF

cat > frontend/src/App.js <<'EOF'
import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Dashboard from './components/Dashboard';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Dashboard />
    </ThemeProvider>
  );
}

export default App;
EOF

cat > frontend/src/index.js <<'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

# Nginx configuration
echo "Creating Nginx load balancer configuration..."

cat > nginx/nginx.conf <<'EOF'
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 2048;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss;

    # Upstream backend servers
    upstream backend {
        least_conn;  # Load balancing algorithm
        
        server backend1:8000 max_fails=3 fail_timeout=30s;
        server backend2:8000 max_fails=3 fail_timeout=30s;
        server backend3:8000 max_fails=3 fail_timeout=30s;
    }

    # Health check endpoint
    server {
        listen 8080;
        
        location /nginx-health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }

    # Main server
    server {
        listen 80;
        server_name localhost;

        # Frontend
        location / {
            root /usr/share/nginx/html;
            index index.html;
            try_files $uri $uri/ /index.html;
        }

        # API proxy
        location /api/ {
            proxy_pass http://backend;
            proxy_http_version 1.1;
            
            # Headers
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
            
            # Buffering
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
            proxy_busy_buffers_size 8k;
        }

        # Health endpoints
        location /health {
            proxy_pass http://backend;
            access_log off;
        }

        # Metrics endpoint
        location /metrics {
            proxy_pass http://backend;
            access_log off;
        }
    }
}
EOF

# Prometheus configuration
echo "Creating monitoring configuration..."

cat > monitoring/prometheus/prometheus.yml <<'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'quiz-platform'
    static_configs:
      - targets: ['backend1:8000', 'backend2:8000', 'backend3:8000']
        labels:
          service: 'backend'
      
      - targets: ['nginx:8080']
        labels:
          service: 'loadbalancer'
    
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
EOF

# Docker Compose configuration
echo "Creating Docker Compose orchestration..."

cat > docker-compose.yml <<'EOF'
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:16-alpine
    container_name: quiz_postgres
    environment:
      POSTGRES_USER: quizuser
      POSTGRES_PASSWORD: quizpass
      POSTGRES_DB: quizdb
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U quizuser"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - quiz_network

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: quiz_redis
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - quiz_network

  # Backend Instance 1
  backend1:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: quiz_backend1
    env_file:
      - ./configs/environments/.env.production
    environment:
      - DATABASE_URL=postgresql://quizuser:quizpass@postgres:5432/quizdb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    networks:
      - quiz_network
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  # Backend Instance 2
  backend2:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: quiz_backend2
    env_file:
      - ./configs/environments/.env.production
    environment:
      - DATABASE_URL=postgresql://quizuser:quizpass@postgres:5432/quizdb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    networks:
      - quiz_network
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  # Backend Instance 3
  backend3:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: quiz_backend3
    env_file:
      - ./configs/environments/.env.production
    environment:
      - DATABASE_URL=postgresql://quizuser:quizpass@postgres:5432/quizdb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    networks:
      - quiz_network
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M

  # Nginx Load Balancer
  nginx:
    image: nginx:1.27-alpine
    container_name: quiz_nginx
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./frontend/build:/usr/share/nginx/html:ro
    ports:
      - "80:80"
      - "8080:8080"
    depends_on:
      - backend1
      - backend2
      - backend3
    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:8080/nginx-health"]
      interval: 30s
      timeout: 10s
      retries: 3
    restart: unless-stopped
    networks:
      - quiz_network

  # Prometheus Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: quiz_prometheus
    volumes:
      - ./monitoring/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - quiz_network
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  prometheus_data:

networks:
  quiz_network:
    driver: bridge
EOF

# Backend Dockerfile
cat > backend/Dockerfile <<'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Build and deployment scripts
echo "Creating build and deployment scripts..."

cat > build.sh <<'EOF'
#!/bin/bash

set -e

echo "=== Quiz Platform Production Build ==="
echo ""
echo "Choose build option:"
echo "1) Build with Docker"
echo "2) Build without Docker (local)"
echo ""
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo "Building with Docker..."
        
        # Build backend Docker image
        echo "Building backend..."
        cd backend
        docker build -t quiz-backend:latest .
        cd ..
        
        # Build frontend
        echo "Building frontend..."
        cd frontend
        npm install
        npm run build
        cd ..
        
        # Build and start services
        echo "Starting services with Docker Compose..."
        docker-compose up -d
        
        echo "Waiting for services to be healthy..."
        sleep 30
        
        echo ""
        echo "=== Build Complete ==="
        echo "Services running:"
        docker-compose ps
        echo ""
        echo "Access points:"
        echo "- Frontend: http://localhost:80"
        echo "- API: http://localhost:80/api/"
        echo "- Health: http://localhost:80/health"
        echo "- Prometheus: http://localhost:9090"
        ;;
        
    2)
        echo "Building without Docker (local)..."
        
        # Setup backend
        echo "Setting up backend..."
        cd backend
        python3 -m venv venv
        source venv/bin/activate
        pip install -r requirements.txt
        
        # Copy development environment
        cp ../configs/environments/.env.development .env
        
        echo "Backend setup complete"
        cd ..
        
        # Setup frontend
        echo "Setting up frontend..."
        cd frontend
        npm install
        echo "REACT_APP_ENV=development" > .env
        npm run build
        cd ..
        
        echo ""
        echo "=== Build Complete (Local) ==="
        echo "To start services:"
        echo "1. Start PostgreSQL and Redis locally"
        echo "2. Run: ./start.sh"
        ;;
        
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
EOF

cat > start.sh <<'EOF'
#!/bin/bash

set -e

echo "=== Starting Quiz Platform ==="
echo ""
echo "Choose startup option:"
echo "1) Start with Docker"
echo "2) Start without Docker (local)"
echo ""
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo "Starting with Docker Compose..."
        docker-compose up -d
        
        echo "Waiting for services..."
        sleep 20
        
        echo ""
        echo "=== Services Started ==="
        docker-compose ps
        echo ""
        echo "Access points:"
        echo "- Frontend: http://localhost:80"
        echo "- API Health: http://localhost:80/health"
        echo "- Metrics: http://localhost:9090"
        
        echo ""
        echo "View logs:"
        echo "  docker-compose logs -f"
        ;;
        
    2)
        echo "Starting services locally..."
        
        # Start backend
        echo "Starting backend..."
        cd backend
        source venv/bin/activate
        python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
        BACKEND_PID=$!
        cd ..
        
        # Start frontend
        echo "Starting frontend..."
        cd frontend
        REACT_APP_ENV=development npm start &
        FRONTEND_PID=$!
        cd ..
        
        echo ""
        echo "=== Services Started (Local) ==="
        echo "Backend PID: $BACKEND_PID"
        echo "Frontend PID: $FRONTEND_PID"
        echo ""
        echo "Access points:"
        echo "- Frontend: http://localhost:3000"
        echo "- API: http://localhost:8000"
        echo "- Health: http://localhost:8000/health"
        
        echo ""
        echo "To stop services: ./stop.sh"
        
        # Save PIDs
        echo $BACKEND_PID > .backend.pid
        echo $FRONTEND_PID > .frontend.pid
        ;;
        
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
EOF

cat > stop.sh <<'EOF'
#!/bin/bash

echo "=== Stopping Quiz Platform ==="

if [ -f ".backend.pid" ]; then
    echo "Stopping local services..."
    kill $(cat .backend.pid) 2>/dev/null || true
    kill $(cat .frontend.pid) 2>/dev/null || true
    rm -f .backend.pid .frontend.pid
    echo "Local services stopped"
else
    echo "Stopping Docker services..."
    docker-compose down
    echo "Docker services stopped"
fi
EOF

chmod +x build.sh start.sh stop.sh

# Testing
echo "Creating test suite..."

cat > backend/tests/test_production.py <<'EOF'
import pytest
import httpx
from app.main import app
from app.config import get_settings

settings = get_settings()

@pytest.mark.asyncio
async def test_health_check():
    """Test basic health endpoint"""
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_readiness_check():
    """Test deep health check"""
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health/ready")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint"""
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Quiz Platform API"
        assert data["environment"] == settings.environment
EOF

cat > backend/pytest.ini <<'EOF'
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
EOF

# README
cat > README.md <<'EOF'
# Quiz Platform - Production Environment

Production-ready Quiz Platform with auto-scaling, load balancing, and comprehensive monitoring.

## Architecture

- **Load Balancer**: Nginx (least connections algorithm)
- **Backend**: 3 FastAPI instances with auto-scaling
- **Database**: PostgreSQL with connection pooling
- **Cache**: Redis cluster
- **Monitoring**: Prometheus metrics collection
- **Container Orchestration**: Docker Compose

## Quick Start

### With Docker (Recommended)
```bash
./build.sh  # Choose option 1
./start.sh  # Choose option 1
```

### Without Docker
```bash
./build.sh  # Choose option 2
# Start PostgreSQL and Redis separately
./start.sh  # Choose option 2
```

## Access Points

- Frontend: http://localhost:80
- API: http://localhost:80/api/
- Health Check: http://localhost:80/health
- Metrics: http://localhost:9090

## Monitoring

View Prometheus metrics:
```bash
open http://localhost:9090
```

View container logs:
```bash
docker-compose logs -f
```

## Testing

Run tests:
```bash
cd backend
source venv/bin/activate
pytest -v
```

## Scaling

Manual scaling:
```bash
docker-compose up -d --scale backend=5
```

## Stopping Services

```bash
./stop.sh
```

## Production Deployment

1. Update environment configs in `configs/environments/`
2. Configure SSL certificates in `nginx/ssl/`
3. Set production database credentials
4. Deploy using container orchestration (Kubernetes, ECS, etc.)

## Health Checks

- **Liveness**: `/health/live` - Is service running?
- **Readiness**: `/health/ready` - Can service handle requests?
- **Deep Health**: `/health` - Check all dependencies

## Environment Variables

See `configs/environments/` for different environment configurations:
- `.env.development` - Local development
- `.env.staging` - Staging environment
- `.env.production` - Production environment
EOF

echo ""
echo "=========================================="
echo "✅ Production Environment Setup Complete!"
echo "=========================================="
echo ""
echo "Project structure created in: $PROJECT_ROOT"
echo ""
echo "Next steps:"
echo "1. cd $PROJECT_ROOT"
echo "2. ./build.sh (choose Docker or local)"
echo "3. ./start.sh (start services)"
echo "4. Open http://localhost:80"
echo ""
echo "Files created:"
echo "- Backend API with health checks"
echo "- Frontend dashboard with monitoring"
echo "- Nginx load balancer configuration"
echo "- Docker Compose orchestration"
echo "- Prometheus monitoring setup"
echo "- Multi-environment configurations"
echo "- Build and deployment scripts"
echo ""
echo "Happy deploying! 🚀"