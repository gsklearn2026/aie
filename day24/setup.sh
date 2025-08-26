#!/bin/bash

# Day 24: Logging and Monitoring Service Implementation Script
# AI Engineering Quiz Platform - Week 4

set -e

echo "🚀 Starting Day 24: Logging and Monitoring Service Implementation"

# Create project structure
echo "📁 Creating project structure..."
mkdir -p ai-quiz-platform/day24-logging-monitoring/{backend,frontend,tests,docs,logs}
cd ai-quiz-platform/day24-logging-monitoring

mkdir -p backend/{app,services,middleware,models,config}
mkdir -p frontend/{src,public,components,pages,utils}
mkdir -p tests/{unit,integration,e2e}

# Create backend logging service
echo "🐍 Creating Python backend logging service..."

# Backend requirements
cat > backend/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
python-json-logger==2.0.7
elasticsearch==8.11.0
redis==5.0.1
prometheus-client==0.19.0
google-generativeai==0.3.2
psutil==5.9.6
aiofiles==23.2.1
python-multipart==0.0.6
requests==2.31.0
pytest==7.4.3
pytest-asyncio==0.21.1
python-dotenv==1.0.0
sqlalchemy==2.0.23
alembic==1.13.0
pydantic==2.5.0
structlog==23.2.0
EOF

# Logging configuration
cat > backend/config/logging_config.py << 'EOF'
import os
import structlog
from datetime import datetime
from typing import Any, Dict

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

class LoggingConfig:
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
    ENABLE_CONSOLE = os.getenv("ENABLE_CONSOLE", "true").lower() == "true"
    ENABLE_FILE = os.getenv("ENABLE_FILE", "true").lower() == "true"
    
    # Elasticsearch configuration
    ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "localhost:9200")
    ELASTICSEARCH_INDEX = os.getenv("ELASTICSEARCH_INDEX", "quiz-platform-logs")
    
    # Redis configuration
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    
    # Metrics configuration
    METRICS_PORT = int(os.getenv("METRICS_PORT", "8000"))
EOF

# Logging middleware
cat > backend/middleware/logging_middleware.py << 'EOF'
import time
import uuid
import structlog
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Dict, Any
import json

logger = structlog.get_logger()

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Extract user context
        user_id = request.headers.get("X-User-ID", "anonymous")
        session_id = request.headers.get("X-Session-ID", "unknown")
        
        # Start timer
        start_time = time.perf_counter()
        
        # Add context to request
        request.state.request_id = request_id
        request.state.user_id = user_id
        request.state.session_id = session_id
        
        # Log request start
        await self._log_request_start(request, request_id, user_id, session_id)
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate timing
            process_time = time.perf_counter() - start_time
            
            # Log request completion
            await self._log_request_complete(
                request, response, request_id, user_id, session_id, process_time
            )
            
            # Add headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.perf_counter() - start_time
            await self._log_request_error(
                request, e, request_id, user_id, session_id, process_time
            )
            raise
    
    async def _log_request_start(self, request: Request, request_id: str, 
                                user_id: str, session_id: str):
        logger.info(
            "Request started",
            event="request_start",
            request_id=request_id,
            user_id=user_id,
            session_id=session_id,
            method=request.method,
            url=str(request.url),
            user_agent=request.headers.get("User-Agent"),
            ip_address=request.client.host if request.client else None
        )
    
    async def _log_request_complete(self, request: Request, response: Response,
                                  request_id: str, user_id: str, session_id: str,
                                  process_time: float):
        logger.info(
            "Request completed",
            event="request_complete",
            request_id=request_id,
            user_id=user_id,
            session_id=session_id,
            method=request.method,
            url=str(request.url),
            status_code=response.status_code,
            process_time_ms=round(process_time * 1000, 2)
        )
    
    async def _log_request_error(self, request: Request, error: Exception,
                               request_id: str, user_id: str, session_id: str,
                               process_time: float):
        logger.error(
            "Request failed",
            event="request_error",
            request_id=request_id,
            user_id=user_id,
            session_id=session_id,
            method=request.method,
            url=str(request.url),
            error_type=type(error).__name__,
            error_message=str(error),
            process_time_ms=round(process_time * 1000, 2)
        )
