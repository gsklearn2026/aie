from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import logging

from pools.database_pool import initialize_db_pool, get_db_pool
from pools.gemini_pool import initialize_gemini_pool, get_gemini_pool
from services.quiz_service import QuizService

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Quiz Platform - Day 53")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pools on startup
@app.on_event("startup")
async def startup():
    try:
        # Initialize database pool
        db_url = os.getenv("DATABASE_URL", "postgresql://quizuser:quizpass@localhost:5432/quizdb")
        db_min = int(os.getenv("DB_POOL_MIN", 5))
        db_max = int(os.getenv("DB_POOL_MAX", 50))
        
        initialize_db_pool(db_url, db_min, db_max)
        logger.info("✅ Database pool initialized")
        
        # Initialize Gemini pool
        gemini_key = os.getenv("GEMINI_API_KEY")
        ai_pool_size = int(os.getenv("AI_POOL_SIZE", 10))
        ai_rate_limit = int(os.getenv("AI_RATE_LIMIT_PER_MIN", 50))
        
        initialize_gemini_pool(gemini_key, ai_pool_size, ai_rate_limit)
        logger.info("✅ Gemini AI pool initialized")
        
        # Create quiz table
        QuizService.create_quiz_table()
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise

@app.on_event("shutdown")
async def shutdown():
    try:
        get_db_pool().close_all()
        logger.info("✅ Pools closed gracefully")
    except Exception as e:
        logger.error(f"❌ Shutdown error: {e}")

class QuizRequest(BaseModel):
    topic: str
    difficulty: str = "medium"

@app.get("/")
async def root():
    return {"message": "Quiz Platform API - Day 53: Connection Pooling", "status": "running"}

@app.post("/api/quiz/generate")
async def generate_quiz(request: QuizRequest):
    try:
        quiz = QuizService.generate_and_store_quiz(request.topic, request.difficulty)
        return {"success": True, "quiz": quiz}
    except Exception as e:
        logger.error(f"❌ Error generating quiz: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/quiz/list")
async def list_quizzes():
    try:
        quizzes = QuizService.get_all_quizzes()
        return {"success": True, "quizzes": quizzes, "count": len(quizzes)}
    except Exception as e:
        logger.error(f"❌ Error listing quizzes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/metrics/pools")
async def get_pool_metrics():
    try:
        db_metrics = get_db_pool().get_metrics()
        gemini_metrics = get_gemini_pool().get_metrics()
        
        return {
            "success": True,
            "metrics": {
                "database": db_metrics,
                "gemini_ai": gemini_metrics
            }
        }
    except Exception as e:
        logger.error(f"❌ Error getting metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy", "pools": "active"}
