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
        # Get all users who have completed sessions
        user_ids_with_sessions = db.query(QuizSession.user_id).filter(
            QuizSession.is_completed == True
        ).distinct().all()
        
        user_ids = [user_id[0] for user_id in user_ids_with_sessions]
        
        if not user_ids:
            return {
                "success": True,
                "data": []
            }
        
        # Get user details for these users
        users = db.query(User).filter(User.id.in_(user_ids)).all()
        
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
        
        # Get top performers (only include users with performances)
        top_performers = []
        seen_user_ids = set()  # Track to avoid duplicates
        for user in users:
            if user.id in user_performances and user.id not in seen_user_ids:
                seen_user_ids.add(user.id)
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
