from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
import google.generativeai as genai
import os
import json
import random

from app.utils.database import get_db
from app.models.models import Quiz, Score, User
from app.api.auth import get_current_user
from app.utils.redis_client import redis_client

router = APIRouter()

# Gemini API key is optional - fallback questions will be used if not available
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

def generate_fallback_quiz(topic: str, difficulty: str, num_questions: int) -> List[dict]:
    """Generate basic quiz questions as fallback when API is unavailable"""
    questions = []
    base_questions = {
        "easy": [
            {"question": f"What is {topic}?", "options": ["A programming language", "A database", "A framework", "A tool"], "correct_answer": 0},
            {"question": f"Which of these is related to {topic}?", "options": ["Variables", "Functions", "Classes", "All of the above"], "correct_answer": 3},
            {"question": f"In {topic}, what is a common feature?", "options": ["Syntax", "Semantics", "Both", "Neither"], "correct_answer": 2},
        ],
        "medium": [
            {"question": f"How does {topic} handle data?", "options": ["Sequentially", "In parallel", "Both ways", "Neither"], "correct_answer": 2},
            {"question": f"What is a key concept in {topic}?", "options": ["Abstraction", "Encapsulation", "Polymorphism", "All of the above"], "correct_answer": 3},
            {"question": f"Which best describes {topic}?", "options": ["Simple", "Complex", "Versatile", "All of the above"], "correct_answer": 3},
        ],
        "hard": [
            {"question": f"What is an advanced feature of {topic}?", "options": ["Basic operations", "Advanced algorithms", "Complex data structures", "All of the above"], "correct_answer": 3},
            {"question": f"How would you optimize {topic}?", "options": ["Caching", "Indexing", "Both", "Neither"], "correct_answer": 2},
            {"question": f"What is the best practice for {topic}?", "options": ["Follow conventions", "Use patterns", "Document code", "All of the above"], "correct_answer": 3},
        ]
    }
    
    # Get questions for the difficulty level
    available_questions = base_questions.get(difficulty, base_questions["medium"])
    
    # Repeat questions if needed
    for i in range(num_questions):
        base_q = available_questions[i % len(available_questions)]
        # Customize question with topic
        question = {
            "question": base_q["question"].replace("{topic}", topic),
            "options": base_q["options"],
            "correct_answer": base_q["correct_answer"]
        }
        questions.append(question)
    
    return questions

class QuizRequest(BaseModel):
    topic: str
    difficulty: str = "medium"
    num_questions: int = 5

class QuizAnswer(BaseModel):
    quiz_id: int
    answers: List[int]

@router.post("/generate")
async def generate_quiz(
    request: QuizRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Check cache first
        cache_key = f"quiz:{request.topic}:{request.difficulty}:{request.num_questions}"
        cached_quiz = await redis_client.get(cache_key)
        
        if cached_quiz:
            questions = json.loads(cached_quiz)
        else:
            # Generate using Gemini - try multiple models for quota availability
            # If no API key, use fallback immediately
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                questions = generate_fallback_quiz(request.topic, request.difficulty, request.num_questions)
            else:
                try:
                    # Try different models - gemini-pro usually has better quota than experimental models
                    models_to_try = ['gemini-pro', 'gemini-1.5-pro', 'gemini-2.0-flash-exp']
                    response = None
                    last_error = None
                    
                    for model_name in models_to_try:
                    try:
                        model = genai.GenerativeModel(model_name)
                        prompt = f"""Generate {request.num_questions} multiple choice questions about {request.topic} at {request.difficulty} difficulty.
                        Return ONLY a JSON array with this exact structure, no other text:
                        [{{"question": "...", "options": ["A", "B", "C", "D"], "correct_answer": 0}}]
                        The correct_answer is the index (0-3) of the correct option."""
                        
                        response = model.generate_content(prompt)
                        break  # Success, exit loop
                    except Exception as e:
                        last_error = e
                        error_str = str(e).lower()
                        # If quota error, try next model
                        if "quota" in error_str or "429" in error_str or "resource exhausted" in error_str:
                            continue  # Try next model
                        # If model not found, try next
                        if "not found" in error_str or "404" in error_str:
                            continue  # Try next model
                        raise  # Re-raise if it's a different error
                
                if response is None:
                    # All models failed, use fallback
                    questions = generate_fallback_quiz(request.topic, request.difficulty, request.num_questions)
                else:
                    questions_text = response.text.strip()
                    
                    # Clean up response
                    if "```json" in questions_text:
                        questions_text = questions_text.split("```json")[1].split("```")[0].strip()
                    elif "```" in questions_text:
                        questions_text = questions_text.split("```")[1].split("```")[0].strip()
                    
                    questions = json.loads(questions_text)
                
                    # Cache for 1 hour
                    await redis_client.setex(cache_key, 3600, json.dumps(questions))
                except Exception as e:
                # If Gemini API fails, use fallback instead of error
                error_msg = str(e).lower()
                if "quota" in error_msg or "429" in error_msg or "resource exhausted" in error_msg:
                    # Use fallback questions when quota is exceeded
                    questions = generate_fallback_quiz(request.topic, request.difficulty, request.num_questions)
                    # Cache fallback questions too
                    await redis_client.setex(cache_key, 3600, json.dumps(questions))
                else:
                    # For other errors, try fallback as well
                    try:
                        questions = generate_fallback_quiz(request.topic, request.difficulty, request.num_questions)
                        await redis_client.setex(cache_key, 3600, json.dumps(questions))
                    except:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Failed to generate quiz: {str(e)}"
                        )
        
        # Save quiz
        quiz = Quiz(
            user_id=current_user.id,
            topic=request.topic,
            difficulty=request.difficulty,
            questions=questions
        )
        db.add(quiz)
        db.commit()
        db.refresh(quiz)
        
        return {"quiz_id": quiz.id, "questions": questions}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create quiz: {str(e)}")

@router.post("/submit")
def submit_quiz(
    submission: QuizAnswer,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    quiz = db.query(Quiz).filter(Quiz.id == submission.quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Calculate score
    correct = 0
    for i, answer in enumerate(submission.answers):
        if i < len(quiz.questions) and answer == quiz.questions[i]["correct_answer"]:
            correct += 1
    
    score_pct = (correct / len(quiz.questions)) * 100
    
    score = Score(
        user_id=current_user.id,
        quiz_id=quiz.id,
        score=score_pct,
        total_questions=len(quiz.questions)
    )
    db.add(score)
    db.commit()
    
    return {
        "score": score_pct,
        "correct": correct,
        "total": len(quiz.questions)
    }
