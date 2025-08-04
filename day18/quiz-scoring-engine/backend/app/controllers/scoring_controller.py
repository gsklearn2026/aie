from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import List, Optional
import redis

from ..models.scoring_models import QuizSubmission, ScoreResult, UserPerformanceMetrics, ScoringStrategy
from ..services.scoring_service import ScoringService
from config.settings import settings

router = APIRouter(prefix="/scoring", tags=["scoring"])

# Dependency to get scoring service
def get_scoring_service() -> ScoringService:
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return ScoringService(redis_client)

@router.post("/calculate", response_model=ScoreResult)
async def calculate_score(
    submission: QuizSubmission,
    background_tasks: BackgroundTasks,
    scoring_service: ScoringService = Depends(get_scoring_service)
):
    """Calculate score for a quiz submission"""
    try:
        result = await scoring_service.calculate_score(submission)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating score: {str(e)}")

@router.get("/user/{user_id}/metrics", response_model=UserPerformanceMetrics)
async def get_user_metrics(
    user_id: str,
    scoring_service: ScoringService = Depends(get_scoring_service)
):
    """Get user performance metrics"""
    try:
        metrics = await scoring_service.get_user_performance_metrics(user_id)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting user metrics: {str(e)}")

@router.get("/strategies")
async def get_available_strategies():
    """Get list of available scoring strategies"""
    return {
        "strategies": [
            {
                "name": strategy.value,
                "description": _get_strategy_description(strategy)
            }
            for strategy in ScoringStrategy
        ]
    }

def _get_strategy_description(strategy: ScoringStrategy) -> str:
    descriptions = {
        ScoringStrategy.BASIC: "Simple correct/incorrect scoring with equal weighting",
        ScoringStrategy.WEIGHTED: "Accounts for question difficulty and importance",
        ScoringStrategy.ADAPTIVE: "Adjusts based on user performance and question difficulty",
        ScoringStrategy.CONFIDENCE: "Includes user confidence levels in scoring"
    }
    return descriptions.get(strategy, "Unknown strategy")

@router.post("/demo/sample-quiz")
async def create_sample_quiz_submission():
    """Create a sample quiz submission for demo purposes"""
    from ..models.scoring_models import QuestionAnswer
    
    sample_answers = [
        QuestionAnswer(
            question_id="q1",
            answer="Paris",
            is_correct=True,
            time_taken=15.5,
            difficulty=2.0,
            weight=1.0,
            confidence=4
        ),
        QuestionAnswer(
            question_id="q2", 
            answer="Berlin",
            is_correct=False,
            time_taken=25.3,
            difficulty=3.0,
            weight=1.5,
            confidence=2
        ),
        QuestionAnswer(
            question_id="q3",
            answer="Tokyo",
            is_correct=True,
            time_taken=12.1,
            difficulty=1.0,
            weight=1.0,
            confidence=5
        )
    ]
    
    return QuizSubmission(
        quiz_id="demo-quiz-001",
        user_id="demo-user-123",
        answers=sample_answers,
        total_time=52.9,
        strategy=ScoringStrategy.CONFIDENCE,
        metadata={"quiz_type": "geography", "level": "intermediate"}
    )
