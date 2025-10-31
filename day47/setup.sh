#!/bin/bash

# Day 47: Results and Analytics Interface Implementation Script
# AI Engineering Quiz Platform - Analytics Dashboard

set -e

echo "🚀 Day 47: Setting up Results and Analytics Interface"
echo "=================================================="

# Create project structure
echo "📁 Creating project structure..."
mkdir -p quiz-analytics-platform/{backend,frontend,docker,tests,docs,scripts}
cd quiz-analytics-platform

# Backend structure
mkdir -p backend/{app/{models,routes,services,utils},tests,config}
mkdir -p backend/app/{analytics,database}

# Frontend structure  
mkdir -p frontend/{src/{components,pages,services,utils,styles},public,tests}
mkdir -p frontend/src/components/{dashboard,charts,analytics}

# Create requirements.txt for Python backend
cat > backend/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
sqlalchemy==2.0.23
alembic==1.13.1
psycopg2-binary==2.9.9
redis==5.0.1
pandas==2.1.3
numpy==1.25.2
matplotlib==3.8.2
seaborn==0.13.0
plotly==5.17.0
google-generativeai==0.3.2
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
python-dotenv==1.0.0
cors==1.0.1
fastapi-cors==0.0.6
aioredis==2.0.1
sqlalchemy-utils==0.41.1
EOF

# Create package.json for React frontend
cat > frontend/package.json << 'EOF'
{
  "name": "quiz-analytics-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "@testing-library/jest-dom": "^6.1.4",
    "@testing-library/react": "^13.4.0",
    "@testing-library/user-event": "^14.5.1",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "react-router-dom": "^6.17.0",
    "axios": "^1.6.0",
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0",
    "recharts": "^2.8.0",
    "date-fns": "^2.30.0",
    "lodash": "^4.17.21",
    "@mui/material": "^5.14.15",
    "@mui/icons-material": "^5.14.15",
    "@emotion/react": "^11.11.1",
    "@emotion/styled": "^11.11.0",
    "web-vitals": "^3.5.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "proxy": "http://localhost:8000"
}
EOF

# Create environment files
cat > backend/.env << 'EOF'
DATABASE_URL=postgresql://quiz_user:quiz_pass@localhost:5432/quiz_analytics
REDIS_URL=redis://localhost:6379
GEMINI_API_KEY=AIzaSyDGswqDT4wQw_bd4WZtIgYAawRDZ0Gisn8
JWT_SECRET_KEY=your-secret-key-change-in-production
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
EOF

cat > frontend/.env << 'EOF'
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
EOF

# Create main FastAPI application
cat > backend/app/main.py << 'EOF'
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
import os
from dotenv import load_dotenv

from app.routes import analytics, dashboard, auth
from app.database.connection import init_db

load_dotenv()

app = FastAPI(title="Quiz Analytics API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"message": "Quiz Analytics API is running!", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "quiz-analytics-api"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
EOF

# Create database models
cat > backend/app/models/quiz.py << 'EOF'
from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    quiz_sessions = relationship("QuizSession", back_populates="user")

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    category = Column(String)
    difficulty_level = Column(String)
    total_questions = Column(Integer)
    time_limit = Column(Integer)  # in minutes
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    questions = relationship("Question", back_populates="quiz")
    sessions = relationship("QuizSession", back_populates="quiz")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    question_text = Column(Text)
    question_type = Column(String)  # multiple_choice, true_false, text
    options = Column(Text)  # JSON string for multiple choice
    correct_answer = Column(String)
    difficulty_score = Column(Float)
    topic = Column(String)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    responses = relationship("QuestionResponse", back_populates="question")

class QuizSession(Base):
    __tablename__ = "quiz_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    score = Column(Float)
    total_questions = Column(Integer)
    correct_answers = Column(Integer)
    time_taken = Column(Integer)  # in seconds
    is_completed = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="quiz_sessions")
    quiz = relationship("Quiz", back_populates="sessions")
    responses = relationship("QuestionResponse", back_populates="session")

class QuestionResponse(Base):
    __tablename__ = "question_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("quiz_sessions.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    user_answer = Column(String)
    is_correct = Column(Boolean)
    time_taken = Column(Integer)  # in seconds
    answered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("QuizSession", back_populates="responses")
    question = relationship("Question", back_populates="responses")
EOF

# Create database connection
cat > backend/app/database/connection.py << 'EOF'
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./quiz_analytics.db")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    from app.models.quiz import Base
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")
EOF

# Create analytics service
cat > backend/app/services/analytics_service.py << 'EOF'
import google.generativeai as genai
import pandas as pd
import numpy as np
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.quiz import QuizSession, QuestionResponse, User, Quiz
from app.database.connection import get_db
import os
import json
from datetime import datetime, timedelta

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

