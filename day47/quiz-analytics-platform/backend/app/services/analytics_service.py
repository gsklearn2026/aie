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
