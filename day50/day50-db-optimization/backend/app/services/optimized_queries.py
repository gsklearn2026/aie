from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, desc
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from ..models.models import Quiz, Question, QuizAttempt, User

class OptimizedQueries:
    """Repository with optimized database queries"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # OPTIMIZED: Single query with JOIN instead of N+1
    def get_quizzes_with_questions(self, category: Optional[str] = None) -> List[Quiz]:
        """Fetch quizzes with questions in a single query"""
        query = self.db.query(Quiz).options(joinedload(Quiz.questions))
        
        if category:
            query = query.filter(Quiz.category == category)
        
        return query.filter(Quiz.is_active == True).all()
    
    # OPTIMIZED: Uses composite index on (user_id, created_at)
    def get_user_recent_attempts(self, user_id: int, days: int = 30) -> List[QuizAttempt]:
        """Get user's recent quiz attempts (optimized with index)"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        return self.db.query(QuizAttempt).filter(
            and_(
                QuizAttempt.user_id == user_id,
                QuizAttempt.created_at >= cutoff_date
            )
        ).order_by(desc(QuizAttempt.created_at)).all()
    
    # OPTIMIZED: Single query with aggregation
    def get_leaderboard(self, quiz_id: Optional[int] = None, limit: int = 10) -> List[Dict]:
        """Get top scorers (optimized with indexes and aggregation)"""
        query = self.db.query(
            User.username,
            func.avg(QuizAttempt.score).label('avg_score'),
            func.count(QuizAttempt.id).label('attempts')
        ).join(QuizAttempt)
        
        if quiz_id:
            query = query.filter(QuizAttempt.quiz_id == quiz_id)
        
        return query.group_by(User.id, User.username)\
            .order_by(desc('avg_score'))\
            .limit(limit)\
            .all()
    
    # OPTIMIZED: Uses covering index
    def get_quiz_statistics(self, quiz_id: int) -> Dict:
        """Get quiz statistics with optimized aggregation"""
        stats = self.db.query(
            func.count(QuizAttempt.id).label('total_attempts'),
            func.avg(QuizAttempt.score).label('avg_score'),
            func.max(QuizAttempt.score).label('max_score'),
            func.min(QuizAttempt.score).label('min_score')
        ).filter(QuizAttempt.quiz_id == quiz_id).first()
        
        return {
            'total_attempts': stats[0] or 0,
            'average_score': float(stats[1] or 0),
            'max_score': float(stats[2] or 0),
            'min_score': float(stats[3] or 0)
        }
    
    # OPTIMIZED: Category performance with JOIN
    def get_category_performance(self, user_id: int) -> List[Dict]:
        """Get user performance by category"""
        results = self.db.query(
            Quiz.category,
            func.avg(QuizAttempt.score).label('avg_score'),
            func.count(QuizAttempt.id).label('attempts')
        ).join(QuizAttempt).filter(
            QuizAttempt.user_id == user_id
        ).group_by(Quiz.category).all()
        
        return [
            {
                'category': r[0],
                'average_score': float(r[1]),
                'attempts': r[2]
            }
            for r in results
        ]
