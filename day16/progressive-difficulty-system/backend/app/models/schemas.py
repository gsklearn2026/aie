from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime

class LearningState(str, Enum):
    WARMING_UP = "warming_up"
    OPTIMAL_CHALLENGE = "optimal_challenge"
    STRUGGLING = "struggling"
    MASTERY = "mastery"

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"

class QuestionResponse(BaseModel):
    question_id: str
    is_correct: bool
    response_time_ms: int
    confidence_score: float = Field(ge=0.0, le=1.0)
    attempts: int = 1
    timestamp: datetime

class SessionData(BaseModel):
    session_id: str
    start_time: datetime
    questions_answered: int
    current_streak: int
    session_duration_ms: int

class UserPerformance(BaseModel):
    user_id: str
    recent_responses: List[QuestionResponse]
    session_data: SessionData
    historical_accuracy: float = Field(ge=0.0, le=1.0)
    learning_velocity: float
    consistency_score: float = Field(ge=0.0, le=1.0)

class DifficultyRequest(BaseModel):
    user_id: str
    recent_performance: List[QuestionResponse]
    session_data: SessionData
    subject_area: Optional[str] = None

class DifficultyResponse(BaseModel):
    recommended_difficulty: DifficultyLevel
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    user_state: LearningState
    adjustment_factors: Dict[str, Any]
    next_question_criteria: Dict[str, Any]

class UserStateInfo(BaseModel):
    user_id: str
    current_state: LearningState
    difficulty_level: DifficultyLevel
    performance_trend: str
    sessions_completed: int
    total_questions_answered: int
    current_accuracy: float
    confidence_level: float
    last_updated: datetime
