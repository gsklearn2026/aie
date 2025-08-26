#!/bin/bash

# Day 22: Caching Strategy Implementation - Full Project Setup Script
# This script creates the complete project structure with Redis caching

set -e  # Exit on any error

echo "🚀 Day 22: Setting up Caching Strategy Implementation..."

# Create main project directory
PROJECT_ROOT="day22_caching_implementation"
mkdir -p $PROJECT_ROOT
cd $PROJECT_ROOT

echo "📁 Creating project structure..."

# Backend structure
mkdir -p backend/{src/{api,models,services,cache,config,tests},static}
mkdir -p backend/src/api/{routes,middleware}
mkdir -p backend/src/tests/{unit,integration}

# Frontend structure  
mkdir -p frontend/{src/{components,services,hooks,styles},public}
mkdir -p frontend/src/components/{Quiz,Dashboard,Common}

# Docker and config
mkdir -p docker configs scripts

echo "📄 Creating configuration files..."

# Docker Compose for Redis and services
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  redis:
    image: redis:7.2-alpine
    container_name: quiz_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
      - ./configs/redis.conf:/usr/local/etc/redis/redis.conf
    command: redis-server /usr/local/etc/redis/redis.conf
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 3

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: quiz_backend
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: quiz_frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend

volumes:
  redis_data:
EOF

# Redis configuration
cat > configs/redis.conf << 'EOF'
# Redis Configuration for Quiz Platform Caching

# Memory and persistence
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000

# Network
bind 0.0.0.0
port 6379
timeout 300
tcp-keepalive 300

# Logging
loglevel notice
logfile ""

# Performance
tcp-backlog 511
databases 16
EOF

echo "🐍 Setting up Python backend..."

# Backend Dockerfile
cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE 8000
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Python requirements
cat > backend/requirements.txt << 'EOF'
fastapi==0.110.2
uvicorn[standard]==0.29.0
redis==5.0.4
pydantic==2.7.1
python-multipart==0.0.9
google-generativeai==0.5.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pytest==8.2.0
pytest-asyncio==0.23.6
httpx==0.27.0
python-dotenv==1.0.1
structlog==24.1.0
prometheus-client==0.20.0
aioredis==2.0.1
EOF

# Main FastAPI application
cat > backend/src/main.py << 'EOF'
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import structlog
from contextlib import asynccontextmanager

from .config.settings import get_settings
from .cache.redis_client import get_redis_client
from .api.routes import quiz_routes, cache_routes
from .api.middleware.cache_middleware import CacheMiddleware

settings = get_settings()
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Quiz Platform with Caching...")
    redis_client = await get_redis_client()
    await redis_client.ping()
    logger.info("Redis connection established")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")

app = FastAPI(
    title="Quiz Platform with Caching",
    description="Day 22: Advanced caching implementation",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom cache middleware
app.add_middleware(CacheMiddleware)

# Include routers
app.include_router(quiz_routes.router, prefix="/api/v1")
app.include_router(cache_routes.router, prefix="/api/v1/cache")

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head><title>Quiz Platform Cache Demo</title></head>
        <body>
            <h1>🚀 Quiz Platform with Redis Caching</h1>
            <p>Day 22 Implementation Running!</p>
            <ul>
                <li><a href="/docs">API Documentation</a></li>
                <li><a href="/api/v1/cache/stats">Cache Statistics</a></li>
                <li><a href="http://localhost:3000">Frontend Dashboard</a></li>
            </ul>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    redis_client = await get_redis_client()
    redis_status = "healthy" if await redis_client.ping() else "unhealthy"
    
    return {
        "status": "healthy",
        "redis": redis_status,
        "cache_enabled": True
    }
EOF

# Settings configuration
cat > backend/src/config/settings.py << 'EOF'
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    redis_url: str = "redis://localhost:6379"
    gemini_api_key: str = "your-gemini-api-key"
    cache_default_ttl: int = 3600  # 1 hour
    cache_quiz_ttl: int = 3600     # 1 hour
    cache_user_progress_ttl: int = 1800  # 30 minutes
    cache_leaderboard_ttl: int = 300     # 5 minutes
    cache_learning_path_ttl: int = 86400 # 24 hours
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
EOF

# Redis client
cat > backend/src/cache/redis_client.py << 'EOF'
import redis.asyncio as redis
import json
import structlog
from typing import Optional, Any, Dict
from ..config.settings import get_settings

logger = structlog.get_logger()
settings = get_settings()

class RedisClient:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        self.hit_count = 0
        self.miss_count = 0
    
    async def connect(self):
        self.redis = redis.from_url(
            settings.redis_url,
            encoding="utf8",
            decode_responses=True,
            max_connections=20
        )
        await self.redis.ping()
        logger.info("Redis connected successfully")
    
    async def get(self, key: str) -> Optional[Any]:
        if not self.redis:
            await self.connect()
        
        try:
            value = await self.redis.get(key)
            if value:
                self.hit_count += 1
                logger.debug("Cache hit", key=key)
                return json.loads(value)
            else:
                self.miss_count += 1
                logger.debug("Cache miss", key=key)
                return None
        except Exception as e:
            logger.error("Redis get error", key=key, error=str(e))
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> bool:
        if not self.redis:
            await self.connect()
        
        try:
            ttl = ttl or settings.cache_default_ttl
            await self.redis.setex(key, ttl, json.dumps(value, default=str))
            logger.debug("Cache set", key=key, ttl=ttl)
            return True
        except Exception as e:
            logger.error("Redis set error", key=key, error=str(e))
            return False
    
    async def delete(self, key: str) -> bool:
        if not self.redis:
            await self.connect()
        
        try:
            result = await self.redis.delete(key)
            logger.debug("Cache delete", key=key, deleted=bool(result))
            return bool(result)
        except Exception as e:
            logger.error("Redis delete error", key=key, error=str(e))
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        if not self.redis:
            await self.connect()
        
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                deleted = await self.redis.delete(*keys)
                logger.info("Pattern invalidated", pattern=pattern, count=deleted)
                return deleted
            return 0
        except Exception as e:
            logger.error("Pattern invalidation error", pattern=pattern, error=str(e))
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        if not self.redis:
            await self.connect()
        
        info = await self.redis.info()
        hit_rate = self.hit_count / (self.hit_count + self.miss_count) if (self.hit_count + self.miss_count) > 0 else 0
        
        return {
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "hit_rate": f"{hit_rate:.2%}",
            "connected_clients": info.get("connected_clients", 0),
            "used_memory_human": info.get("used_memory_human", "0B"),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0)
        }

