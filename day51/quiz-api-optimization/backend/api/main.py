from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from backend.middleware.compression import CompressionMiddleware
from backend.middleware.caching import cache_response
from backend.cache.redis_cache import cache_manager
from backend.monitoring.metrics import init_db, get_performance_stats, record_metric
from backend.models.quiz import Quiz, Question
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from backend.config.settings import settings
import google.generativeai as genai
import time
import random

app = FastAPI(title="Quiz API Optimization")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add compression middleware
app.add_middleware(CompressionMiddleware)

# Database setup
engine = create_async_engine(settings.DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

@app.on_event("startup")
async def startup():
    await init_db()
    await cache_manager.connect()
    # Seed sample data
    await seed_sample_data()

@app.on_event("shutdown")
async def shutdown():
    await cache_manager.disconnect()

async def seed_sample_data():
    async with async_session() as session:
        # Check if data exists
        result = await session.execute(select(Quiz))
        if result.first():
            return
            
        # Create sample quizzes
        quizzes = [
            Quiz(title="Python Basics", description="Test your Python knowledge", difficulty="Easy", category="Programming"),
            Quiz(title="Data Structures", description="Advanced data structures", difficulty="Medium", category="Computer Science"),
            Quiz(title="Machine Learning", description="ML fundamentals", difficulty="Hard", category="AI"),
        ]
        
        for quiz in quizzes:
            session.add(quiz)
        await session.commit()
        
        # Create sample questions
        for quiz_id in range(1, 4):
            for i in range(20):
                question = Question(
                    quiz_id=quiz_id,
                    question_text=f"Sample question {i+1} for quiz {quiz_id}?",
                    option_a="Option A",
                    option_b="Option B",
                    option_c="Option C",
                    option_d="Option D",
                    correct_answer=random.choice(['A', 'B', 'C', 'D']),
                    explanation="Sample explanation",
                    points=10
                )
                session.add(question)
        await session.commit()

@app.get("/")
async def root():
    return {"message": "Quiz API Optimization System", "status": "running"}

@app.get("/api/quizzes")
@cache_response(ttl=1800, key_prefix="quizzes_list")
async def get_quizzes(
    fields: str = Query(None, description="Comma-separated fields to return"),
    limit: int = Query(10, le=100)
):
    start_time = time.time()
    
    async with async_session() as session:
        stmt = select(Quiz).limit(limit)
        result = await session.execute(stmt)
        quizzes = result.scalars().all()
        
        quiz_data = []
        for quiz in quizzes:
            data = {
                "id": quiz.id,
                "title": quiz.title,
                "description": quiz.description,
                "difficulty": quiz.difficulty,
                "category": quiz.category,
                "created_at": str(quiz.created_at),
                "updated_at": str(quiz.updated_at)
            }
            
            # Field filtering
            if fields:
                requested_fields = [f.strip() for f in fields.split(',')]
                data = {k: v for k, v in data.items() if k in requested_fields}
                
            quiz_data.append(data)
    
    response = {
        "quizzes": quiz_data,
        "count": len(quiz_data),
        "optimization_enabled": True
    }
    
    return response

@app.get("/api/quiz/{quiz_id}")
@cache_response(ttl=3600, key_prefix="quiz_detail")
async def get_quiz(
    quiz_id: int,
    fields: str = Query(None, description="Comma-separated fields"),
    include_questions: bool = Query(True)
):
    start_time = time.time()
    
    async with async_session() as session:
        # Get quiz
        stmt = select(Quiz).where(Quiz.id == quiz_id)
        result = await session.execute(stmt)
        quiz = result.scalar_one_or_none()
        
        if not quiz:
            return JSONResponse({"error": "Quiz not found"}, status_code=404)
            
        quiz_data = {
            "id": quiz.id,
            "title": quiz.title,
            "description": quiz.description,
            "difficulty": quiz.difficulty,
            "category": quiz.category,
            "created_at": str(quiz.created_at)
        }
        
        # Get questions if requested
        if include_questions:
            stmt = select(Question).where(Question.quiz_id == quiz_id)
            result = await session.execute(stmt)
            questions = result.scalars().all()
            
            quiz_data["questions"] = [
                {
                    "id": q.id,
                    "question_text": q.question_text,
                    "options": {
                        "A": q.option_a,
                        "B": q.option_b,
                        "C": q.option_c,
                        "D": q.option_d
                    },
                    "correct_answer": q.correct_answer,
                    "explanation": q.explanation,
                    "points": q.points
                }
                for q in questions
            ]
            
        # Field filtering
        if fields:
            requested_fields = [f.strip() for f in fields.split(',')]
            quiz_data = {k: v for k, v in quiz_data.items() if k in requested_fields}
            
    return quiz_data

@app.get("/api/quiz/{quiz_id}/generate-ai")
async def generate_quiz_content(quiz_id: int):
    """Generate quiz content using Gemini AI (not cached for demo)"""
    start_time = time.time()
    
    prompt = f"Generate 3 multiple choice questions about programming with 4 options each."
    
    try:
        response = model.generate_content(prompt)
        return {
            "quiz_id": quiz_id,
            "ai_generated_content": response.text,
            "generation_time_ms": int((time.time() - start_time) * 1000)
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/metrics/performance")
async def get_metrics():
    stats = await get_performance_stats(limit=50)
    cache_stats = await cache_manager.get_stats()
    
    return {
        "performance_by_endpoint": stats,
        "cache_statistics": cache_stats,
        "timestamp": time.time()
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "compression": settings.ENABLE_COMPRESSION,
        "caching": settings.ENABLE_CACHING,
        "redis_connected": cache_manager.redis_client is not None
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
