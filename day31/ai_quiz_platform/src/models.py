"""Data models for the quiz platform."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class DifficultyLevel(str, Enum):
    """Quiz difficulty levels."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class QuestionType(str, Enum):
    """Question types supported by the platform."""

    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"


class Question(BaseModel):
    """Individual quiz question model."""

    id: Optional[str] = None
    text: str = Field(..., min_length=10, max_length=1000)
    type: QuestionType
    difficulty: DifficultyLevel
    options: Optional[List[str]] = None
    correct_answer: str
    explanation: Optional[str] = None
    points: int = Field(default=1, ge=1, le=10)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("options")
    @classmethod
    def validate_options(cls, v, info):
        """Validate options based on question type."""
        if info.data.get("type") == QuestionType.MULTIPLE_CHOICE and (not v or len(v) < 2):
            raise ValueError("Multiple choice questions must have at least 2 options")
        return v


class Quiz(BaseModel):
    """Quiz model containing multiple questions."""

    id: Optional[str] = None
    title: str = Field(..., min_length=5, max_length=200)
    description: Optional[str] = None
    questions: List[Question] = Field(..., min_length=1)
    difficulty: DifficultyLevel
    time_limit: Optional[int] = Field(None, ge=60, le=7200)  # seconds
    max_attempts: int = Field(default=3, ge=1, le=10)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def total_points(self) -> int:
        """Calculate total points for the quiz."""
        return sum(q.points for q in self.questions)


class UserPerformance(BaseModel):
    """User performance tracking model."""

    user_id: str
    quiz_id: str
    score: int = Field(ge=0)
    max_score: int = Field(gt=0)
    completion_time: int  # seconds
    difficulty: DifficultyLevel
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    @property
    def percentage_score(self) -> float:
        """Calculate percentage score."""
        return (self.score / self.max_score) * 100

    @property
    def performance_rating(self) -> str:
        """Get performance rating based on score."""
        percentage = self.percentage_score
        if percentage >= 90:
            return "excellent"
        elif percentage >= 80:
            return "good"
        elif percentage >= 70:
            return "fair"
        else:
            return "needs_improvement"


class QuizGenerationRequest(BaseModel):
    """Request model for AI-powered quiz generation."""

    topic: str = Field(..., min_length=2, max_length=100)
    difficulty: DifficultyLevel
    question_count: int = Field(default=5, ge=1, le=20)
    question_types: List[QuestionType] = Field(
        default_factory=lambda: [QuestionType.MULTIPLE_CHOICE]
    )
    time_limit: Optional[int] = Field(None, ge=60, le=7200)
    focus_areas: List[str] = Field(default_factory=list)


class QuizResponse(BaseModel):
    """Response model for quiz operations."""

    success: bool
    message: str
    quiz: Optional[Quiz] = None
    errors: List[str] = Field(default_factory=list)