class AnalyticsService:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def get_user_performance_summary(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Get comprehensive performance summary for a user"""
        sessions = db.query(QuizSession).filter(
            QuizSession.user_id == user_id,
            QuizSession.is_completed == True
        ).all()
        
        if not sessions:
            return {"message": "No completed sessions found"}
        
        total_sessions = len(sessions)
        total_score = sum(session.score or 0 for session in sessions)
        avg_score = total_score / total_sessions if total_sessions > 0 else 0
        
        # Calculate performance trends
        recent_sessions = sorted(sessions, key=lambda x: x.completed_at)[-10:]
        recent_scores = [session.score for session in recent_sessions if session.score]
        
        performance_trend = self._calculate_trend(recent_scores)
        
        return {
            "user_id": user_id,
            "total_sessions": total_sessions,
            "average_score": round(avg_score, 2),
            "best_score": max(session.score for session in sessions if session.score),
            "recent_performance_trend": performance_trend,
            "total_time_spent": sum(session.time_taken or 0 for session in sessions),
            "completion_rate": len([s for s in sessions if s.is_completed]) / len(sessions) * 100
        }
    
    async def get_quiz_analytics(self, db: Session, quiz_id: int) -> Dict[str, Any]:
        """Get comprehensive analytics for a specific quiz"""
        sessions = db.query(QuizSession).filter(
            QuizSession.quiz_id == quiz_id,
            QuizSession.is_completed == True
        ).all()
        
        if not sessions:
            return {"message": "No completed sessions found for this quiz"}
        
        scores = [session.score for session in sessions if session.score]
        times = [session.time_taken for session in sessions if session.time_taken]
        
        analytics = {
            "quiz_id": quiz_id,
            "total_attempts": len(sessions),
            "average_score": np.mean(scores) if scores else 0,
            "median_score": np.median(scores) if scores else 0,
            "score_distribution": self._get_score_distribution(scores),
            "average_completion_time": np.mean(times) if times else 0,
            "difficulty_rating": self._calculate_difficulty_rating(scores),
            "completion_rate": len([s for s in sessions if s.is_completed]) / len(sessions) * 100
        }
        
        # Get AI insights
        ai_insights = await self._generate_quiz_insights(analytics)
        analytics["ai_insights"] = ai_insights
        
        return analytics
    
    async def get_learning_progress(self, db: Session, user_id: int, days: int = 30) -> Dict[str, Any]:
        """Get learning progress over time"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        sessions = db.query(QuizSession).filter(
            QuizSession.user_id == user_id,
            QuizSession.completed_at >= cutoff_date,
            QuizSession.is_completed == True
        ).order_by(QuizSession.completed_at).all()
        
        daily_progress = {}
        for session in sessions:
            date_key = session.completed_at.date().isoformat()
            if date_key not in daily_progress:
                daily_progress[date_key] = {
                    "sessions_completed": 0,
                    "total_score": 0,
                    "time_spent": 0
                }
            daily_progress[date_key]["sessions_completed"] += 1
            daily_progress[date_key]["total_score"] += session.score or 0
            daily_progress[date_key]["time_spent"] += session.time_taken or 0
        
        # Generate learning insights
        progress_data = list(daily_progress.values())
        ai_recommendations = await self._generate_learning_recommendations(progress_data)
        
        return {
            "user_id": user_id,
            "period_days": days,
            "daily_progress": daily_progress,
            "total_sessions": len(sessions),
            "improvement_trend": self._calculate_improvement_trend(sessions),
            "ai_recommendations": ai_recommendations
        }
    
    async def get_realtime_dashboard_data(self, db: Session) -> Dict[str, Any]:
        """Get real-time dashboard data for overview"""
        # Get recent activity (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        
        recent_sessions = db.query(QuizSession).filter(
            QuizSession.started_at >= yesterday
        ).count()
        
        active_users = db.query(User).count()
        total_quizzes = db.query(Quiz).count()
        
        # Get performance metrics
        completed_sessions = db.query(QuizSession).filter(
            QuizSession.is_completed == True
        ).all()
        
        avg_score = np.mean([s.score for s in completed_sessions if s.score]) if completed_sessions else 0
        
        return {
            "real_time_stats": {
                "active_sessions_24h": recent_sessions,
                "total_active_users": active_users,
                "total_quizzes": total_quizzes,
                "platform_avg_score": round(avg_score, 2)
            },
            "updated_at": datetime.utcnow().isoformat()
        }
    
    def _calculate_trend(self, scores: List[float]) -> str:
        """Calculate performance trend from recent scores"""
        if len(scores) < 2:
            return "insufficient_data"
        
        recent_avg = np.mean(scores[-3:]) if len(scores) >= 3 else np.mean(scores)
        earlier_avg = np.mean(scores[:-3]) if len(scores) >= 6 else np.mean(scores[:-1])
        
        if recent_avg > earlier_avg * 1.1:
            return "improving"
        elif recent_avg < earlier_avg * 0.9:
            return "declining"
        else:
            return "stable"
    
    def _get_score_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Get score distribution in ranges"""
        if not scores:
            return {}
        
        ranges = {
            "0-20": 0, "21-40": 0, "41-60": 0, 
            "61-80": 0, "81-100": 0
        }
        
        for score in scores:
            if score <= 20:
                ranges["0-20"] += 1
            elif score <= 40:
                ranges["21-40"] += 1
            elif score <= 60:
                ranges["41-60"] += 1
            elif score <= 80:
                ranges["61-80"] += 1
            else:
                ranges["81-100"] += 1
        
        return ranges
    
    def _calculate_difficulty_rating(self, scores: List[float]) -> str:
        """Calculate quiz difficulty based on average scores"""
        if not scores:
            return "unknown"
        
        avg_score = np.mean(scores)
        if avg_score >= 80:
            return "easy"
        elif avg_score >= 60:
            return "medium"
        elif avg_score >= 40:
            return "hard"
        else:
            return "very_hard"
    
    def _calculate_improvement_trend(self, sessions: List[QuizSession]) -> Dict[str, Any]:
        """Calculate improvement trend over sessions"""
        if len(sessions) < 2:
            return {"trend": "insufficient_data"}
        
        scores = [session.score for session in sessions if session.score]
        if len(scores) < 2:
            return {"trend": "insufficient_data"}
        
        # Linear regression to find trend
        x = np.arange(len(scores))
        slope = np.polyfit(x, scores, 1)[0]
        
        return {
            "trend": "improving" if slope > 0.5 else "declining" if slope < -0.5 else "stable",
            "slope": round(slope, 3),
            "improvement_rate": f"{abs(slope):.1f} points per session"
        }
    
    async def _generate_quiz_insights(self, analytics: Dict[str, Any]) -> List[str]:
        """Generate AI-powered insights for quiz performance"""
        try:
            prompt = f"""
            Analyze this quiz performance data and provide 3 concise, actionable insights:
            
            Quiz Analytics:
            - Total attempts: {analytics['total_attempts']}
            - Average score: {analytics['average_score']:.1f}%
            - Completion rate: {analytics['completion_rate']:.1f}%
            - Difficulty rating: {analytics['difficulty_rating']}
            
            Provide insights as a JSON list of strings, each insight should be under 50 words and actionable.
            """
            
            response = self.model.generate_content(prompt)
            try:
                insights = json.loads(response.text)
                return insights if isinstance(insights, list) else [response.text]
            except:
                return [response.text]
        except Exception as e:
            return ["Unable to generate AI insights at this time"]
    
    async def _generate_learning_recommendations(self, progress_data: List[Dict]) -> List[str]:
        """Generate personalized learning recommendations"""
        try:
            prompt = f"""
            Based on this learning progress data, provide 3 personalized study recommendations:
            
            Progress Summary: {len(progress_data)} active days
            Recent Performance: {progress_data[-3:] if len(progress_data) >= 3 else progress_data}
            
            Provide recommendations as a JSON list of strings, each under 40 words and specific.
            """
            
            response = self.model.generate_content(prompt)
            try:
                recommendations = json.loads(response.text)
                return recommendations if isinstance(recommendations, list) else [response.text]
            except:
                return [response.text]
        except Exception as e:
            return ["Continue regular practice", "Focus on weaker topics", "Maintain consistent study schedule"]
EOF

# Create analytics routes
cat > backend/app/routes/analytics.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.analytics_service import AnalyticsService
from typing import Optional

router = APIRouter()
analytics_service = AnalyticsService()

@router.get("/user/{user_id}/performance")
async def get_user_performance(user_id: int, db: Session = Depends(get_db)):
    """Get comprehensive performance analytics for a user"""
    try:
        performance = await analytics_service.get_user_performance_summary(db, user_id)
        return {"success": True, "data": performance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quiz/{quiz_id}")
async def get_quiz_analytics(quiz_id: int, db: Session = Depends(get_db)):
    """Get detailed analytics for a specific quiz"""
    try:
        analytics = await analytics_service.get_quiz_analytics(db, quiz_id)
        return {"success": True, "data": analytics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/user/{user_id}/progress")
async def get_learning_progress(user_id: int, days: Optional[int] = 30, db: Session = Depends(get_db)):
    """Get learning progress over specified time period"""
    try:
        progress = await analytics_service.get_learning_progress(db, user_id, days)
        return {"success": True, "data": progress}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard/realtime")
async def get_realtime_dashboard(db: Session = Depends(get_db)):
    """Get real-time dashboard data"""
    try:
        dashboard_data = await analytics_service.get_realtime_dashboard_data(db)
        return {"success": True, "data": dashboard_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
EOF

# Create dashboard routes
cat > backend/app/routes/dashboard.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.quiz import QuizSession, User, Quiz
from typing import List, Dict, Any
from datetime import datetime, timedelta
import json

router = APIRouter()

@router.get("/overview")
async def get_dashboard_overview(db: Session = Depends(get_db)):
    """Get dashboard overview statistics"""
    try:
        # Get basic counts
        total_users = db.query(User).count()
        total_quizzes = db.query(Quiz).count()
        total_sessions = db.query(QuizSession).count()
        completed_sessions = db.query(QuizSession).filter(QuizSession.is_completed == True).count()
        
        # Get recent activity
        last_week = datetime.utcnow() - timedelta(days=7)
        recent_sessions = db.query(QuizSession).filter(QuizSession.started_at >= last_week).count()
        
        return {
            "success": True,
            "data": {
                "total_users": total_users,
                "total_quizzes": total_quizzes,
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "completion_rate": (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
                "recent_activity": recent_sessions
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/charts/performance-trends")
async def get_performance_trends(db: Session = Depends(get_db)):
    """Get performance trend data for charts"""
    try:
        # Get last 30 days of data
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        sessions = db.query(QuizSession).filter(
            QuizSession.completed_at >= thirty_days_ago,
            QuizSession.is_completed == True
        ).order_by(QuizSession.completed_at).all()
        
        # Group by date
        daily_data = {}
        for session in sessions:
            date_key = session.completed_at.date().isoformat()
            if date_key not in daily_data:
                daily_data[date_key] = {
                    "date": date_key,
                    "sessions": 0,
                    "avg_score": 0,
                    "total_score": 0
                }
            daily_data[date_key]["sessions"] += 1
            daily_data[date_key]["total_score"] += session.score or 0
        
        # Calculate averages
        chart_data = []
        for date, data in daily_data.items():
            data["avg_score"] = data["total_score"] / data["sessions"] if data["sessions"] > 0 else 0
            chart_data.append(data)
        
        return {
            "success": True,
            "data": sorted(chart_data, key=lambda x: x["date"])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/charts/score-distribution")
async def get_score_distribution(db: Session = Depends(get_db)):
    """Get score distribution data for charts"""
    try:
        completed_sessions = db.query(QuizSession).filter(
            QuizSession.is_completed == True,
            QuizSession.score.isnot(None)
        ).all()
        
        score_ranges = {
            "0-20": 0, "21-40": 0, "41-60": 0, 
            "61-80": 0, "81-100": 0
        }
        
        for session in completed_sessions:
            score = session.score
            if score <= 20:
                score_ranges["0-20"] += 1
            elif score <= 40:
                score_ranges["21-40"] += 1
            elif score <= 60:
                score_ranges["41-60"] += 1
            elif score <= 80:
                score_ranges["61-80"] += 1
            else:
                score_ranges["81-100"] += 1
        
        chart_data = [{"range": k, "count": v} for k, v in score_ranges.items()]
        
        return {
            "success": True,
            "data": chart_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/top-performers")
async def get_top_performers(db: Session = Depends(get_db)):
    """Get top performing users"""
    try:
        # Get users with their average scores
        users_with_scores = db.query(
            User.id,
            User.username,
            User.full_name
        ).join(QuizSession).filter(
            QuizSession.is_completed == True
        ).all()
        
        # Calculate average scores per user
        user_performances = {}
        sessions = db.query(QuizSession).filter(QuizSession.is_completed == True).all()
        
        for session in sessions:
            user_id = session.user_id
            if user_id not in user_performances:
                user_performances[user_id] = {
                    "total_score": 0,
                    "session_count": 0
                }
            user_performances[user_id]["total_score"] += session.score or 0
            user_performances[user_id]["session_count"] += 1
        
        # Get top performers
        top_performers = []
        for user in users_with_scores:
            if user.id in user_performances:
                perf = user_performances[user.id]
                avg_score = perf["total_score"] / perf["session_count"]
                top_performers.append({
                    "user_id": user.id,
                    "username": user.username,
                    "full_name": user.full_name,
                    "average_score": round(avg_score, 2),
                    "sessions_completed": perf["session_count"]
                })
        
        # Sort by average score and take top 10
        top_performers.sort(key=lambda x: x["average_score"], reverse=True)
        
        return {
            "success": True,
            "data": top_performers[:10]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
EOF

# Create auth routes
cat > backend/app/routes/auth.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.models.quiz import User
from pydantic import BaseModel

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: str
    full_name: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username or email already registered"
        )
    
    # Create new user
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.get("/users", response_model=list[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(User).all()
    return users

@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
EOF

# Create sample data generator
cat > backend/app/utils/sample_data.py << 'EOF'
from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.models.quiz import User, Quiz, Question, QuizSession, QuestionResponse
from datetime import datetime, timedelta
import random
import json

def create_sample_data():
    """Create sample data for testing and demonstration"""
    db = SessionLocal()
    
    try:
        # Create sample users
        users_data = [
            {"username": "alice_student", "email": "alice@example.com", "full_name": "Alice Johnson"},
            {"username": "bob_learner", "email": "bob@example.com", "full_name": "Bob Smith"},
            {"username": "carol_quiz", "email": "carol@example.com", "full_name": "Carol Davis"},
            {"username": "david_study", "email": "david@example.com", "full_name": "David Wilson"},
            {"username": "eve_practice", "email": "eve@example.com", "full_name": "Eve Brown"}
        ]
        
        users = []
        for user_data in users_data:
            existing = db.query(User).filter(User.username == user_data["username"]).first()
            if not existing:
                user = User(**user_data)
                db.add(user)
                db.flush()
                users.append(user)
            else:
                users.append(existing)
        
        # Create sample quizzes
        quizzes_data = [
            {
                "title": "Python Basics",
                "description": "Test your knowledge of Python fundamentals",
                "category": "Programming",
                "difficulty_level": "beginner",
                "total_questions": 10,
                "time_limit": 30
            },
            {
                "title": "Data Structures",
                "description": "Arrays, Lists, and Trees concepts",
                "category": "Computer Science",
                "difficulty_level": "intermediate",
                "total_questions": 15,
                "time_limit": 45
            },
            {
                "title": "Machine Learning Fundamentals",
                "description": "Basic ML concepts and algorithms",
                "category": "AI/ML",
                "difficulty_level": "intermediate",
                "total_questions": 12,
                "time_limit": 40
            }
        ]
        
        quizzes = []
        for quiz_data in quizzes_data:
            existing = db.query(Quiz).filter(Quiz.title == quiz_data["title"]).first()
            if not existing:
                quiz = Quiz(**quiz_data)
                db.add(quiz)
                db.flush()
                quizzes.append(quiz)
            else:
                quizzes.append(existing)
        
        # Create sample questions for each quiz
        questions_data = {
            "Python Basics": [
                {
                    "question_text": "What is the correct way to define a function in Python?",
                    "question_type": "multiple_choice",
                    "options": json.dumps(["function myFunc():", "def myFunc():", "define myFunc():", "func myFunc():"]),
                    "correct_answer": "def myFunc():",
                    "difficulty_score": 0.2,
                    "topic": "Functions"
                },
                {
                    "question_text": "Python is case-sensitive",
                    "question_type": "true_false",
                    "options": json.dumps(["True", "False"]),
                    "correct_answer": "True",
                    "difficulty_score": 0.1,
                    "topic": "Syntax"
                }
            ]
        }
        
        for quiz in quizzes:
            if quiz.title in questions_data:
                for q_data in questions_data[quiz.title]:
                    existing = db.query(Question).filter(
                        Question.quiz_id == quiz.id,
                        Question.question_text == q_data["question_text"]
                    ).first()
                    if not existing:
                        question = Question(quiz_id=quiz.id, **q_data)
                        db.add(question)
        
        # Create sample quiz sessions with random data
        for user in users:
            for quiz in quizzes:
                # Create 3-7 sessions per user per quiz
                num_sessions = random.randint(3, 7)
                for i in range(num_sessions):
                    # Random date within last 30 days
                    days_ago = random.randint(1, 30)
                    started_at = datetime.utcnow() - timedelta(days=days_ago)
                    completed_at = started_at + timedelta(minutes=random.randint(10, quiz.time_limit))
                    
                    # Random performance metrics
                    correct_answers = random.randint(3, quiz.total_questions)
                    score = (correct_answers / quiz.total_questions) * 100
                    time_taken = random.randint(600, quiz.time_limit * 60)  # seconds
                    
                    session = QuizSession(
                        user_id=user.id,
                        quiz_id=quiz.id,
                        started_at=started_at,
                        completed_at=completed_at,
                        score=score,
                        total_questions=quiz.total_questions,
                        correct_answers=correct_answers,
                        time_taken=time_taken,
                        is_completed=True
                    )
                    db.add(session)
        
        db.commit()
        print("Sample data created successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating sample data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
EOF

# Create React App structure
echo "🔧 Creating React frontend components..."

# Main App component
cat > frontend/src/App.js << 'EOF'
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Dashboard from './components/dashboard/Dashboard';
import UserAnalytics from './components/analytics/UserAnalytics';
import QuizAnalytics from './components/analytics/QuizAnalytics';
import Navigation from './components/Navigation';
import './App.css';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2196f3',
    },
    secondary: {
      main: '#ff9800',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <div className="App">
          <Navigation />
          <main style={{ padding: '20px', marginTop: '64px' }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/user/:userId" element={<UserAnalytics />} />
              <Route path="/quiz/:quizId" element={<QuizAnalytics />} />
            </Routes>
          </main>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;
EOF

# Navigation component
cat > frontend/src/components/Navigation.js << 'EOF'
import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import DashboardIcon from '@mui/icons-material/Dashboard';
import AnalyticsIcon from '@mui/icons-material/Analytics';

function Navigation() {
  const navigate = useNavigate();

  return (
    <AppBar position="fixed">
      <Toolbar>
        <DashboardIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Quiz Analytics Platform
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button color="inherit" onClick={() => navigate('/')}>
            Dashboard
          </Button>
          <Button color="inherit" onClick={() => navigate('/user/1')}>
            User Analytics
          </Button>
          <Button color="inherit" onClick={() => navigate('/quiz/1')}>
            Quiz Analytics
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
}

export default Navigation;
EOF

# Dashboard component
cat > frontend/src/components/dashboard/Dashboard.js << 'EOF'
import React, { useState, useEffect } from 'react';
import { 
  Container, Grid, Paper, Typography, Box, CircularProgress,
  Card, CardContent, CardHeader 
} from '@mui/material';
import {
  People, Quiz, TrendingUp, Assessment
} from '@mui/icons-material';
import PerformanceTrendChart from '../charts/PerformanceTrendChart';
import ScoreDistributionChart from '../charts/ScoreDistributionChart';
import TopPerformersTable from './TopPerformersTable';
import RealTimeStats from './RealTimeStats';
import { fetchDashboardOverview, fetchPerformanceTrends, fetchScoreDistribution } from '../../services/api';

function Dashboard() {
  const [overview, setOverview] = useState(null);
  const [trendData, setTrendData] = useState([]);
  const [distributionData, setDistributionData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [overviewRes, trendsRes, distributionRes] = await Promise.all([
        fetchDashboardOverview(),
        fetchPerformanceTrends(),
        fetchScoreDistribution()
      ]);
      
      setOverview(overviewRes.data.data);
      setTrendData(trendsRes.data.data);
      setDistributionData(distributionRes.data.data);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl">
      <Typography variant="h4" gutterBottom>
        Analytics Dashboard
      </Typography>
      
      <Grid container spacing={3}>
        {/* Overview Cards */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <People color="primary" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{overview?.total_users || 0}</Typography>
                  <Typography color="textSecondary">Total Users</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Quiz color="secondary" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{overview?.total_quizzes || 0}</Typography>
                  <Typography color="textSecondary">Total Quizzes</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Assessment color="success" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{overview?.total_sessions || 0}</Typography>
                  <Typography color="textSecondary">Total Sessions</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <TrendingUp color="info" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{overview?.completion_rate?.toFixed(1) || 0}%</Typography>
                  <Typography color="textSecondary">Completion Rate</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Trend Chart */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Performance Trends (Last 30 Days)
            </Typography>
            <PerformanceTrendChart data={trendData} />
          </Paper>
        </Grid>

        {/* Score Distribution */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Score Distribution
            </Typography>
            <ScoreDistributionChart data={distributionData} />
          </Paper>
        </Grid>

        {/* Real-time Stats */}
        <Grid item xs={12} md={6}>
          <RealTimeStats />
        </Grid>

        {/* Top Performers */}
        <Grid item xs={12} md={6}>
          <TopPerformersTable />
        </Grid>
      </Grid>
    </Container>
  );
}

export default Dashboard;
EOF

# Performance Trend Chart component
cat > frontend/src/components/charts/PerformanceTrendChart.js << 'EOF'
import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { format, parseISO } from 'date-fns';

function PerformanceTrendChart({ data }) {
  const formattedData = data.map(item => ({
    ...item,
    date: format(parseISO(item.date), 'MMM dd'),
    avg_score: Math.round(item.avg_score * 10) / 10
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={formattedData}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis 
          dataKey="date" 
          tick={{ fontSize: 12 }}
        />
        <YAxis 
          domain={[0, 100]}
          tick={{ fontSize: 12 }}
        />
        <Tooltip 
          formatter={(value, name) => [
            `${value}${name === 'avg_score' ? '%' : ''}`,
            name === 'avg_score' ? 'Average Score' : 'Sessions'
          ]}
          labelFormatter={(label) => `Date: ${label}`}
        />
        <Legend />
        <Line 
          type="monotone" 
          dataKey="avg_score" 
          stroke="#2196f3" 
          strokeWidth={2}
          dot={{ r: 4 }}
          name="Average Score (%)"
        />
        <Line 
          type="monotone" 
          dataKey="sessions" 
          stroke="#ff9800" 
          strokeWidth={2}
          dot={{ r: 4 }}
          name="Daily Sessions"
        />
      </LineChart>
    </ResponsiveContainer>
  );
}

export default PerformanceTrendChart;
EOF

# Score Distribution Chart component
cat > frontend/src/components/charts/ScoreDistributionChart.js << 'EOF'
import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts';

function ScoreDistributionChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis 
          dataKey="range" 
          tick={{ fontSize: 12 }}
        />
        <YAxis tick={{ fontSize: 12 }} />
        <Tooltip 
          formatter={(value) => [value, 'Students']}
          labelFormatter={(label) => `Score Range: ${label}%`}
        />
        <Bar 
          dataKey="count" 
          fill="#4caf50"
          radius={[4, 4, 0, 0]}
        />
      </BarChart>
    </ResponsiveContainer>
  );
}

export default ScoreDistributionChart;
EOF

# Real-time stats component
cat > frontend/src/components/dashboard/RealTimeStats.js << 'EOF'
import React, { useState, useEffect } from 'react';
import { 
  Paper, Typography, Box, Chip, CircularProgress 
} from '@mui/material';
import { Speed, TrendingUp, Update } from '@mui/icons-material';
import { fetchRealtimeDashboard } from '../../services/api';

function RealTimeStats() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRealtimeStats();
    const interval = setInterval(loadRealtimeStats, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const loadRealtimeStats = async () => {
    try {
      const response = await fetchRealtimeDashboard();
      setStats(response.data.data.real_time_stats);
      setLoading(false);
    } catch (error) {
      console.error('Error loading real-time stats:', error);
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Paper sx={{ p: 2 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
          <CircularProgress />
        </Box>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2 }}>
      <Box display="flex" alignItems="center" justifyContent="between" mb={2}>
        <Typography variant="h6" gutterBottom>
          Real-Time Statistics
        </Typography>
        <Chip 
          icon={<Update />} 
          label="Live" 
          color="success" 
          variant="outlined" 
          size="small"
        />
      </Box>
      
      <Box spacing={2}>
        <Box display="flex" alignItems="center" mb={2}>
          <Speed color="primary" sx={{ mr: 2 }} />
          <Box>
            <Typography variant="h5">{stats?.active_sessions_24h || 0}</Typography>
            <Typography color="textSecondary">Active Sessions (24h)</Typography>
          </Box>
        </Box>
        
        <Box display="flex" alignItems="center" mb={2}>
          <TrendingUp color="success" sx={{ mr: 2 }} />
          <Box>
            <Typography variant="h5">{stats?.platform_avg_score || 0}%</Typography>
            <Typography color="textSecondary">Platform Average Score</Typography>
          </Box>
        </Box>
        
        <Box mt={2}>
          <Typography variant="body2" color="textSecondary">
            Data updates every 10 seconds
          </Typography>
        </Box>
      </Box>
    </Paper>
  );
}

export default RealTimeStats;
EOF

# Top Performers Table component
cat > frontend/src/components/dashboard/TopPerformersTable.js << 'EOF'
import React, { useState, useEffect } from 'react';
import {
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Avatar,
  Box,
  CircularProgress
} from '@mui/material';
import { EmojiEvents, Person } from '@mui/icons-material';
import { fetchTopPerformers } from '../../services/api';

function TopPerformersTable() {
  const [performers, setPerformers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadTopPerformers();
  }, []);

  const loadTopPerformers = async () => {
    try {
      const response = await fetchTopPerformers();
      setPerformers(response.data.data);
    } catch (error) {
      console.error('Error loading top performers:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRankColor = (index) => {
    switch (index) {
      case 0: return 'gold';
      case 1: return 'silver';
      case 2: return '#cd7f32';
      default: return 'primary';
    }
  };

  if (loading) {
    return (
      <Paper sx={{ p: 2 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
          <CircularProgress />
        </Box>
      </Paper>
    );
  }

  return (
    <Paper sx={{ p: 2 }}>
      <Box display="flex" alignItems="center" mb={2}>
        <EmojiEvents sx={{ mr: 1, color: 'gold' }} />
        <Typography variant="h6">
          Top Performers
        </Typography>
      </Box>
      
      <TableContainer>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Rank</TableCell>
              <TableCell>User</TableCell>
              <TableCell align="right">Avg Score</TableCell>
              <TableCell align="right">Sessions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {performers.slice(0, 5).map((performer, index) => (
              <TableRow key={performer.user_id}>
                <TableCell>
                  <Chip 
                    size="small"
                    label={`#${index + 1}`}
                    sx={{ 
                      bgcolor: index < 3 ? getRankColor(index) : 'default',
                      color: index < 3 ? 'white' : 'default'
                    }}
                  />
                </TableCell>
                <TableCell>
                  <Box display="flex" alignItems="center">
                    <Avatar sx={{ width: 24, height: 24, mr: 1 }}>
                      <Person fontSize="small" />
                    </Avatar>
                    <Box>
                      <Typography variant="body2" fontWeight="medium">
                        {performer.full_name || performer.username}
                      </Typography>
                      <Typography variant="caption" color="textSecondary">
                        @{performer.username}
                      </Typography>
                    </Box>
                  </Box>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body2" fontWeight="bold" color="primary">
                    {performer.average_score}%
                  </Typography>
                </TableCell>
                <TableCell align="right">
                  <Typography variant="body2">
                    {performer.sessions_completed}
                  </Typography>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Paper>
  );
}

export default TopPerformersTable;
EOF

# API service
cat > frontend/src/services/api.js << 'EOF'
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
});

// Dashboard APIs
export const fetchDashboardOverview = () => api.get('/api/dashboard/overview');
export const fetchPerformanceTrends = () => api.get('/api/dashboard/charts/performance-trends');
export const fetchScoreDistribution = () => api.get('/api/dashboard/charts/score-distribution');
export const fetchTopPerformers = () => api.get('/api/dashboard/top-performers');
export const fetchRealtimeDashboard = () => api.get('/api/analytics/dashboard/realtime');

// Analytics APIs
export const fetchUserPerformance = (userId) => api.get(`/api/analytics/user/${userId}/performance`);
export const fetchQuizAnalytics = (quizId) => api.get(`/api/analytics/quiz/${quizId}`);
export const fetchLearningProgress = (userId, days = 30) => 
  api.get(`/api/analytics/user/${userId}/progress?days=${days}`);

// Auth APIs
export const registerUser = (userData) => api.post('/api/auth/register', userData);
export const fetchUsers = () => api.get('/api/auth/users');

export default api;
EOF

# User Analytics component
cat > frontend/src/components/analytics/UserAnalytics.js << 'EOF'
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Container, Grid, Paper, Typography, Box, CircularProgress,
  Card, CardContent, Chip, List, ListItem, ListItemText
} from '@mui/material';
import {
  TrendingUp, School, Speed, CheckCircle
} from '@mui/icons-material';
import { fetchUserPerformance, fetchLearningProgress } from '../../services/api';

function UserAnalytics() {
  const { userId } = useParams();
  const [performance, setPerformance] = useState(null);
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUserAnalytics();
  }, [userId]);

  const loadUserAnalytics = async () => {
    try {
      setLoading(true);
      const [perfRes, progRes] = await Promise.all([
        fetchUserPerformance(userId),
        fetchLearningProgress(userId)
      ]);
      
      setPerformance(perfRes.data.data);
      setProgress(progRes.data.data);
    } catch (error) {
      console.error('Error loading user analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const getTrendColor = (trend) => {
    switch (trend) {
      case 'improving': return 'success';
      case 'declining': return 'error';
      default: return 'default';
    }
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'improving': return '📈';
      case 'declining': return '📉';
      default: return '📊';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl">
      <Typography variant="h4" gutterBottom>
        User Analytics - User #{userId}
      </Typography>
      
      <Grid container spacing={3}>
        {/* Performance Overview */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <School color="primary" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{performance?.average_score || 0}%</Typography>
                  <Typography color="textSecondary">Average Score</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <CheckCircle color="success" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{performance?.total_sessions || 0}</Typography>
                  <Typography color="textSecondary">Total Sessions</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <TrendingUp color="info" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{performance?.best_score || 0}%</Typography>
                  <Typography color="textSecondary">Best Score</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Speed color="warning" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{performance?.completion_rate?.toFixed(1) || 0}%</Typography>
                  <Typography color="textSecondary">Completion Rate</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Performance Trend */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Performance Trend
            </Typography>
            <Box display="flex" alignItems="center" mb={2}>
              <Typography variant="h3" sx={{ mr: 2 }}>
                {getTrendIcon(performance?.recent_performance_trend)}
              </Typography>
              <Box>
                <Chip 
                  label={performance?.recent_performance_trend || 'stable'}
                  color={getTrendColor(performance?.recent_performance_trend)}
                  sx={{ mb: 1 }}
                />
                <Typography variant="body2" color="textSecondary">
                  Based on recent quiz sessions
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Grid>

        {/* Learning Progress */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Learning Progress (Last 30 Days)
            </Typography>
            <Box>
              <Typography variant="body1" gutterBottom>
                Sessions Completed: {progress?.total_sessions || 0}
              </Typography>
              <Typography variant="body1" gutterBottom>
                Improvement Trend: 
                <Chip 
                  label={progress?.improvement_trend?.trend || 'stable'}
                  color={getTrendColor(progress?.improvement_trend?.trend)}
                  size="small"
                  sx={{ ml: 1 }}
                />
              </Typography>
              {progress?.improvement_trend?.improvement_rate && (
                <Typography variant="body2" color="textSecondary">
                  {progress.improvement_trend.improvement_rate}
                </Typography>
              )}
            </Box>
          </Paper>
        </Grid>

        {/* AI Recommendations */}
        {progress?.ai_recommendations && (
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                🤖 AI-Powered Learning Recommendations
              </Typography>
              <List>
                {progress.ai_recommendations.map((recommendation, index) => (
                  <ListItem key={index} divider={index < progress.ai_recommendations.length - 1}>
                    <ListItemText
                      primary={recommendation}
                      secondary={`Recommendation ${index + 1}`}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Container>
  );
}

export default UserAnalytics;
EOF

# Quiz Analytics component
cat > frontend/src/components/analytics/QuizAnalytics.js << 'EOF'
import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Container, Grid, Paper, Typography, Box, CircularProgress,
  Card, CardContent, List, ListItem, ListItemText, Chip
} from '@mui/material';
import {
  Quiz, People, Speed, TrendingUp
} from '@mui/icons-material';
import { fetchQuizAnalytics } from '../../services/api';

function QuizAnalytics() {
  const { quizId } = useParams();
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadQuizAnalytics();
  }, [quizId]);

  const loadQuizAnalytics = async () => {
    try {
      setLoading(true);
      const response = await fetchQuizAnalytics(quizId);
      setAnalytics(response.data.data);
    } catch (error) {
      console.error('Error loading quiz analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case 'easy': return 'success';
      case 'medium': return 'warning';
      case 'hard': return 'error';
      case 'very_hard': return 'error';
      default: return 'default';
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl">
      <Typography variant="h4" gutterBottom>
        Quiz Analytics - Quiz #{quizId}
      </Typography>
      
      <Grid container spacing={3}>
        {/* Quiz Overview */}
        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Quiz color="primary" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{analytics?.total_attempts || 0}</Typography>
                  <Typography color="textSecondary">Total Attempts</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <TrendingUp color="success" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{analytics?.average_score?.toFixed(1) || 0}%</Typography>
                  <Typography color="textSecondary">Average Score</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <Speed color="info" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{Math.round(analytics?.average_completion_time / 60) || 0}</Typography>
                  <Typography color="textSecondary">Avg Time (min)</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center">
                <People color="warning" sx={{ mr: 2, fontSize: 40 }} />
                <Box>
                  <Typography variant="h4">{analytics?.completion_rate?.toFixed(1) || 0}%</Typography>
                  <Typography color="textSecondary">Completion Rate</Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Quiz Statistics */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Quiz Statistics
            </Typography>
            <Box>
              <Box display="flex" justifyContent="space-between" mb={2}>
                <Typography>Difficulty Rating:</Typography>
                <Chip 
                  label={analytics?.difficulty_rating || 'unknown'}
                  color={getDifficultyColor(analytics?.difficulty_rating)}
                  size="small"
                />
              </Box>
              <Box display="flex" justifyContent="space-between" mb={2}>
                <Typography>Median Score:</Typography>
                <Typography fontWeight="bold">
                  {analytics?.median_score?.toFixed(1) || 0}%
                </Typography>
              </Box>
              <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>
                Score Distribution:
              </Typography>
              {analytics?.score_distribution && Object.entries(analytics.score_distribution).map(([range, count]) => (
                <Box key={range} display="flex" justifyContent="space-between" mb={1}>
                  <Typography>{range}%:</Typography>
                  <Typography fontWeight="bold">{count} students</Typography>
                </Box>
              ))}
            </Box>
          </Paper>
        </Grid>

        {/* AI Insights */}
        {analytics?.ai_insights && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                🤖 AI-Generated Insights
              </Typography>
              <List>
                {analytics.ai_insights.map((insight, index) => (
                  <ListItem key={index} divider={index < analytics.ai_insights.length - 1}>
                    <ListItemText
                      primary={insight}
                      secondary={`Insight ${index + 1}`}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Container>
  );
}

export default QuizAnalytics;
EOF

# Create CSS
cat > frontend/src/App.css << 'EOF'
.App {
  text-align: left;
}

body {
  margin: 0;
  font-family: 'Roboto', 'Helvetica', 'Arial', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background-color: #f5f5f5;
}

.MuiPaper-root {
  border-radius: 8px !important;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1) !important;
}

.MuiCard-root {
  transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.MuiCard-root:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
}

.recharts-wrapper {
  font-family: 'Roboto', sans-serif !important;
}
EOF

# Create index.js
cat > frontend/src/index.js << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

cat > frontend/src/index.css << 'EOF'
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
EOF

# Create public/index.html
cat > frontend/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Quiz Analytics Platform - AI Engineering Day 47" />
    <title>Quiz Analytics Platform</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOF

# Create tests
mkdir -p backend/tests frontend/src/tests

cat > backend/tests/test_analytics.py << 'EOF'
import pytest
import asyncio
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_dashboard_overview():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/dashboard/overview")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data" in data

@pytest.mark.asyncio
async def test_performance_trends():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/dashboard/charts/performance-trends")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_realtime_dashboard():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/analytics/dashboard/realtime")
        assert response.status_code == 200

@pytest.mark.asyncio 
async def test_user_performance():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/analytics/user/1/performance")
        assert response.status_code == 200

if __name__ == "__main__":
    asyncio.run(test_dashboard_overview())
EOF

cat > frontend/src/tests/Dashboard.test.js << 'EOF'
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Dashboard from '../components/dashboard/Dashboard';
import * as api from '../services/api';

// Mock the API
jest.mock('../services/api');

const MockedDashboard = () => (
  <BrowserRouter>
    <Dashboard />
  </BrowserRouter>
);

test('renders dashboard with loading state', () => {
  api.fetchDashboardOverview.mockResolvedValue({ data: { data: {} } });
  api.fetchPerformanceTrends.mockResolvedValue({ data: { data: [] } });
  api.fetchScoreDistribution.mockResolvedValue({ data: { data: [] } });
  
  render(<MockedDashboard />);
  expect(screen.getByRole('progressbar')).toBeInTheDocument();
});

test('renders dashboard content after loading', async () => {
  const mockOverview = {
    total_users: 100,
    total_quizzes: 50,
    total_sessions: 500,
    completion_rate: 85.5
  };
  
  api.fetchDashboardOverview.mockResolvedValue({ data: { data: mockOverview } });
  api.fetchPerformanceTrends.mockResolvedValue({ data: { data: [] } });
  api.fetchScoreDistribution.mockResolvedValue({ data: { data: [] } });
  
  render(<MockedDashboard />);
  
  await waitFor(() => {
    expect(screen.getByText('Analytics Dashboard')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument();
    expect(screen.getByText('50')).toBeInTheDocument();
  });
});
EOF

# Create Docker files
cat > docker/Dockerfile.backend << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat > docker/Dockerfile.frontend << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY frontend/ .

# Build the app
RUN npm run build

# Install serve to run the production build
RUN npm install -g serve

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000 || exit 1

# Serve the built app
CMD ["serve", "-s", "build", "-p", "3000"]
EOF

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://quiz_user:quiz_pass@postgres:5432/quiz_analytics
      - REDIS_URL=redis://redis:6379
      - GEMINI_API_KEY=AIzaSyDGswqDT4wQw_bd4WZtIgYAawRDZ0Gisn8
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
    command: ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

  frontend:
    build:
      context: .
      dockerfile: docker/Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
    command: ["npm", "start"]

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: quiz_analytics
      POSTGRES_USER: quiz_user
      POSTGRES_PASSWORD: quiz_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U quiz_user -d quiz_analytics"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
  redis_data:
EOF

# Create build script
cat > build.sh << 'EOF'
#!/bin/bash

echo "🚀 Building Quiz Analytics Platform - Day 47"
echo "============================================="

# Check if running with Docker
if [ "$1" = "--docker" ]; then
    echo "🐳 Building with Docker..."
    
    # Build and start services
    docker-compose down -v
    docker-compose build
    docker-compose up -d postgres redis
    
    echo "⏳ Waiting for database to be ready..."
    sleep 10
    
    # Start application services
    docker-compose up -d backend frontend
    
    echo "⏳ Waiting for services to start..."
    sleep 15
    
    # Create sample data
    echo "🔧 Creating sample data..."
    docker-compose exec backend python app/utils/sample_data.py
    
    echo "✅ Docker build complete!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend: http://localhost:8000"
    echo "📊 API Docs: http://localhost:8000/docs"
    
else
    echo "💻 Building without Docker..."
    
    # Setup Python backend
    echo "🔧 Setting up Python backend..."
    cd backend
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Initialize database
    echo "🗃️ Initializing database..."
    python -c "
from app.database.connection import init_db
import asyncio
asyncio.run(init_db())
"
    
    # Create sample data
    echo "📊 Creating sample data..."
    python app/utils/sample_data.py
    
    # Setup React frontend
    echo "⚛️ Setting up React frontend..."
    cd ../frontend
    npm install
    npm run build
    
    cd ..
    
    echo "✅ Build complete!"
    echo "📋 Next steps:"
    echo "   1. Run: ./start.sh (to start all services)"
    echo "   2. Run: ./start.sh --docker (to start with Docker)"
fi

# Run tests
echo "🧪 Running tests..."
if [ "$1" = "--docker" ]; then
    docker-compose exec backend python -m pytest tests/ -v
    # Frontend tests would run here
else
    cd backend
    source venv/bin/activate
    python -m pytest tests/ -v
    cd ../frontend
    npm test -- --coverage --passWithNoTests --watchAll=false
    cd ..
fi

echo "🎉 Build and test completed successfully!"
EOF

chmod +x build.sh

# Create start script
cat > start.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting Quiz Analytics Platform"
echo "=================================="

if [ "$1" = "--docker" ]; then
    echo "🐳 Starting with Docker..."
    docker-compose up -d
    
    echo "⏳ Waiting for services..."
    sleep 10
    
    echo "✅ All services started!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend: http://localhost:8000"
    echo "📊 API Documentation: http://localhost:8000/docs"
    echo "📈 Postgres Admin: localhost:5432"
    
    # Show service status
    docker-compose ps
    
else
    echo "💻 Starting without Docker..."
    
    # Start backend
    echo "🔧 Starting backend..."
    cd backend
    source venv/bin/activate
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
    BACKEND_PID=$!
    cd ..
    
    # Start frontend
    echo "⚛️ Starting frontend..."
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    echo "✅ Services started!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔧 Backend: http://localhost:8000"
    echo "📊 API Documentation: http://localhost:8000/docs"
    
    # Save PIDs for stop script
    echo $BACKEND_PID > .backend.pid
    echo $FRONTEND_PID > .frontend.pid
fi

echo "🎯 Demo completed! Analytics dashboard is ready."
echo "🔍 Check the dashboard for real-time analytics and insights."
EOF

chmod +x start.sh

# Create stop script
cat > stop.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping Quiz Analytics Platform"
echo "==================================="

if [ -f docker-compose.yml ] && docker-compose ps -q > /dev/null 2>&1; then
    echo "🐳 Stopping Docker services..."
    docker-compose down
    echo "✅ Docker services stopped!"
else
    echo "💻 Stopping local services..."
    
    if [ -f .backend.pid ]; then
        BACKEND_PID=$(cat .backend.pid)
        kill $BACKEND_PID 2>/dev/null
        rm .backend.pid
        echo "🔧 Backend stopped"
    fi
    
    if [ -f .frontend.pid ]; then
        FRONTEND_PID=$(cat .frontend.pid)
        kill $FRONTEND_PID 2>/dev/null
        rm .frontend.pid
        echo "⚛️ Frontend stopped"
    fi
    
    echo "✅ Local services stopped!"
fi
EOF

chmod +x stop.sh

# Create README
cat > README.md << 'EOF'
# Quiz Analytics Platform - Day 47

## AI Engineering Results and Analytics Interface

This project implements a comprehensive analytics dashboard for educational quiz platforms, featuring real-time data visualization, AI-powered insights, and performance tracking.

### Features

- **Real-time Analytics Dashboard**: Live statistics and performance metrics
- **Interactive Data Visualizations**: Charts showing trends, distributions, and progress
- **AI-Powered Insights**: Gemini AI generates personalized recommendations
- **User Performance Tracking**: Individual learning progress and improvement trends
- **Quiz Analytics**: Detailed analysis of quiz difficulty and performance
- **Responsive Design**: Works across desktop and mobile devices

### Technology Stack

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL, Redis
- **Frontend**: React, Material-UI, Recharts, Axios
- **AI**: Google Gemini AI for intelligent insights
- **Database**: PostgreSQL with sample educational data
- **Caching**: Redis for performance optimization
- **Containerization**: Docker and Docker Compose

### Quick Start

#### Option 1: Docker (Recommended)
```bash
./build.sh --docker
./start.sh --docker
```

#### Option 2: Local Development
```bash
./build.sh
./start.sh
```

### URLs

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Dashboard Features

1. **Main Dashboard**: Overview statistics, performance trends, score distributions
2. **User Analytics**: Individual performance tracking with AI recommendations
3. **Quiz Analytics**: Detailed quiz analysis with difficulty ratings
4. **Real-time Updates**: Live statistics updated every 10 seconds

### API Endpoints

- `GET /api/dashboard/overview` - Dashboard overview statistics
- `GET /api/dashboard/charts/performance-trends` - Performance trend data
- `GET /api/analytics/user/{id}/performance` - User performance summary
- `GET /api/analytics/quiz/{id}` - Quiz analytics with AI insights

### Testing

```bash
# Backend tests
cd backend && python -m pytest tests/ -v

# Frontend tests  
cd frontend && npm test
```

### Architecture

The system follows a modern microservices architecture:
- **API Layer**: RESTful APIs with FastAPI
- **Data Layer**: PostgreSQL for persistence, Redis for caching
- **Analytics Engine**: Real-time data processing and AI insights
- **Presentation Layer**: React with responsive Material-UI components

### Sample Data

The system includes comprehensive sample data:
- 5 sample users with varied performance
- 3 different quizzes (Python, Data Structures, ML)
- 30+ quiz sessions with realistic performance metrics
- Question responses and timing data

### Next Steps

This implementation prepares for Day 48: Error Handling and Loading States by providing a robust foundation with proper state management and API integration patterns.
EOF

echo "✅ Day 47 Implementation Complete!"
echo ""
echo "📁 Project structure created with:"
echo "   - Full-stack analytics dashboard"
echo "   - Python FastAPI backend with Gemini AI"
echo "   - React frontend with Material-UI"
echo "   - Comprehensive test suites"
echo "   - Docker containerization"
echo "   - Sample educational data"
echo ""
echo "🚀 Next steps:"
echo "   1. Run: ./build.sh --docker"
echo "   2. Visit: http://localhost:3000"
echo "   3. Explore the analytics dashboard!"