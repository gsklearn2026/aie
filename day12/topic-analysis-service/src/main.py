import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import List, Dict, Any
import structlog
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
import redis.asyncio as redis
from dotenv import load_dotenv

from models import TopicAnalysisRequest, TopicAnalysisResponse, HealthResponse
from topic_analyzer import TopicAnalyzer
from cache import CacheManager

# Load environment variables
load_dotenv()

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
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Metrics
REQUEST_COUNT = Counter('topic_analysis_requests_total', 'Total topic analysis requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('topic_analysis_request_duration_seconds', 'Request duration')
ANALYSIS_COUNT = Counter('topic_analysis_completed_total', 'Completed analyses', ['status'])

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Topic Analysis Service")
    
    # Initialize Redis connection
    app.state.redis = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
    
    # Initialize components
    app.state.cache_manager = CacheManager(app.state.redis)
    app.state.topic_analyzer = TopicAnalyzer(
        api_key=os.getenv("ANTHROPIC_API_KEY"),
        cache_manager=app.state.cache_manager
    )
    
    logger.info("Service initialization complete")
    yield
    
    # Shutdown
    logger.info("Shutting down Topic Analysis Service")
    await app.state.redis.close()

app = FastAPI(
    title="Topic Analysis Service",
    description="AI-powered topic extraction and categorization service",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files and templates
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = asyncio.get_event_loop().time()
    response = await call_next(request)
    process_time = asyncio.get_event_loop().time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    REQUEST_DURATION.observe(process_time)
    return response

@app.get("/", include_in_schema=False)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Test Redis connection
        await app.state.redis.ping()
        
        return HealthResponse(
            status="healthy",
            service="topic-analysis-service",
            version="1.0.0"
        )
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/analyze", response_model=TopicAnalysisResponse)
async def analyze_topics(
    request: TopicAnalysisRequest,
    background_tasks: BackgroundTasks
):
    """Analyze topics in provided content"""
    REQUEST_COUNT.labels(method="POST", endpoint="/analyze").inc()
    
    try:
        logger.info("Processing topic analysis request", content_length=len(request.content))
        
        # Perform topic analysis
        analysis_result = await app.state.topic_analyzer.analyze(
            content=request.content,
            options=request.options
        )
        
        ANALYSIS_COUNT.labels(status="success").inc()
        
        logger.info("Topic analysis completed successfully", 
                   topics_count=len(analysis_result.topics))
        
        return analysis_result
        
    except Exception as e:
        ANALYSIS_COUNT.labels(status="error").inc()
        logger.error("Topic analysis failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/cache/stats")
async def cache_stats():
    """Cache statistics endpoint"""
    try:
        stats = await app.state.cache_manager.get_stats()
        return {"cache_stats": stats}
    except Exception as e:
        logger.error("Failed to get cache stats", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get cache stats")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None
    )