# Global redis client instance
_redis_client = RedisClient()

async def get_redis_client() -> RedisClient:
    if not _redis_client.redis:
        await _redis_client.connect()
    return _redis_client
EOF

# Cache service
cat > backend/src/services/cache_service.py << 'EOF'
from typing import Optional, Any, List, Dict, Callable
import structlog
from ..cache.redis_client import get_redis_client
from ..config.settings import get_settings

logger = structlog.get_logger()
settings = get_settings()

class CacheService:
    def __init__(self):
        self.redis_client = None
    
    async def _get_redis(self):
        if not self.redis_client:
            self.redis_client = await get_redis_client()
        return self.redis_client
    
    async def get_or_set(
        self, 
        key: str, 
        fetch_func: Callable, 
        ttl: int = None,
        *args, 
        **kwargs
    ) -> Any:
        """Cache-aside pattern implementation"""
        redis = await self._get_redis()
        
        # Try to get from cache first
        cached_value = await redis.get(key)
        if cached_value is not None:
            return cached_value
        
        # Cache miss - fetch from source
        fresh_value = await fetch_func(*args, **kwargs)
        
        # Set in cache for next time
        if fresh_value is not None:
            await redis.set(key, fresh_value, ttl)
        
        return fresh_value
    
    async def invalidate_quiz_cache(self, quiz_id: str):
        """Invalidate all cache entries related to a quiz"""
        redis = await self._get_redis()
        patterns = [
            f"quiz:{quiz_id}",
            f"quiz:{quiz_id}:*",
            f"user_progress:*:{quiz_id}",
            f"leaderboard:{quiz_id}:*"
        ]
        
        total_deleted = 0
        for pattern in patterns:
            deleted = await redis.invalidate_pattern(pattern)
            total_deleted += deleted
        
        logger.info("Quiz cache invalidated", quiz_id=quiz_id, deleted_keys=total_deleted)
        return total_deleted
    
    async def cache_quiz(self, quiz_id: str, quiz_data: Dict) -> bool:
        """Cache quiz data with appropriate TTL"""
        redis = await self._get_redis()
        key = f"quiz:{quiz_id}"
        return await redis.set(key, quiz_data, settings.cache_quiz_ttl)
    
    async def cache_user_progress(self, user_id: str, quiz_id: str, progress_data: Dict) -> bool:
        """Cache user progress data"""
        redis = await self._get_redis()
        key = f"user_progress:{user_id}:{quiz_id}"
        return await redis.set(key, progress_data, settings.cache_user_progress_ttl)
    
    async def cache_leaderboard(self, quiz_id: str, leaderboard_data: List) -> bool:
        """Cache leaderboard data"""
        redis = await self._get_redis()
        key = f"leaderboard:{quiz_id}:top10"
        return await redis.set(key, leaderboard_data, settings.cache_leaderboard_ttl)
    
    async def cache_learning_path(self, user_id: str, path_data: Dict) -> bool:
        """Cache AI-generated learning path"""
        redis = await self._get_redis()
        key = f"learning_path:{user_id}"
        return await redis.set(key, path_data, settings.cache_learning_path_ttl)

# Global cache service instance
cache_service = CacheService()
EOF

# Quiz routes with caching
cat > backend/src/api/routes/quiz_routes.py << 'EOF'
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import google.generativeai as genai
from ...services.cache_service import cache_service
from ...config.settings import get_settings

router = APIRouter(prefix="/quiz", tags=["quiz"])
settings = get_settings()

# Configure Gemini AI
genai.configure(api_key=settings.gemini_api_key)
model = genai.GenerativeModel('gemini-pro')

