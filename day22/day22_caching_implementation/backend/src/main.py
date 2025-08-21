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
    await redis_client.redis.ping()
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
    redis_status = "healthy" if await redis_client.redis.ping() else "unhealthy"
    
    return {
        "status": "healthy",
        "redis": redis_status,
        "cache_enabled": True
    }
