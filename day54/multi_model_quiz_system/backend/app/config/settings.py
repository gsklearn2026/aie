from pydantic_settings import BaseSettings
from typing import Dict, Any

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://quizuser:quizpass@localhost:5432/quizdb"
    REDIS_URL: str = "redis://localhost:6379/0"
    GEMINI_API_KEY: str = ""  # Set via environment variable or .env file
    
    # Model Profiles Configuration
    MODEL_PROFILES: Dict[str, Dict[str, Any]] = {
        "multiple_choice_expert": {
            "temperature": 0.3,
            "max_tokens": 800,
            "model_name": "gemini-2.0-flash",
            "system_prompt": "You are a precise quiz creator specializing in multiple-choice questions. Create clear, unambiguous questions with one correct answer and three plausible distractors.",
            "cost_tier": "standard",
            "max_retry": 2
        },
        "true_false_efficient": {
            "temperature": 0.2,
            "max_tokens": 400,
            "model_name": "gemini-2.0-flash",
            "system_prompt": "You are an efficient quiz creator for true/false questions. Create clear, factual statements that are definitively true or false.",
            "cost_tier": "economy",
            "max_retry": 2
        },
        "short_answer_balanced": {
            "temperature": 0.4,
            "max_tokens": 600,
            "model_name": "gemini-2.0-flash",
            "system_prompt": "You are a quiz creator for short answer questions. Create questions that require concise, specific answers demonstrating understanding.",
            "cost_tier": "standard",
            "max_retry": 2
        },
        "essay_creative": {
            "temperature": 0.7,
            "max_tokens": 1200,
            "model_name": "gemini-2.5-pro",
            "system_prompt": "You are a thought-provoking educator creating essay questions. Design questions that encourage critical thinking, analysis, and creative expression.",
            "cost_tier": "premium",
            "max_retry": 3
        },
        "coding_specialist": {
            "temperature": 0.35,
            "max_tokens": 1000,
            "model_name": "gemini-2.5-pro",
            "system_prompt": "You are a programming quiz specialist. Create coding questions with clear requirements, test cases, and proper syntax highlighting needs.",
            "cost_tier": "premium",
            "max_retry": 2
        },
        "general_fallback": {
            "temperature": 0.5,
            "max_tokens": 800,
            "model_name": "gemini-2.0-flash",
            "system_prompt": "You are a versatile quiz creator. Generate high-quality questions for any subject and question type.",
            "cost_tier": "standard",
            "max_retry": 1
        }
    }
    
    # Routing rules
    ROUTING_RULES: Dict[str, str] = {
        "multiple_choice": "multiple_choice_expert",
        "true_false": "true_false_efficient",
        "short_answer": "short_answer_balanced",
        "essay": "essay_creative",
        "coding": "coding_specialist"
    }
    
    # Quality thresholds
    QUALITY_THRESHOLD: float = 3.5
    FALLBACK_CHAIN: list = ["general_fallback"]
    
    class Config:
        env_file = ".env"

settings = Settings()
