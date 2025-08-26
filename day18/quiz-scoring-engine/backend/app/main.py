from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import redis
from contextlib import asynccontextmanager

from .controllers.scoring_controller import router as scoring_router
from .services.scoring_service import ScoringService
from config.settings import settings

# Global services
redis_client = None
scoring_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global redis_client, scoring_service
    try:
        redis_client = redis.from_url(settings.redis_url, decode_responses=True)
        scoring_service = ScoringService(redis_client)
        yield
    except Exception as e:
        print(f"Error during startup: {e}")
        yield
    finally:
        # Shutdown
        if redis_client:
            redis_client.close()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
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

# Include routers
app.include_router(scoring_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Quiz Scoring Engine API", "version": settings.app_version}

@app.get("/health")
async def health_check():
    try:
        redis_client.ping()
        return {"status": "healthy", "redis": "connected"}
    except:
        return {"status": "degraded", "redis": "disconnected"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
