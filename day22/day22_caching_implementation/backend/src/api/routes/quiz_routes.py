from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import google.generativeai as genai
from ...services.cache_service import cache_service
from ...config.settings import get_settings

router = APIRouter(prefix="/quiz", tags=["quiz"])
settings = get_settings()

# Configure Gemini AI
genai.configure(api_key=settings.gemini_api_key)
model = genai.GenerativeModel('gemini-pro')

# Mock database functions (replace with real DB in production)
async def fetch_quiz_from_db(quiz_id: str) -> Dict:
    """Simulate database fetch"""
    return {
        "id": quiz_id,
        "title": f"Quiz {quiz_id}",
        "questions": [
            {
                "id": 1,
                "question": "What is caching?",
                "options": ["A", "B", "C", "D"],
                "correct": 0
            }
        ],
        "created_at": "2024-01-01T00:00:00Z"
    }

async def fetch_user_progress_from_db(user_id: str, quiz_id: str) -> Dict:
    """Simulate user progress fetch"""
    return {
        "user_id": user_id,
        "quiz_id": quiz_id,
        "score": 85,
        "completed": True,
        "time_spent": 300
    }

async def fetch_leaderboard_from_db(quiz_id: str) -> List[Dict]:
    """Simulate leaderboard fetch"""
    return [
        {"user_id": "user1", "score": 95, "time": 180},
        {"user_id": "user2", "score": 90, "time": 200},
        {"user_id": "user3", "score": 85, "time": 220}
    ]

@router.get("/{quiz_id}")
async def get_quiz(quiz_id: str):
    """Get quiz with caching"""
    cache_key = f"quiz:{quiz_id}"
    
    quiz_data = await cache_service.get_or_set(
        cache_key,
        fetch_quiz_from_db,
        settings.cache_quiz_ttl,
        quiz_id
    )
    
    if not quiz_data:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    return quiz_data

@router.get("/{quiz_id}/progress/{user_id}")
async def get_user_progress(quiz_id: str, user_id: str):
    """Get user progress with caching"""
    cache_key = f"user_progress:{user_id}:{quiz_id}"
    
    progress_data = await cache_service.get_or_set(
        cache_key,
        fetch_user_progress_from_db,
        settings.cache_user_progress_ttl,
        user_id,
        quiz_id
    )
    
    return progress_data or {"user_id": user_id, "quiz_id": quiz_id, "score": 0, "completed": False}

@router.get("/{quiz_id}/leaderboard")
async def get_leaderboard(quiz_id: str):
    """Get leaderboard with caching"""
    cache_key = f"leaderboard:{quiz_id}:top10"
    
    leaderboard_data = await cache_service.get_or_set(
        cache_key,
        fetch_leaderboard_from_db,
        settings.cache_leaderboard_ttl,
        quiz_id
    )
    
    return {"quiz_id": quiz_id, "leaderboard": leaderboard_data}

@router.get("/{quiz_id}/explanation/{topic}")
async def get_ai_explanation(quiz_id: str, topic: str):
    """Get AI explanation with caching"""
    cache_key = f"ai_explanation:{topic}:{hash(topic) % 10000}"
    
    async def generate_explanation():
        try:
            prompt = f"Explain {topic} in simple terms for quiz students. Keep it under 200 words."
            response = model.generate_content(prompt)
            return {"topic": topic, "explanation": response.text}
        except Exception as e:
            return {"topic": topic, "explanation": f"Explanation for {topic} (cached demo)"}
    
    explanation = await cache_service.get_or_set(
        cache_key,
        generate_explanation,
        21600  # 6 hours for AI explanations
    )
    
    return explanation

@router.post("/{quiz_id}/invalidate")
async def invalidate_quiz_cache(quiz_id: str):
    """Force invalidate quiz cache"""
    deleted_count = await cache_service.invalidate_quiz_cache(quiz_id)
    return {"message": f"Invalidated {deleted_count} cache entries for quiz {quiz_id}"}
