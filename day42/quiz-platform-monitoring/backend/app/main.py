from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from prometheus_client.exposition import CONTENT_TYPE_LATEST
import psutil
import time
import asyncio
from typing import Dict, Any
import uvicorn
from starlette.responses import Response
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Quiz Platform Monitoring API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
REQUEST_COUNT = Counter('quiz_platform_requests_total', 'Total requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('quiz_platform_request_duration_seconds', 'Request duration')
ACTIVE_USERS = Gauge('quiz_platform_active_users', 'Active users count')
SYSTEM_CPU = Gauge('quiz_platform_cpu_usage_percent', 'CPU usage percentage')
SYSTEM_MEMORY = Gauge('quiz_platform_memory_usage_percent', 'Memory usage percentage')
QUIZ_QUESTIONS_SERVED = Counter('quiz_platform_questions_served_total', 'Total questions served')
AI_API_CALLS = Counter('quiz_platform_ai_api_calls_total', 'Total AI API calls', ['status'])

# In-memory storage for demo
active_users_count = 0
quiz_stats = {
    'questions_answered': 0,
    'total_users': 0,
    'avg_response_time': 0.0,
    'error_rate': 0.0
}

@app.middleware("http")
async def monitor_requests(request, call_next):
    """Middleware to monitor all requests"""
    start_time = time.time()
    
    response = await call_next(request)
    
    # Record metrics
    duration = time.time() - start_time
    REQUEST_DURATION.observe(duration)
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    
    return response

@app.on_event("startup")
async def startup_event():
    """Initialize monitoring on startup"""
    logger.info("Starting monitoring service...")
    # Start background task to update system metrics
    asyncio.create_task(update_system_metrics())

async def update_system_metrics():
    """Background task to update system metrics"""
    while True:
        try:
            # Update system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            SYSTEM_CPU.set(cpu_percent)
            SYSTEM_MEMORY.set(memory_percent)
            ACTIVE_USERS.set(active_users_count)
            
            logger.info(f"System metrics updated - CPU: {cpu_percent}%, Memory: {memory_percent}%")
            
        except Exception as e:
            logger.error(f"Error updating system metrics: {e}")
        
        await asyncio.sleep(10)  # Update every 10 seconds

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "Quiz Platform Monitoring",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    cpu_percent = psutil.cpu_percent()
    memory_percent = psutil.virtual_memory().percent
    
    status = "healthy"
    if cpu_percent > 80 or memory_percent > 80:
        status = "warning"
    if cpu_percent > 95 or memory_percent > 95:
        status = "critical"
    
    return {
        "status": status,
        "cpu_usage": cpu_percent,
        "memory_usage": memory_percent,
        "active_users": active_users_count,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/api/dashboard/stats")
async def get_dashboard_stats():
    """Get current dashboard statistics"""
    return {
        "activeUsers": active_users_count,
        "questionsAnswered": quiz_stats['questions_answered'],
        "avgResponseTime": quiz_stats['avg_response_time'],
        "errorRate": quiz_stats['error_rate'],
        "systemHealth": {
            "cpu": psutil.cpu_percent(),
            "memory": psutil.virtual_memory().percent,
            "status": "healthy" if psutil.cpu_percent() < 80 else "warning"
        }
    }

@app.post("/api/quiz/answer")
async def submit_quiz_answer(answer_data: Dict[Any, Any]):
    """Simulate quiz answer submission"""
    global active_users_count
    
    # Simulate processing time
    processing_time = time.time()
    await asyncio.sleep(0.1)  # Simulate work
    
    # Update metrics
    QUIZ_QUESTIONS_SERVED.inc()
    quiz_stats['questions_answered'] += 1
    quiz_stats['avg_response_time'] = time.time() - processing_time
    
    # Simulate AI API call
    AI_API_CALLS.labels(status="success").inc()
    
    return {
        "success": True,
        "score": 85,
        "feedback": "Great job!",
        "processing_time": time.time() - processing_time
    }

@app.post("/api/users/login")
async def user_login():
    """Simulate user login"""
    global active_users_count
    active_users_count += 1
    quiz_stats['total_users'] = active_users_count
    
    return {
        "success": True,
        "user_id": f"user_{active_users_count}",
        "session_token": "fake_token_123"
    }

@app.post("/api/users/logout")  
async def user_logout():
    """Simulate user logout"""
    global active_users_count
    if active_users_count > 0:
        active_users_count -= 1
    
    return {"success": True}

@app.post("/api/simulate/load")
async def simulate_load():
    """Simulate system load for testing"""
    global active_users_count
    active_users_count += 10
    quiz_stats['questions_answered'] += 50
    
    return {
        "message": "Load simulation started",
        "new_active_users": active_users_count
    }

@app.post("/api/simulate/error")
async def simulate_error():
    """Simulate error for testing alerting"""
    quiz_stats['error_rate'] = 25.0  # 25% error rate
    raise HTTPException(status_code=500, detail="Simulated error for testing")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
