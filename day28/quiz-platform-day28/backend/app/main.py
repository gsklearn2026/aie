from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from sqlalchemy.orm import Session
import redis
import json
import os
from datetime import datetime
from typing import Optional, List
import logging

from .config.database import get_db, init_db
from .config.redis_config import get_redis
from .services.export_service import ExportService
from .models.export_models import ExportRequest, ExportJob, ExportStatus
from .api.export_routes import router as export_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Quiz Platform - Export Service",
    description="High-performance data export service for quiz analytics",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(export_router, prefix="/api/v1/export", tags=["export"])

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    # Database tables are already created manually
    # init_db()  # Skip database initialization
    logger.info("Export service started successfully")

@app.get("/")
async def root():
    return {
        "message": "AI Quiz Platform Export Service",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        redis_client = get_redis()
        redis_client.ping()
        return {"status": "healthy", "timestamp": datetime.utcnow()}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")
