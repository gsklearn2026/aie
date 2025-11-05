from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database.base import get_db, get_query_stats
from ..services.query_optimizer import QueryOptimizer

router = APIRouter(prefix="/api/performance", tags=["performance"])

@router.get("/query-stats")
def get_performance_stats(db: Session = Depends(get_db)):
    """Get database query performance statistics"""
    stats = get_query_stats()
    
    formatted_stats = []
    for query, data in stats.items():
        avg_time = data['total_time'] / data['count'] if data['count'] > 0 else 0
        formatted_stats.append({
            'query': query,
            'count': data['count'],
            'avg_time': round(avg_time * 1000, 2),  # Convert to ms
            'max_time': round(data['max_time'] * 1000, 2),
            'total_time': round(data['total_time'] * 1000, 2)
        })
    
    # Sort by total time descending
    formatted_stats.sort(key=lambda x: x['total_time'], reverse=True)
    
    return {'query_stats': formatted_stats[:20]}  # Top 20 queries

@router.get("/index-usage")
def get_index_usage(db: Session = Depends(get_db)):
    """Get database index usage statistics"""
    optimizer = QueryOptimizer(db)
    return {'indexes': optimizer.check_index_usage()}

@router.get("/analyze-query")
def analyze_query(query: str, db: Session = Depends(get_db)):
    """Analyze a specific query"""
    optimizer = QueryOptimizer(db)
    return optimizer.analyze_query(query)

@router.post("/trigger-index-usage")
def trigger_index_usage(db: Session = Depends(get_db)):
    """Trigger queries to generate index usage statistics"""
    from ..models.models import User, Quiz
    
    # Query users by email (uses users_email_key and idx_user_email)
    users_by_email = db.query(User).filter(User.email.like('user%')).limit(5).all()
    
    # Query users by username (uses users_username_key and idx_user_username)
    users_by_username = db.query(User).filter(User.username.like('user%')).limit(5).all()
    
    # Query users by id (uses users_pkey and ix_users_id)
    users_by_id = db.query(User).filter(User.id.in_([1, 2, 3, 4, 5])).all()
    
    # Query quizzes by category (uses idx_quiz_category if exists)
    quizzes_by_category = db.query(Quiz).filter(Quiz.category == 'Python').limit(5).all()
    
    return {
        'message': 'Index usage triggered',
        'users_by_email': len(users_by_email),
        'users_by_username': len(users_by_username),
        'users_by_id': len(users_by_id),
        'quizzes_by_category': len(quizzes_by_category)
    }
