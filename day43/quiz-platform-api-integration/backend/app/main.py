"""Main FastAPI application with API integration layer"""
import os
import asyncio
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog
from .core.config import settings
from .api import router
from .services.cache_service import CacheService
from .services.ai_service import AIService

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

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown handling"""
    logger.info("Starting API Integration Layer")
    
    # Initialize services
    cache_service = CacheService()
    ai_service = AIService()
    
    app.state.cache_service = cache_service
    app.state.ai_service = ai_service
    
    await cache_service.connect()
    logger.info("Cache service connected")
    
    yield
    
    # Cleanup
    await cache_service.disconnect()
    logger.info("Application shutdown complete")

app = FastAPI(
    title="Quiz Platform API Integration Layer",
    description="Production-ready API integration with error handling and caching",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "api-integration-layer",
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
