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
