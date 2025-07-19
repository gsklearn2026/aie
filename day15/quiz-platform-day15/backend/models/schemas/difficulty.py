from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate" 
    ADVANCED = "advanced"
    EXPERT = "expert"

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    TRUE_FALSE = "true_false"
    FILL_BLANK = "fill_blank"

class QuestionRequest(BaseModel):
    question_text: str = Field(..., min_length=5, max_length=2000)
    subject: str = Field(..., min_length=2, max_length=50)
    question_type: QuestionType
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    context: Optional[str] = None

class FeatureVector(BaseModel):
    readability_score: float
    syntactic_complexity: float
    vocabulary_difficulty: float
    concept_density: float
    cognitive_load: float
    question_type_complexity: float

class DifficultyResponse(BaseModel):
    question_id: Optional[str] = None
    difficulty_level: DifficultyLevel
    difficulty_score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    features: FeatureVector
    processing_time_ms: float
    reasoning: str

class BatchRequest(BaseModel):
    questions: List[QuestionRequest]
    
class BatchResponse(BaseModel):
    results: List[DifficultyResponse]
    total_processed: int
    average_processing_time_ms: float
