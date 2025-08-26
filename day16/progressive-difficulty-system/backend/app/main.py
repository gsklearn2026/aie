from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from .services.difficulty_engine import ProgressiveDifficultyEngine
from .models.schemas import UserPerformance, DifficultyRequest, DifficultyResponse
from config.settings import get_settings
import structlog

logger = structlog.get_logger()

# Global engine instance
difficulty_engine = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global difficulty_engine
    settings = get_settings()
    difficulty_engine = ProgressiveDifficultyEngine(settings)
    await difficulty_engine.initialize()
    logger.info("Progressive Difficulty Engine initialized")
    yield
    await difficulty_engine.cleanup()
    logger.info("Progressive Difficulty Engine cleaned up")

app = FastAPI(
    title="Progressive Difficulty Algorithm",
    description="Adaptive learning difficulty management system",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "progressive-difficulty"}

@app.post("/api/v1/difficulty/next", response_model=DifficultyResponse)
async def get_next_difficulty(request: DifficultyRequest):
    """Get next question difficulty level based on user performance"""
    try:
        result = await difficulty_engine.calculate_next_difficulty(
            user_id=request.user_id,
            recent_performance=request.recent_performance,
            current_session_data=request.session_data
        )
        return result
    except Exception as e:
        logger.error("Error calculating difficulty", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/performance/update")
async def update_performance(performance: UserPerformance):
    """Update user performance metrics"""
    try:
        await difficulty_engine.update_user_performance(performance)
        return {"status": "updated", "user_id": performance.user_id}
    except Exception as e:
        logger.error("Error updating performance", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/user/{user_id}/state")
async def get_user_state(user_id: str):
    """Get current user learning state"""
    try:
        state = await difficulty_engine.get_user_state(user_id)
        return state
    except Exception as e:
        logger.error("Error getting user state", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