# Mock database functions (replace with real DB in production)
async def fetch_quiz_from_db(quiz_id: str) -> Dict:
    """Simulate database fetch"""
    return {
        "id": quiz_id,
        "title": f"Quiz {quiz_id}",
        "questions": [
            {
                "id": 1,
                "question": "What is caching?",
                "options": ["A", "B", "C", "D"],
                "correct": 0
            }
        ],
        "created_at": "2024-01-01T00:00:00Z"
    }

async def fetch_user_progress_from_db(user_id: str, quiz_id: str) -> Dict:
    """Simulate user progress fetch"""
    return {
        "user_id": user_id,
        "quiz_id": quiz_id,
        "score": 85,
        "completed": True,
        "time_spent": 300
    }

async def fetch_leaderboard_from_db(quiz_id: str) -> List[Dict]:
    """Simulate leaderboard fetch"""
    return [
        {"user_id": "user1", "score": 95, "time": 180},
        {"user_id": "user2", "score": 90, "time": 200},
        {"user_id": "user3", "score": 85, "time": 220}
    ]

@router.get("/{quiz_id}")
async def get_quiz(quiz_id: str):
    """Get quiz with caching"""
    cache_key = f"quiz:{quiz_id}"
    
    quiz_data = await cache_service.get_or_set(
        cache_key,
        fetch_quiz_from_db,
        settings.cache_quiz_ttl,
        quiz_id
    )
    
    if not quiz_data:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    return quiz_data

@router.get("/{quiz_id}/progress/{user_id}")
async def get_user_progress(quiz_id: str, user_id: str):
    """Get user progress with caching"""
    cache_key = f"user_progress:{user_id}:{quiz_id}"
    
    progress_data = await cache_service.get_or_set(
        cache_key,
        fetch_user_progress_from_db,
        settings.cache_user_progress_ttl,
        user_id,
        quiz_id
    )
    
    return progress_data or {"user_id": user_id, "quiz_id": quiz_id, "score": 0, "completed": False}

@router.get("/{quiz_id}/leaderboard")
async def get_leaderboard(quiz_id: str):
    """Get leaderboard with caching"""
    cache_key = f"leaderboard:{quiz_id}:top10"
    
    leaderboard_data = await cache_service.get_or_set(
        cache_key,
        fetch_leaderboard_from_db,
        settings.cache_leaderboard_ttl,
        quiz_id
    )
    
    return {"quiz_id": quiz_id, "leaderboard": leaderboard_data}

@router.get("/{quiz_id}/explanation/{topic}")
async def get_ai_explanation(quiz_id: str, topic: str):
    """Get AI explanation with caching"""
    cache_key = f"ai_explanation:{topic}:{hash(topic) % 10000}"
    
    async def generate_explanation():
        try:
            prompt = f"Explain {topic} in simple terms for quiz students. Keep it under 200 words."
            response = model.generate_content(prompt)
            return {"topic": topic, "explanation": response.text}
        except Exception as e:
            return {"topic": topic, "explanation": f"Explanation for {topic} (cached demo)"}
    
    explanation = await cache_service.get_or_set(
        cache_key,
        generate_explanation,
        21600  # 6 hours for AI explanations
    )
    
    return explanation

@router.post("/{quiz_id}/invalidate")
async def invalidate_quiz_cache(quiz_id: str):
    """Force invalidate quiz cache"""
    deleted_count = await cache_service.invalidate_quiz_cache(quiz_id)
    return {"message": f"Invalidated {deleted_count} cache entries for quiz {quiz_id}"}
EOF

# Cache monitoring routes
cat > backend/src/api/routes/cache_routes.py << 'EOF'
from fastapi import APIRouter, Depends
from ...cache.redis_client import get_redis_client

router = APIRouter(tags=["cache"])

@router.get("/stats")
async def get_cache_stats():
    """Get cache performance statistics"""
    redis_client = await get_redis_client()
    stats = await redis_client.get_stats()
    
    return {
        "cache_performance": stats,
        "recommendations": {
            "hit_rate": "Target: >75%",
            "memory_usage": "Monitor growth trends",
            "connections": "Keep under 20 for this demo"
        }
    }

@router.post("/flush")
async def flush_cache():
    """Flush all cache (use with caution)"""
    redis_client = await get_redis_client()
    if redis_client.redis:
        await redis_client.redis.flushall()
        return {"message": "Cache flushed successfully"}
    return {"error": "Redis not connected"}

@router.get("/keys/{pattern}")
async def list_cache_keys(pattern: str = "*"):
    """List cache keys matching pattern"""
    redis_client = await get_redis_client()
    if redis_client.redis:
        keys = await redis_client.redis.keys(pattern)
        return {"keys": keys[:50], "total": len(keys)}  # Limit to 50 for display
    return {"keys": [], "total": 0}
EOF

# Cache middleware
cat > backend/src/api/middleware/cache_middleware.py << 'EOF'
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import time
import structlog

logger = structlog.get_logger()

class CacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Add cache headers for static content
        response = await call_next(request)
        
        # Add timing header
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        
        # Add cache-related headers
        if request.url.path.startswith("/api/v1/quiz/"):
            response.headers["X-Cache-Strategy"] = "cache-aside"
            response.headers["Cache-Control"] = "public, max-age=300"  # 5 minutes browser cache
        
        return response