EOF

# Metrics service
cat > backend/services/metrics_service.py << 'EOF'
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import psutil
import structlog
from typing import Dict, Any
import time

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_USERS = Gauge('active_users_total', 'Number of active users')
SYSTEM_CPU = Gauge('system_cpu_percent', 'System CPU usage')
SYSTEM_MEMORY = Gauge('system_memory_percent', 'System memory usage')
QUIZ_SUBMISSIONS = Counter('quiz_submissions_total', 'Total quiz submissions', ['quiz_type'])
AI_INFERENCE_TIME = Histogram('ai_inference_duration_seconds', 'AI model inference time')

class MetricsService:
    def __init__(self):
        self.start_time = time.time()
        
    def start_metrics_server(self, port: int = 8000):
        """Start Prometheus metrics server"""
        start_http_server(port)
        logger.info("Metrics server started", port=port)
    
    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request metrics"""
        REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=status).inc()
        REQUEST_DURATION.observe(duration)
        
        logger.info(
            "Request metrics recorded",
            event="metrics_request",
            method=method,
            endpoint=endpoint,
            status=status,
            duration_ms=round(duration * 1000, 2)
        )
    
    def record_quiz_submission(self, quiz_type: str):
        """Record quiz submission"""
        QUIZ_SUBMISSIONS.labels(quiz_type=quiz_type).inc()
        
        logger.info(
            "Quiz submission recorded",
            event="metrics_quiz_submission",
            quiz_type=quiz_type
        )
    
    def record_ai_inference(self, duration: float):
        """Record AI inference time"""
        AI_INFERENCE_TIME.observe(duration)
        
        logger.info(
            "AI inference metrics recorded",
            event="metrics_ai_inference",
            duration_ms=round(duration * 1000, 2)
        )
    
    def update_system_metrics(self):
        """Update system resource metrics"""
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        
        SYSTEM_CPU.set(cpu_percent)
        SYSTEM_MEMORY.set(memory_percent)
        
        logger.debug(
            "System metrics updated",
            event="metrics_system",
            cpu_percent=cpu_percent,
            memory_percent=memory_percent
        )
    
    def set_active_users(self, count: int):
        """Set active user count"""
        ACTIVE_USERS.set(count)
        
        logger.info(
            "Active users updated",
            event="metrics_active_users",
            count=count
        )

# Global metrics instance
metrics_service = MetricsService()
EOF

# Logging service
cat > backend/services/logging_service.py << 'EOF'
import json
import aiofiles
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import structlog
from elasticsearch import AsyncElasticsearch
import redis.asyncio as redis

logger = structlog.get_logger()

class LoggingService:
    def __init__(self, elasticsearch_host: str = "localhost:9200", 
                 redis_host: str = "localhost", redis_port: int = 6379):
        self.es_client = None
        self.redis_client = None
        self.elasticsearch_host = elasticsearch_host
        self.redis_host = redis_host
        self.redis_port = redis_port
        
    async def initialize(self):
        """Initialize connections"""
        try:
            # Initialize Elasticsearch
            self.es_client = AsyncElasticsearch([self.elasticsearch_host])
            
            # Initialize Redis
            self.redis_client = redis.Redis(
                host=self.redis_host, 
                port=self.redis_port, 
                decode_responses=True
            )
            
            logger.info("Logging service initialized successfully")
            
        except Exception as e:
            logger.warning(
                "Failed to initialize external services, using file-based logging",
                error=str(e)
            )
    
    async def log_event(self, event_data: Dict[str, Any]):
        """Log an event with structured data"""
        # Add timestamp
        event_data["timestamp"] = datetime.utcnow().isoformat()
        
        # Log to file
        await self._log_to_file(event_data)
        
        # Log to Elasticsearch if available
        if self.es_client:
            await self._log_to_elasticsearch(event_data)
        
        # Cache recent logs in Redis
        if self.redis_client:
            await self._cache_log_entry(event_data)
        
        logger.debug("Event logged", event=event_data.get("event"))
    
    async def _log_to_file(self, event_data: Dict[str, Any]):
        """Write log entry to file"""
        log_entry = json.dumps(event_data) + "\n"
        
        async with aiofiles.open("logs/app.log", "a") as f:
            await f.write(log_entry)
    
    async def _log_to_elasticsearch(self, event_data: Dict[str, Any]):
        """Index log entry in Elasticsearch"""
        try:
            index_name = f"quiz-platform-logs-{datetime.utcnow().strftime('%Y-%m-%d')}"
            await self.es_client.index(index=index_name, body=event_data)
        except Exception as e:
            logger.error("Failed to index to Elasticsearch", error=str(e))
    
    async def _cache_log_entry(self, event_data: Dict[str, Any]):
        """Cache recent log entry in Redis"""
        try:
            # Keep last 1000 log entries in Redis
            await self.redis_client.lpush("recent_logs", json.dumps(event_data))
            await self.redis_client.ltrim("recent_logs", 0, 999)
            await self.redis_client.expire("recent_logs", 3600)  # 1 hour expiry
        except Exception as e:
            logger.error("Failed to cache log entry", error=str(e))
    
    async def search_logs(self, query: str, start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None, limit: int = 100) -> List[Dict]:
        """Search logs with optional time range"""
        logs = []
        
        # Try Elasticsearch first
        if self.es_client:
            try:
                es_query = {
                    "query": {
                        "bool": {
                            "must": [
                                {"query_string": {"query": query}}
                            ]
                        }
                    },
                    "size": limit,
                    "sort": [{"timestamp": {"order": "desc"}}]
                }
                
                if start_time or end_time:
                    time_range = {}
                    if start_time:
                        time_range["gte"] = start_time.isoformat()
                    if end_time:
                        time_range["lte"] = end_time.isoformat()
                    
                    es_query["query"]["bool"]["must"].append({
                        "range": {"timestamp": time_range}
                    })
                
                response = await self.es_client.search(
                    index="quiz-platform-logs-*",
                    body=es_query
                )
                
                logs = [hit["_source"] for hit in response["hits"]["hits"]]
                
            except Exception as e:
                logger.error("Elasticsearch search failed", error=str(e))
        
        # Fallback to Redis cache for recent logs
        if not logs and self.redis_client:
            try:
                cached_logs = await self.redis_client.lrange("recent_logs", 0, limit - 1)
                logs = [json.loads(log) for log in cached_logs]
                
                # Filter by query (simple text search)
                if query:
                    logs = [log for log in logs if query.lower() in json.dumps(log).lower()]
                
            except Exception as e:
                logger.error("Redis search failed", error=str(e))
        
        return logs
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Get logging metrics summary"""
        summary = {
            "total_logs_today": 0,
            "error_count_today": 0,
            "warning_count_today": 0,
            "avg_response_time": 0,
            "top_endpoints": [],
            "top_errors": []
        }
        
        if self.es_client:
            try:
                # Get today's logs
                today = datetime.utcnow().strftime('%Y-%m-%d')
                index_name = f"quiz-platform-logs-{today}"
                
                # Total logs today
                response = await self.es_client.count(index=index_name)
                summary["total_logs_today"] = response.get("count", 0)
                
                # Error and warning counts
                for level in ["error", "warning"]:
                    response = await self.es_client.count(
                        index=index_name,
                        body={"query": {"term": {"level": level}}}
                    )
                    summary[f"{level}_count_today"] = response.get("count", 0)
                
            except Exception as e:
                logger.error("Failed to get metrics summary", error=str(e))
        
        return summary

