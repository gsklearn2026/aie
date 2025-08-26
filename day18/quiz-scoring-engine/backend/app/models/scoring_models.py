from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from enum import Enum
import datetime

class ScoringStrategy(str, Enum):
    BASIC = "basic"
    WEIGHTED = "weighted" 
    ADAPTIVE = "adaptive"
    CONFIDENCE = "confidence"

class QuestionAnswer(BaseModel):
    question_id: str
    answer: str
    is_correct: bool
    time_taken: float = Field(gt=0, description="Time in seconds")
    difficulty: float = Field(ge=1, le=5, description="Question difficulty 1-5")
    weight: float = Field(ge=0.1, le=5.0, default=1.0)
    confidence: Optional[int] = Field(None, ge=1, le=5, description="User confidence 1-5")

class QuizSubmission(BaseModel):
    quiz_id: str
    user_id: str
    answers: List[QuestionAnswer]
    total_time: float
    strategy: ScoringStrategy = ScoringStrategy.WEIGHTED
    metadata: Dict[str, Any] = {}

class ScoreResult(BaseModel):
    quiz_id: str
    user_id: str
    raw_score: float
    normalized_score: float
    percentile_rank: Optional[float] = None
    strategy_used: ScoringStrategy
    breakdown: Dict[str, Any]
    timestamp: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

class UserPerformanceMetrics(BaseModel):
    user_id: str
    average_score: float
    total_quizzes: int
    performance_trend: List[float]
    difficulty_preferences: Dict[str, float]