EOF

# Create __init__.py files
touch backend/src/__init__.py
touch backend/src/api/__init__.py
touch backend/src/api/routes/__init__.py
touch backend/src/api/middleware/__init__.py
touch backend/src/models/__init__.py
touch backend/src/services/__init__.py
touch backend/src/cache/__init__.py
touch backend/src/config/__init__.py

echo "⚛️ Setting up React frontend..."

# Frontend package.json
cat > frontend/package.json << 'EOF'
{
  "name": "quiz-platform-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "@testing-library/jest-dom": "^6.4.5",
    "@testing-library/react": "^15.0.7",
    "@testing-library/user-event": "^14.5.2",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.23.1",
    "react-scripts": "5.0.1",
    "axios": "^1.7.2",
    "recharts": "^2.12.7",
    "web-vitals": "^4.0.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
EOF

# Frontend Dockerfile
cat > frontend/Dockerfile << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm install

# Copy source code
COPY . .

EXPOSE 3000
CMD ["npm", "start"]
EOF

# Main React App
cat > frontend/src/App.js << 'EOF'
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './components/Dashboard/Dashboard';
import QuizView from './components/Quiz/QuizView';
import CacheMonitor from './components/Dashboard/CacheMonitor';
import './styles/App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <header className="app-header">
          <h1>🚀 Quiz Platform - Day 22: Caching Demo</h1>
          <nav>
            <a href="/">Dashboard</a>
            <a href="/cache">Cache Monitor</a>
          </nav>
        </header>
        
        <main>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/quiz/:quizId" element={<QuizView />} />
            <Route path="/cache" element={<CacheMonitor />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
EOF

# API Service
cat > frontend/src/services/api.js << 'EOF'
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with interceptors for cache headers
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
});

