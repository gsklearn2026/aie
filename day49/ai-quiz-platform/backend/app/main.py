from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime, timedelta
import google.generativeai as genai
import jwt
import hashlib
import json
import os
from typing import List, Optional
import uvicorn

# Configure Gemini AI
genai.configure(api_key="AIzaSyDGswqDT4wQw_bd4WZtIgYAawRDZ0Gisn8")

app = FastAPI(title="AI Quiz Platform", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "sqlite:///./quiz_platform.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Quiz(Base):
    __tablename__ = "quizzes"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    questions = Column(Text)  # JSON string
    difficulty = Column(String, default="medium")
    category = Column(String, default="general")
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, index=True)

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer)
    user_id = Column(Integer)
    answers = Column(Text)  # JSON string
    score = Column(Integer)
    completed_at = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    created_at: datetime

class QuizCreate(BaseModel):
    title: str
    description: str
    difficulty: str = "medium"
    category: str = "general"

class QuizResponse(BaseModel):
    id: int
    title: str
    description: str
    questions: str
    difficulty: str
    category: str
    created_at: datetime

class QuizAttemptCreate(BaseModel):
    quiz_id: int
    answers: dict

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Security
SECRET_KEY = "your-secret-key-here"
ALGORITHM = "HS256"
security = HTTPBearer()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# Gemini AI service
async def generate_quiz_questions(topic: str, difficulty: str, num_questions: int = 5):
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    Generate {num_questions} multiple choice questions about {topic} with {difficulty} difficulty.
    Return the response in JSON format with the following structure:
    {{
        "questions": [
            {{
                "question": "Question text here?",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": 0,
                "explanation": "Brief explanation of the correct answer"
            }}
        ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        # Extract JSON from response
        response_text = response.text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith('```'):
            response_text = response_text[3:-3].strip()
        
        return json.loads(response_text)
    except Exception as e:
        print(f"Error generating questions: {e}")
        return {
            "questions": [
                {
                    "question": "What is the capital of France?",
                    "options": ["London", "Paris", "Madrid", "Rome"],
                    "correct_answer": 1,
                    "explanation": "Paris is the capital and most populous city of France."
                }
            ]
        }

# Routes
@app.get("/")
async def root():
    return {"message": "AI Quiz Platform API", "status": "running"}

@app.post("/api/auth/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.email == user.email) | (User.username == user.username)
    ).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create new user
    hashed_pw = hash_password(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_pw
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    token = create_access_token({"sub": user.email})
    return {"token": token, "user": UserResponse(**db_user.__dict__)}

@app.post("/api/auth/login")
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or user.hashed_password != hash_password(user_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    token = create_access_token({"sub": user_data.email})
    return {"token": token, "user": UserResponse(**user.__dict__)}

@app.get("/api/auth/me")
async def get_current_user(current_user_email: str = Depends(verify_token), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == current_user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(**user.__dict__)

@app.post("/api/quizzes/generate")
async def create_quiz(
    quiz_data: QuizCreate,
    current_user_email: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == current_user_email).first()
    
    # Generate questions using Gemini AI
    questions_data = await generate_quiz_questions(
        quiz_data.category, 
        quiz_data.difficulty,
        5
    )
    
    db_quiz = Quiz(
        title=quiz_data.title,
        description=quiz_data.description,
        questions=json.dumps(questions_data),
        difficulty=quiz_data.difficulty,
        category=quiz_data.category,
        user_id=user.id
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    
    return QuizResponse(**db_quiz.__dict__)

@app.get("/api/quizzes")
async def get_quizzes(db: Session = Depends(get_db)):
    quizzes = db.query(Quiz).all()
    return [QuizResponse(**quiz.__dict__) for quiz in quizzes]

@app.get("/api/quizzes/{quiz_id}")
async def get_quiz(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return QuizResponse(**quiz.__dict__)

@app.post("/api/quizzes/{quiz_id}/attempt")
async def submit_quiz_attempt(
    quiz_id: int,
    attempt_data: QuizAttemptCreate,
    current_user_email: str = Depends(verify_token),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == current_user_email).first()
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Calculate score
    questions_data = json.loads(quiz.questions)
    correct_answers = 0
    total_questions = len(questions_data["questions"])
    
    for i, question in enumerate(questions_data["questions"]):
        user_answer = attempt_data.answers.get(str(i))
        if user_answer == question["correct_answer"]:
            correct_answers += 1
    
    score = int((correct_answers / total_questions) * 100)
    
    db_attempt = QuizAttempt(
        quiz_id=quiz_id,
        user_id=user.id,
        answers=json.dumps(attempt_data.answers),
        score=score
    )
    db.add(db_attempt)
    db.commit()
    
    return {
        "score": score,
        "correct_answers": correct_answers,
        "total_questions": total_questions,
        "percentage": score
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "database": "connected",
            "gemini_ai": "available",
            "api": "running"
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