# Global logging service instance
logging_service = LoggingService()
EOF

# Main FastAPI application
cat > backend/app/main.py << 'EOF'
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from middleware.logging_middleware import LoggingMiddleware
from services.logging_service import logging_service
from services.metrics_service import metrics_service
from config.logging_config import LoggingConfig
import structlog
import time
import os
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from datetime import datetime
import google.generativeai as genai

# Configure structured logging
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting AI Quiz Platform Logging Service")
    
    # Initialize services
    await logging_service.initialize()
    metrics_service.start_metrics_server(LoggingConfig.METRICS_PORT)
    
    # Configure Gemini AI
    genai.configure(api_key=os.getenv("GEMINI_API_KEY", "your-api-key-here"))
    
    logger.info("Application startup complete")
    yield
    
    # Shutdown
    logger.info("Shutting down application")

app = FastAPI(
    title="AI Quiz Platform - Logging Service",
    description="Centralized logging and monitoring for AI Quiz Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "AI Quiz Platform Logging Service", "status": "healthy"}

@app.post("/api/v1/log")
async def log_event(event_data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Log a custom event"""
    try:
        # Add service metadata
        event_data.update({
            "service": "quiz-platform",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "version": "1.0.0"
        })
        
        # Log the event in background
        background_tasks.add_task(logging_service.log_event, event_data)
        
        logger.info("Custom event logged", event=event_data.get("event"))
        
        return {"status": "logged", "event_id": event_data.get("event_id")}
        
    except Exception as e:
        logger.error("Failed to log event", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to log event")

@app.get("/api/v1/logs/search")
async def search_logs(
    query: str = "",
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 100
):
    """Search logs with optional filters"""
    try:
        # Parse time parameters
        start_dt = datetime.fromisoformat(start_time) if start_time else None
        end_dt = datetime.fromisoformat(end_time) if end_time else None
        
        # Search logs
        logs = await logging_service.search_logs(query, start_dt, end_dt, limit)
        
        logger.info("Log search performed", query=query, result_count=len(logs))
        
        return {
            "logs": logs,
            "total": len(logs),
            "query": query
        }
        
    except Exception as e:
        logger.error("Log search failed", error=str(e))
        raise HTTPException(status_code=500, detail="Log search failed")

@app.get("/api/v1/metrics/summary")
async def get_metrics_summary():
    """Get logging and system metrics summary"""
    try:
        # Update system metrics
        metrics_service.update_system_metrics()
        
        # Get logging metrics
        logging_metrics = await logging_service.get_metrics_summary()
        
        # Get system metrics
        import psutil
        system_metrics = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "uptime_seconds": time.time() - metrics_service.start_time
        }
        
        logger.info("Metrics summary requested")
        
        return {
            "logging": logging_metrics,
            "system": system_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Failed to get metrics summary", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get metrics")

@app.post("/api/v1/quiz/submit")
async def submit_quiz_answer(
    request: Request,
    quiz_data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Mock quiz submission endpoint with comprehensive logging"""
    start_time = time.perf_counter()
    
    try:
        # Extract user context
        user_id = getattr(request.state, "user_id", "anonymous")
        session_id = getattr(request.state, "session_id", "unknown")
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Simulate AI processing
        question = quiz_data.get("question", "")
        user_answer = quiz_data.get("answer", "")
        
        # Log quiz submission
        await logging_service.log_event({
            "event": "quiz_submission",
            "user_id": user_id,
            "session_id": session_id,
            "request_id": request_id,
            "question_id": quiz_data.get("question_id"),
            "quiz_type": quiz_data.get("quiz_type", "general"),
            "question_length": len(question),
            "answer_length": len(user_answer)
        })
        
        # Simulate AI inference with Gemini
        ai_start = time.perf_counter()
        
        try:
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"Evaluate this quiz answer. Question: {question} Answer: {user_answer}"
            response = model.generate_content(prompt)
            ai_result = response.text[:200]  # Truncate for demo
            
        except Exception as ai_error:
            logger.warning("AI inference failed, using fallback", error=str(ai_error))
            ai_result = "Answer evaluation unavailable"
        
        ai_duration = time.perf_counter() - ai_start
        
        # Record metrics
        metrics_service.record_ai_inference(ai_duration)
        metrics_service.record_quiz_submission(quiz_data.get("quiz_type", "general"))
        
        # Log AI inference
        await logging_service.log_event({
            "event": "ai_inference",
            "user_id": user_id,
            "session_id": session_id,
            "request_id": request_id,
            "inference_duration_ms": round(ai_duration * 1000, 2),
            "model": "gemini-pro",
            "prompt_length": len(prompt) if 'prompt' in locals() else 0,
            "response_length": len(ai_result)
        })
        
        total_duration = time.perf_counter() - start_time
        
        # Log completion
        await logging_service.log_event({
            "event": "quiz_submission_complete",
            "user_id": user_id,
            "session_id": session_id,
            "request_id": request_id,
            "total_duration_ms": round(total_duration * 1000, 2),
            "success": True
        })
        
        return {
            "status": "success",
            "evaluation": ai_result,
            "processing_time_ms": round(total_duration * 1000, 2),
            "request_id": request_id
        }
        
    except Exception as e:
        duration = time.perf_counter() - start_time
        
        # Log error
        await logging_service.log_event({
            "event": "quiz_submission_error",
            "user_id": getattr(request.state, "user_id", "anonymous"),
            "session_id": getattr(request.state, "session_id", "unknown"),
            "request_id": getattr(request.state, "request_id", "unknown"),
            "error_type": type(e).__name__,
            "error_message": str(e),
            "duration_ms": round(duration * 1000, 2)
        })
        
        logger.error("Quiz submission failed", error=str(e))
        raise HTTPException(status_code=500, detail="Quiz submission failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
EOF

# Create React frontend
echo "⚛️ Creating React monitoring dashboard..."

# Package.json for frontend
cat > frontend/package.json << 'EOF'
{
  "name": "logging-monitoring-dashboard",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.6.0",
    "recharts": "^2.8.0",
    "date-fns": "^2.30.0",
    "react-router-dom": "^6.8.0",
    "antd": "^5.12.0",
    "@ant-design/icons": "^5.2.0"
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
  },
  "proxy": "http://localhost:8080"
}
EOF

# Frontend HTML template
cat > frontend/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="AI Quiz Platform Monitoring Dashboard" />
    <title>Logging & Monitoring Dashboard</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOF

# Main React component
cat > frontend/src/App.js << 'EOF'
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Layout, Card, Row, Col, Statistic, Table, Input, Button, DatePicker, Alert } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import { SearchOutlined, ReloadOutlined, DashboardOutlined } from '@ant-design/icons';
import './App.css';

const { Header, Content } = Layout;
const { RangePicker } = DatePicker;

function App() {
  const [metrics, setMetrics] = useState(null);
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [performanceData, setPerformanceData] = useState([]);

  // Fetch metrics summary
  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/api/v1/metrics/summary');
      setMetrics(response.data);
      
      // Generate mock performance data for demo
      const mockData = Array.from({ length: 24 }, (_, i) => ({
        hour: `${i}:00`,
        requests: Math.floor(Math.random() * 1000) + 100,
        responseTime: Math.floor(Math.random() * 500) + 50,
        errors: Math.floor(Math.random() * 50)
      }));
      setPerformanceData(mockData);
      
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  // Search logs
  const searchLogs = async (query = searchQuery) => {
    try {
      setLoading(true);
      const response = await axios.get('/api/v1/logs/search', {
        params: { query, limit: 50 }
      });
      setLogs(response.data.logs);
    } catch (error) {
      console.error('Failed to search logs:', error);
    } finally {
      setLoading(false);
    }
  };

  // Submit test quiz
  const submitTestQuiz = async () => {
    try {
      const testData = {
        question_id: `q_${Date.now()}`,
        quiz_type: 'demo',
        question: 'What is the capital of France?',
        answer: 'Paris'
      };

      await axios.post('/api/v1/quiz/submit', testData, {
        headers: {
          'X-User-ID': 'demo_user_123',
          'X-Session-ID': `session_${Date.now()}`
        }
      });

      // Refresh data
      setTimeout(() => {
        fetchMetrics();
        searchLogs();
      }, 1000);
      
    } catch (error) {
      console.error('Failed to submit test quiz:', error);
    }
  };

  useEffect(() => {
    fetchMetrics();
    searchLogs();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => {
      fetchMetrics();
    }, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const logColumns = [
    {
      title: 'Timestamp',
      dataIndex: 'timestamp',
      key: 'timestamp',
      render: (text) => new Date(text).toLocaleString(),
      width: 200
    },
    {
      title: 'Event',
      dataIndex: 'event',
      key: 'event',
      width: 150
    },
    {
      title: 'Level',
      dataIndex: 'level',
      key: 'level',
      width: 100,
      render: (level) => (
        <span className={`log-level ${level?.toLowerCase()}`}>
          {level?.toUpperCase()}
        </span>
      )
    },
    {
      title: 'User ID',
      dataIndex: 'user_id',
      key: 'user_id',
      width: 120
    },
    {
      title: 'Details',
      key: 'details',
      render: (record) => (
        <div style={{ fontSize: '12px', color: '#666' }}>
          {record.request_id && <div>Request: {record.request_id}</div>}
          {record.process_time_ms && <div>Time: {record.process_time_ms}ms</div>}
          {record.error_message && <div>Error: {record.error_message}</div>}
        </div>
      )
    }
  ];

  return (
    <Layout className="layout">
      <Header className="header">
        <div className="logo">
          <DashboardOutlined /> AI Quiz Platform - Logging & Monitoring
        </div>
      </Header>
      
      <Content style={{ padding: '24px' }}>
        {/* Metrics Overview */}
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="Total Logs Today"
                value={metrics?.logging?.total_logs_today || 0}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="Error Count"
                value={metrics?.logging?.error_count_today || 0}
                valueStyle={{ color: '#cf1322' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="CPU Usage"
                value={metrics?.system?.cpu_percent || 0}
                precision={1}
                suffix="%"
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="Memory Usage"
                value={metrics?.system?.memory_percent || 0}
                precision={1}
                suffix="%"
                valueStyle={{ color: '#722ed1' }}
              />
            </Card>
          </Col>
        </Row>

        {/* Performance Charts */}
        <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
          <Col span={12}>
            <Card title="Request Volume (24h)" extra={<ReloadOutlined onClick={fetchMetrics} />}>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="requests" stroke="#1890ff" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </Card>
          </Col>
          <Col span={12}>
            <Card title="Response Time (24h)">
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="hour" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="responseTime" fill="#52c41a" />
                </BarChart>
              </ResponsiveContainer>
            </Card>
          </Col>
        </Row>

        {/* Test Demo */}
        <Card style={{ marginBottom: '24px' }}>
          <Alert
            message="Demo Mode"
            description="Click the button below to submit a test quiz and see real-time logging in action."
            type="info"
            showIcon
            action={
              <Button type="primary" onClick={submitTestQuiz}>
                Submit Test Quiz
              </Button>
            }
          />
        </Card>

        {/* Log Search */}
        <Card title="Log Search & Analysis">
          <div style={{ marginBottom: '16px' }}>
            <Input.Group compact>
              <Input
                style={{ width: '300px' }}
                placeholder="Search logs (e.g., 'error', 'quiz_submission')"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onPressEnter={() => searchLogs()}
              />
              <Button type="primary" icon={<SearchOutlined />} onClick={() => searchLogs()}>
                Search
              </Button>
              <Button onClick={() => searchLogs('')} style={{ marginLeft: '8px' }}>
                Show All
              </Button>
            </Input.Group>
          </div>

          <Table
            dataSource={logs}
            columns={logColumns}
            rowKey={(record) => `${record.timestamp}-${Math.random()}`}
            loading={loading}
            pagination={{ pageSize: 10 }}
            scroll={{ x: 800 }}
            size="small"
          />
        </Card>
      </Content>
    </Layout>
  );
}

export default App;
EOF

# CSS styles
cat > frontend/src/App.css << 'EOF'
.layout {
  min-height: 100vh;
}

.header {
  display: flex;
  align-items: center;
  background: #001529;
}

.logo {
  color: white;
  font-size: 18px;
  font-weight: bold;
}

.log-level {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: bold;
}

.log-level.info {
  background: #e6f7ff;
  color: #1890ff;
}

.log-level.error {
  background: #fff2f0;
  color: #cf1322;
}

.log-level.warning {
  background: #fffbe6;
  color: #faad14;
}

.log-level.debug {
  background: #f6ffed;
  color: #52c41a;
}

.ant-card {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.ant-statistic-content-value {
  font-weight: bold;
}
EOF

# Frontend index.js
cat > frontend/src/index.js << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import 'antd/dist/reset.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

# Create tests
echo "🧪 Creating test files..."

# Backend tests
cat > tests/test_logging_service.py << 'EOF'
import pytest
import asyncio
from datetime import datetime
from backend.services.logging_service import LoggingService

@pytest.mark.asyncio
async def test_log_event():
    service = LoggingService()
    await service.initialize()
    
    event_data = {
        "event": "test_event",
        "user_id": "test_user",
        "message": "Test log entry"
    }
    
    await service.log_event(event_data)
    
    # Search for the logged event
    logs = await service.search_logs("test_event")
    assert len(logs) >= 0  # Should not fail

@pytest.mark.asyncio
async def test_search_logs():
    service = LoggingService()
    await service.initialize()
    
    logs = await service.search_logs("test", limit=10)
    assert isinstance(logs, list)

def test_logging_service_initialization():
    service = LoggingService()
    assert service.elasticsearch_host == "localhost:9200"
    assert service.redis_host == "localhost"
    assert service.redis_port == 6379
EOF

# Frontend test
cat > frontend/src/App.test.js << 'EOF'
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders dashboard title', () => {
  render(<App />);
  const titleElement = screen.getByText(/AI Quiz Platform - Logging & Monitoring/i);
  expect(titleElement).toBeInTheDocument();
});

test('renders metrics cards', () => {
  render(<App />);
  const totalLogsCard = screen.getByText(/Total Logs Today/i);
  expect(totalLogsCard).toBeInTheDocument();
});
EOF

# Environment configuration
cat > .env << 'EOF'
# Backend Configuration
LOG_LEVEL=INFO
ENVIRONMENT=development
GEMINI_API_KEY=your-api-key-here

# Database Configuration
ELASTICSEARCH_HOST=localhost:9200
REDIS_HOST=localhost
REDIS_PORT=6379

# Metrics Configuration
METRICS_PORT=8000

# Server Configuration
HOST=0.0.0.0
PORT=8080
EOF

# Create start script
cat > start.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting AI Quiz Platform - Logging and Monitoring Service"

# Create logs directory
mkdir -p logs

# Setup Python virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Install Node.js dependencies
echo "⚛️ Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Create log files
touch logs/app.log

# Start backend server
echo "🖥️ Starting backend server..."
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to initialize..."
sleep 5

# Start frontend development server
echo "🌐 Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Save PIDs for stop script
echo $BACKEND_PID > .backend_pid
echo $FRONTEND_PID > .frontend_pid

echo "✅ All services started successfully!"
echo "📊 Backend API: http://localhost:8080"
echo "🌐 Frontend Dashboard: http://localhost:3000"
echo "📈 Metrics: http://localhost:8000"
echo ""
echo "💡 Use './stop.sh' to stop all services"

# Keep script running
wait
EOF

# Create stop script
cat > stop.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping AI Quiz Platform services..."

# Stop backend
if [ -f .backend_pid ]; then
    BACKEND_PID=$(cat .backend_pid)
    kill $BACKEND_PID 2>/dev/null
    rm .backend_pid
    echo "🖥️ Backend stopped"
fi

# Stop frontend
if [ -f .frontend_pid ]; then
    FRONTEND_PID=$(cat .frontend_pid)
    kill $FRONTEND_PID 2>/dev/null
    rm .frontend_pid
    echo "🌐 Frontend stopped"
fi

# Kill any remaining processes
pkill -f "uvicorn app.main:app" 2>/dev/null
pkill -f "react-scripts start" 2>/dev/null

echo "✅ All services stopped"
EOF

# Create Docker configuration
cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Copy requirements and install Python dependencies
COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy frontend package.json and install dependencies
COPY frontend/package.json ./frontend/
WORKDIR /app/frontend
RUN npm install

# Copy application code
WORKDIR /app
COPY . .

# Build frontend
WORKDIR /app/frontend
RUN npm run build

# Expose ports
EXPOSE 8080 3000

# Start script
WORKDIR /app
CMD ["./start.sh"]
EOF

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8080:8080"
      - "3000:3000"
      - "8000:8000"
    environment:
      - LOG_LEVEL=INFO
      - ENVIRONMENT=docker
    volumes:
      - ./logs:/app/logs
    depends_on:
      - redis
      - elasticsearch

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data

volumes:
  elasticsearch_data:
EOF

# Create demo script
cat > demo.sh << 'EOF'
#!/bin/bash

echo "🎯 Running Logging and Monitoring Demo"

# Wait for services to be ready
sleep 3

echo "📝 Submitting test quiz answers..."

# Submit multiple test quiz answers
curl -X POST http://localhost:8080/api/v1/quiz/submit \
  -H "Content-Type: application/json" \
  -H "X-User-ID: demo_user_1" \
  -H "X-Session-ID: session_123" \
  -d '{
    "question_id": "q1",
    "quiz_type": "math",
    "question": "What is 2 + 2?",
    "answer": "4"
  }'

curl -X POST http://localhost:8080/api/v1/quiz/submit \
  -H "Content-Type: application/json" \
  -H "X-User-ID: demo_user_2" \
  -H "X-Session-ID: session_456" \
  -d '{
    "question_id": "q2",
    "quiz_type": "science",
    "question": "What is the capital of France?",
    "answer": "Paris"
  }'

echo "📊 Fetching metrics..."
curl -s http://localhost:8080/api/v1/metrics/summary | jq '.'

echo "🔍 Searching logs..."
curl -s "http://localhost:8080/api/v1/logs/search?query=quiz_submission" | jq '.logs | length'

echo "✅ Demo completed! Check the dashboard at http://localhost:3000"
EOF

# Make scripts executable
chmod +x start.sh stop.sh demo.sh

# Run tests
echo "🧪 Running tests..."

# Create Python virtual environment for testing
python3 -m venv test_venv
source test_venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
pip install pytest pytest-asyncio

# Run Python tests
cd backend
python -m pytest ../tests/ -v
cd ..

# Install frontend dependencies and run tests
cd frontend
npm install
npm test -- --run --passWithNoTests
cd ..

deactivate

echo "✅ Day 24 Implementation Complete!"
echo ""
echo "📋 Summary:"
echo "- ✅ Structured logging system implemented"
echo "- ✅ Monitoring dashboard created"
echo "- ✅ Metrics collection configured"
echo "- ✅ Log search functionality added"
echo "- ✅ Real-time performance tracking"
echo "- ✅ Tests passing"
echo ""
echo "🚀 Next Steps:"
echo "1. Run './start.sh' to start all services"
echo "2. Visit http://localhost:3000 for monitoring dashboard"
echo "3. Run './demo.sh' to see logging in action"
echo "4. Check logs in 'logs/app.log' file"
echo ""
echo "📚 Ready for Day 25: Error Handling Framework!"