// Add request interceptor to log cache-related headers
api.interceptors.response.use(
  (response) => {
    // Log cache performance data
    const cacheStrategy = response.headers['x-cache-strategy'];
    const processTime = response.headers['x-process-time'];
    
    if (cacheStrategy) {
      console.log(`Cache Strategy: ${cacheStrategy}, Process Time: ${processTime}ms`);
    }
    
    return response;
  },
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const quizAPI = {
  getQuiz: (quizId) => api.get(`/api/v1/quiz/${quizId}`),
  getUserProgress: (quizId, userId) => api.get(`/api/v1/quiz/${quizId}/progress/${userId}`),
  getLeaderboard: (quizId) => api.get(`/api/v1/quiz/${quizId}/leaderboard`),
  getAIExplanation: (quizId, topic) => api.get(`/api/v1/quiz/${quizId}/explanation/${topic}`),
  invalidateQuizCache: (quizId) => api.post(`/api/v1/quiz/${quizId}/invalidate`),
};

export const cacheAPI = {
  getStats: () => api.get('/api/v1/cache/stats'),
  flushCache: () => api.post('/api/v1/cache/flush'),
  getCacheKeys: (pattern = '*') => api.get(`/api/v1/cache/keys/${pattern}`),
};

export default api;
EOF

# Dashboard Component
cat > frontend/src/components/Dashboard/Dashboard.js << 'EOF'
import React, { useState, useEffect } from 'react';
import { quizAPI } from '../../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const [quizData, setQuizData] = useState(null);
  const [progress, setProgress] = useState(null);
  const [leaderboard, setLeaderboard] = useState(null);
  const [loading, setLoading] = useState(false);
  const [requestTimes, setRequestTimes] = useState([]);

  const DEMO_QUIZ_ID = "javascript-basics";
  const DEMO_USER_ID = "demo-user";

  const measureRequestTime = async (requestFunc) => {
    const startTime = performance.now();
    const result = await requestFunc();
    const endTime = performance.now();
    const responseTime = Math.round(endTime - startTime);
    
    setRequestTimes(prev => [...prev.slice(-9), responseTime]); // Keep last 10 times
    return result;
  };

  const loadQuizData = async () => {
    setLoading(true);
    try {
      const [quizResponse, progressResponse, leaderboardResponse] = await Promise.all([
        measureRequestTime(() => quizAPI.getQuiz(DEMO_QUIZ_ID)),
        measureRequestTime(() => quizAPI.getUserProgress(DEMO_QUIZ_ID, DEMO_USER_ID)),
        measureRequestTime(() => quizAPI.getLeaderboard(DEMO_QUIZ_ID))
      ]);

      setQuizData(quizResponse.data);
      setProgress(progressResponse.data);
      setLeaderboard(leaderboardResponse.data);
    } catch (error) {
      console.error('Error loading quiz data:', error);
    } finally {
      setLoading(false);
    }
  };

  const invalidateCache = async () => {
    try {
      await quizAPI.invalidateQuizCache(DEMO_QUIZ_ID);
      alert('Cache invalidated! Try loading data again to see cache miss.');
    } catch (error) {
      console.error('Error invalidating cache:', error);
    }
  };

  const getAIExplanation = async () => {
    try {
      const response = await measureRequestTime(() => 
        quizAPI.getAIExplanation(DEMO_QUIZ_ID, "caching")
      );
      alert(`AI Explanation: ${response.data.explanation}`);
    } catch (error) {
      console.error('Error getting AI explanation:', error);
    }
  };

  useEffect(() => {
    loadQuizData();
  }, []);

  const averageResponseTime = requestTimes.length > 0 
    ? Math.round(requestTimes.reduce((a, b) => a + b, 0) / requestTimes.length)
    : 0;

  return (
    <div className="dashboard">
      <div className="performance-metrics">
        <div className="metric-card">
          <h3>Response Time</h3>
          <div className="metric-value">{averageResponseTime}ms</div>
          <div className="metric-detail">Average of last {requestTimes.length} requests</div>
        </div>
        
        <div className="metric-card">
          <h3>Cache Benefits</h3>
          <div className="metric-value">
            {averageResponseTime < 100 ? '🟢 Fast' : averageResponseTime < 300 ? '🟡 Moderate' : '🔴 Slow'}
          </div>
          <div className="metric-detail">
            {averageResponseTime < 100 ? 'Cache hits working!' : 'Possible cache misses'}
          </div>
        </div>
      </div>

      <div className="action-buttons">
        <button onClick={loadQuizData} disabled={loading}>
          {loading ? 'Loading...' : '🔄 Load Quiz Data'}
        </button>
        <button onClick={invalidateCache} className="danger">
          🗑️ Clear Cache
        </button>
        <button onClick={getAIExplanation}>
          🤖 Get AI Explanation
        </button>
      </div>

      <div className="data-display">
        {quizData && (
          <div className="data-card">
            <h3>📝 Quiz Data</h3>
            <p><strong>Title:</strong> {quizData.title}</p>
            <p><strong>Questions:</strong> {quizData.questions?.length || 0}</p>
            <p><strong>Cached:</strong> Response time indicates cache usage</p>
          </div>
        )}

        {progress && (
          <div className="data-card">
            <h3>📊 User Progress</h3>
            <p><strong>Score:</strong> {progress.score}%</p>
            <p><strong>Completed:</strong> {progress.completed ? 'Yes' : 'No'}</p>
            <p><strong>Time Spent:</strong> {progress.time_spent}s</p>
          </div>
        )}

        {leaderboard && (
          <div className="data-card">
            <h3>🏆 Leaderboard</h3>
            {leaderboard.leaderboard?.map((entry, index) => (
              <div key={index} className="leaderboard-entry">
                {index + 1}. {entry.user_id}: {entry.score}% ({entry.time}s)
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="response-times">
        <h3>📈 Response Time History</h3>
        <div className="time-bars">
          {requestTimes.map((time, index) => (
            <div 
              key={index} 
              className="time-bar" 
              style={{height: `${Math.min(time / 5, 50)}px`}}
              title={`${time}ms`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
EOF

# Cache Monitor Component
cat > frontend/src/components/Dashboard/CacheMonitor.js << 'EOF'
import React, { useState, useEffect } from 'react';
import { cacheAPI } from '../../services/api';
import './CacheMonitor.css';

const CacheMonitor = () => {
  const [stats, setStats] = useState(null);
  const [keys, setKeys] = useState([]);
  const [loading, setLoading] = useState(false);

  const loadCacheStats = async () => {
    setLoading(true);
    try {
      const [statsResponse, keysResponse] = await Promise.all([
        cacheAPI.getStats(),
        cacheAPI.getCacheKeys()
      ]);
      
      setStats(statsResponse.data);
      setKeys(keysResponse.data.keys);
    } catch (error) {
      console.error('Error loading cache stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const flushCache = async () => {
    if (window.confirm('Are you sure you want to flush all cache?')) {
      try {
        await cacheAPI.flushCache();
        await loadCacheStats();
        alert('Cache flushed successfully!');
      } catch (error) {
        console.error('Error flushing cache:', error);
      }
    }
  };

  useEffect(() => {
    loadCacheStats();
    const interval = setInterval(loadCacheStats, 5000); // Auto-refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  if (loading && !stats) {
    return <div className="loading">Loading cache statistics...</div>;
  }

  return (
    <div className="cache-monitor">
      <div className="monitor-header">
        <h2>🔍 Cache Performance Monitor</h2>
        <div className="monitor-actions">
          <button onClick={loadCacheStats}>🔄 Refresh</button>
          <button onClick={flushCache} className="danger">🗑️ Flush Cache</button>
        </div>
      </div>

      {stats && (
        <div className="stats-grid">
          <div className="stat-card hit-rate">
            <h3>Hit Rate</h3>
            <div className="stat-value">{stats.cache_performance.hit_rate}</div>
            <div className="stat-detail">
              Hits: {stats.cache_performance.hit_count} | 
              Misses: {stats.cache_performance.miss_count}
            </div>
          </div>

          <div className="stat-card memory">
            <h3>Memory Usage</h3>
            <div className="stat-value">{stats.cache_performance.used_memory_human}</div>
            <div className="stat-detail">Redis memory consumption</div>
          </div>

          <div className="stat-card connections">
            <h3>Connections</h3>
            <div className="stat-value">{stats.cache_performance.connected_clients}</div>
            <div className="stat-detail">Active Redis connections</div>
          </div>

          <div className="stat-card keyspace">
            <h3>Redis Keyspace</h3>
            <div className="stat-value">
              {stats.cache_performance.keyspace_hits} / {stats.cache_performance.keyspace_misses}
            </div>
            <div className="stat-detail">Hits / Misses (Redis level)</div>
          </div>
        </div>
      )}

      <div className="cache-keys">
        <h3>📋 Cache Keys ({keys.length})</h3>
        <div className="keys-list">
          {keys.slice(0, 20).map((key, index) => (
            <div key={index} className="cache-key">
              <span className="key-name">{key}</span>
              <span className="key-type">
                {key.includes('quiz:') ? '📝' : 
                 key.includes('user_progress:') ? '📊' : 
                 key.includes('leaderboard:') ? '🏆' : 
                 key.includes('ai_explanation:') ? '🤖' : '🔧'}
              </span>
            </div>
          ))}
          {keys.length > 20 && (
            <div className="more-keys">... and {keys.length - 20} more keys</div>
          )}
        </div>
      </div>

      {stats && (
        <div className="recommendations">
          <h3>💡 Performance Recommendations</h3>
          <ul>
            <li>Target hit rate: {stats.recommendations.hit_rate}</li>
            <li>Memory usage: {stats.recommendations.memory_usage}</li>
            <li>Connections: {stats.recommendations.connections}</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default CacheMonitor;
EOF

# CSS Files
cat > frontend/src/styles/App.css << 'EOF'
.App {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 20px;
  border-radius: 10px;
  margin-bottom: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.app-header h1 {
  margin: 0 0 15px 0;
  font-size: 1.8rem;
}

.app-header nav {
  display: flex;
  gap: 20px;
}

.app-header nav a {
  color: white;
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 5px;
  background: rgba(255, 255, 255, 0.2);
  transition: background 0.3s;
}

.app-header nav a:hover {
  background: rgba(255, 255, 255, 0.3);
}

.loading {
  text-align: center;
  padding: 50px;
  font-size: 1.2rem;
  color: #666;
}
EOF

cat > frontend/src/components/Dashboard/Dashboard.css << 'EOF'
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.performance-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.metric-card {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border-left: 4px solid #4CAF50;
}

.metric-card h3 {
  margin: 0 0 10px 0;
  color: #333;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.metric-value {
  font-size: 2rem;
  font-weight: bold;
  color: #2196F3;
  margin-bottom: 5px;
}

.metric-detail {
  font-size: 0.8rem;
  color: #666;
}

.action-buttons {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-bottom: 20px;
}

.action-buttons button {
  padding: 12px 24px;
  border: none;
  border-radius: 8px;
  background: #2196F3;
  color: white;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.3s ease;
}

.action-buttons button:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.action-buttons button:disabled {
  background: #ccc;
  cursor: not-allowed;
  transform: none;
}

.action-buttons button.danger {
  background: #f44336;
}

.data-display {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.data-card {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.data-card h3 {
  margin: 0 0 15px 0;
  color: #333;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
}

.data-card p {
  margin: 8px 0;
  line-height: 1.5;
}

.leaderboard-entry {
  padding: 8px 0;
  border-bottom: 1px solid #eee;
  font-family: monospace;
}

.response-times {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.response-times h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.time-bars {
  display: flex;
  align-items: end;
  gap: 3px;
  height: 60px;
  padding: 10px 0;
}

.time-bar {
  background: linear-gradient(to top, #4CAF50, #81C784);
  width: 20px;
  min-height: 2px;
  border-radius: 2px 2px 0 0;
  cursor: pointer;
  transition: all 0.3s ease;
}

.time-bar:hover {
  opacity: 0.7;
}
EOF

cat > frontend/src/components/Dashboard/CacheMonitor.css << 'EOF'
.cache-monitor {
  padding: 20px 0;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 2px solid #eee;
}

.monitor-header h2 {
  margin: 0;
  color: #333;
}

.monitor-actions {
  display: flex;
  gap: 10px;
}

.monitor-actions button {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  background: #2196F3;
  color: white;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.3s ease;
}

.monitor-actions button:hover {
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.monitor-actions button.danger {
  background: #f44336;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border-top: 4px solid #4CAF50;
}

.stat-card.hit-rate {
  border-top-color: #4CAF50;
}

.stat-card.memory {
  border-top-color: #FF9800;
}

.stat-card.connections {
  border-top-color: #2196F3;
}

.stat-card.keyspace {
  border-top-color: #9C27B0;
}

.stat-card h3 {
  margin: 0 0 10px 0;
  color: #555;
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.stat-value {
  font-size: 2.2rem;
  font-weight: bold;
  color: #333;
  margin-bottom: 8px;
}

.stat-detail {
  font-size: 0.85rem;
  color: #777;
  line-height: 1.4;
}

.cache-keys {
  background: white;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.cache-keys h3 {
  margin: 0 0 15px 0;
  color: #333;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
}

.keys-list {
  max-height: 300px;
  overflow-y: auto;
}

.cache-key {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid #f5f5f5;
  font-family: 'Monaco', 'Courier New', monospace;
  font-size: 0.85rem;
}

.key-name {
  color: #333;
  word-break: break-all;
}

.key-type {
  font-size: 1.2rem;
  margin-left: 10px;
}

.more-keys {
  padding: 10px 0;
  text-align: center;
  color: #666;
  font-style: italic;
}

.recommendations {
  background: #f8f9fa;
  padding: 20px;
  border-radius: 10px;
  border-left: 4px solid #17a2b8;
}

.recommendations h3 {
  margin: 0 0 15px 0;
  color: #333;
}

.recommendations ul {
  margin: 0;
  padding-left: 20px;
}

.recommendations li {
  margin: 8px 0;
  color: #555;
  line-height: 1.5;
}
EOF

# Create remaining frontend files
cat > frontend/src/components/Quiz/QuizView.js << 'EOF'
import React from 'react';
import { useParams } from 'react-router-dom';

const QuizView = () => {
  const { quizId } = useParams();
  
  return (
    <div style={{padding: '20px', textAlign: 'center'}}>
      <h2>Quiz View for {quizId}</h2>
      <p>Individual quiz interface would be implemented here.</p>
      <p>This demo focuses on the caching infrastructure.</p>
    </div>
  );
};

export default QuizView;
EOF

cat > frontend/src/index.js << 'EOF'
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

cat > frontend/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Quiz Platform with Caching - Day 22" />
    <title>Quiz Platform - Caching Demo</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOF

echo "🧪 Creating test files..."

# Backend tests
cat > backend/src/tests/test_cache_service.py << 'EOF'
import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from src.services.cache_service import CacheService

@pytest.fixture
def cache_service():
    return CacheService()

@pytest.fixture
def mock_redis_client():
    mock_client = AsyncMock()
    mock_client.get.return_value = None
    mock_client.set.return_value = True
    mock_client.invalidate_pattern.return_value = 5
    return mock_client

@pytest.mark.asyncio
async def test_cache_aside_pattern(cache_service, mock_redis_client):
    """Test cache-aside pattern with cache miss and set"""
    
    # Mock the fetch function
    async def mock_fetch_func(quiz_id):
        return {"id": quiz_id, "title": "Test Quiz"}
    
    with patch.object(cache_service, '_get_redis', return_value=mock_redis_client):
        # First call should be cache miss
        result = await cache_service.get_or_set(
            "test_key", 
            mock_fetch_func, 
            3600, 
            "quiz123"
        )
        
        # Verify cache get was called
        mock_redis_client.get.assert_called_once_with("test_key")
        
        # Verify cache set was called with fetched data
        mock_redis_client.set.assert_called_once_with(
            "test_key", 
            {"id": "quiz123", "title": "Test Quiz"}, 
            3600
        )
        
        assert result == {"id": "quiz123", "title": "Test Quiz"}

@pytest.mark.asyncio
async def test_cache_hit(cache_service, mock_redis_client):
    """Test cache hit scenario"""
    
    # Configure mock to return cached data
    cached_data = {"id": "quiz123", "title": "Cached Quiz"}
    mock_redis_client.get.return_value = cached_data
    
    async def mock_fetch_func(quiz_id):
        # This should not be called on cache hit
        pytest.fail("Fetch function should not be called on cache hit")
    
    with patch.object(cache_service, '_get_redis', return_value=mock_redis_client):
        result = await cache_service.get_or_set(
            "test_key", 
            mock_fetch_func, 
            3600, 
            "quiz123"
        )
        
        # Verify only get was called, not set
        mock_redis_client.get.assert_called_once_with("test_key")
        mock_redis_client.set.assert_not_called()
        
        assert result == cached_data

@pytest.mark.asyncio
async def test_quiz_cache_invalidation(cache_service, mock_redis_client):
    """Test quiz cache invalidation"""
    
    with patch.object(cache_service, '_get_redis', return_value=mock_redis_client):
        deleted_count = await cache_service.invalidate_quiz_cache("quiz123")
        
        # Should call invalidate_pattern for each pattern
        assert mock_redis_client.invalidate_pattern.call_count == 4
        assert deleted_count == 20  # 4 patterns * 5 keys each
EOF

cat > backend/src/tests/test_quiz_routes.py << 'EOF'
import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from unittest.mock import patch, AsyncMock

from src.main import app

@pytest.mark.asyncio
async def test_get_quiz_endpoint():
    """Test quiz endpoint returns data"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/quiz/test-quiz")
        
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-quiz"
    assert "title" in data
    assert "questions" in data

@pytest.mark.asyncio
async def test_cache_headers():
    """Test that cache headers are properly set"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/quiz/test-quiz")
        
    assert response.status_code == 200
    assert "X-Cache-Strategy" in response.headers
    assert response.headers["X-Cache-Strategy"] == "cache-aside"
    assert "X-Process-Time" in response.headers

@pytest.mark.asyncio
async def test_cache_invalidation_endpoint():
    """Test cache invalidation endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/quiz/test-quiz/invalidate")
        
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test-quiz" in data["message"]
EOF

# Frontend tests
cat > frontend/src/components/Dashboard/Dashboard.test.js << 'EOF'
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from './Dashboard';

// Mock the API module
jest.mock('../../services/api', () => ({
  quizAPI: {
    getQuiz: jest.fn(),
    getUserProgress: jest.fn(),
    getLeaderboard: jest.fn(),
    invalidateQuizCache: jest.fn(),
  }
}));

const MockedDashboard = () => (
  <BrowserRouter>
    <Dashboard />
  </BrowserRouter>
);

test('renders dashboard components', async () => {
  const { quizAPI } = require('../../services/api');
  
  // Mock API responses
  quizAPI.getQuiz.mockResolvedValue({
    data: { id: 'test', title: 'Test Quiz', questions: [] }
  });
  quizAPI.getUserProgress.mockResolvedValue({
    data: { score: 85, completed: true, time_spent: 300 }
  });
  quizAPI.getLeaderboard.mockResolvedValue({
    data: { leaderboard: [] }
  });

  render(<MockedDashboard />);
  
  // Check for key elements
  expect(screen.getByText('Response Time')).toBeInTheDocument();
  expect(screen.getByText('Cache Benefits')).toBeInTheDocument();
  
  // Wait for data loading
  await waitFor(() => {
    expect(screen.getByText('Load Quiz Data')).toBeInTheDocument();
  });
});

test('displays performance metrics', () => {
  render(<MockedDashboard />);
  
  expect(screen.getByText('Response Time')).toBeInTheDocument();
  expect(screen.getByText('Cache Benefits')).toBeInTheDocument();
  expect(screen.getByText('Average of last 0 requests')).toBeInTheDocument();
});
EOF

echo "🚀 Creating startup scripts..."

# Environment file
cat > .env << 'EOF'
GEMINI_API_KEY=your-gemini-api-key-here
REDIS_URL=redis://localhost:6379
ENVIRONMENT=development
EOF

# Start script
cat > start.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting Day 22: Caching Implementation Demo"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create Python virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# Install Node.js dependencies
echo "⚛️ Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Start services with Docker Compose
echo "🐳 Starting services with Docker Compose..."
docker-compose up -d redis

# Wait for Redis to be ready
echo "⏳ Waiting for Redis to be ready..."
sleep 5

# Start backend
echo "🖥️ Starting backend server..."
cd backend
source ../venv/bin/activate
python -m pytest src/tests/ -v
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "🌐 Starting frontend..."
cd frontend
npm test -- --watchAll=false
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ All services started successfully!"
echo ""
echo "🌐 Access the application:"
echo "   Frontend Dashboard: http://localhost:3000"
echo "   Backend API Docs:   http://localhost:8000/docs"
echo "   Cache Statistics:   http://localhost:8000/api/v1/cache/stats"
echo "   Health Check:       http://localhost:8000/health"
echo ""
echo "🧪 Demo Instructions:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Click 'Load Quiz Data' multiple times to see caching in action"
echo "3. Monitor response times - first request may be slower (cache miss)"
echo "4. Subsequent requests should be faster (cache hits)"
echo "5. Click 'Clear Cache' and try loading again to see cache miss"
echo "6. Visit Cache Monitor tab to see detailed statistics"
echo ""
echo "📊 Watch for:"
echo "   - Response times under 100ms (cache hits)"
echo "   - Cache hit rates above 75%"
echo "   - Memory usage in Redis"
echo ""
echo "💡 To stop all services, run: ./stop.sh"

# Store PIDs for cleanup
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

# Keep script running
wait
EOF

# Stop script
cat > stop.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping Day 22: Caching Implementation Demo"

# Kill background processes
if [ -f backend.pid ]; then
    echo "Stopping backend..."
    kill $(cat backend.pid) 2>/dev/null || true
    rm backend.pid
fi

if [ -f frontend.pid ]; then
    echo "Stopping frontend..."
    kill $(cat frontend.pid) 2>/dev/null || true
    rm frontend.pid
fi

# Stop Docker services
echo "Stopping Docker services..."
docker-compose down

# Deactivate virtual environment
deactivate 2>/dev/null || true

echo "✅ All services stopped successfully!"
EOF

# Make scripts executable
chmod +x start.sh stop.sh

echo "✅ Project setup complete!"
echo ""
echo "📁 Project structure created:"
echo "   ├── backend/          (Python FastAPI with Redis caching)"
echo "   ├── frontend/         (React dashboard)"
echo "   ├── docker-compose.yml (Redis container)"
echo "   ├── start.sh          (Launch everything)"
echo "   └── stop.sh           (Stop everything)"
echo ""
echo "🚀 To start the demo:"
echo "   ./start.sh"
echo ""
echo "📚 What was implemented:"
echo "   ✅ Redis caching layer with connection pooling"
echo "   ✅ Cache-aside pattern for quiz data"
echo "   ✅ Smart TTL strategies by data type"
echo "   ✅ Cache invalidation on content updates"
echo "   ✅ Performance monitoring dashboard"
echo "   ✅ Comprehensive test suite"
echo "   ✅ Real-time cache statistics"
echo ""
echo "🎯 Success metrics to observe:"
echo "   • Response times < 100ms for cached requests"
echo "   • Cache hit rates > 75%"
echo "   • Database query reduction by 60-80%"
echo "   • System handles 10x more concurrent requests"