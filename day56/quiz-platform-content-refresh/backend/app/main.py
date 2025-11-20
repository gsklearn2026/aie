from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from app.core.config import settings
from app.core.database import engine, Base
from app.api import content, jobs, metrics, versions
from app.jobs.scheduler import start_scheduler, shutdown_scheduler

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application", version="1.0.0")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    start_scheduler()
    yield
    # Shutdown
    shutdown_scheduler()
    logger.info("Application shutdown complete")

app = FastAPI(
    title="Quiz Platform - Content Refresh Service",
    description="Automated content lifecycle management with AI-powered refresh",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://0.0.0.0:3000"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(content.router, prefix="/api/content", tags=["Content"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])
app.include_router(versions.router, prefix="/api/versions", tags=["Versions"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "content-refresh"}
