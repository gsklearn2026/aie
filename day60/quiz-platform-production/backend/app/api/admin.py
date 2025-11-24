from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.utils.database import get_db
from app.models.models import User, Quiz, Score
from app.api.auth import get_current_user

router = APIRouter()

def require_admin(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.get("/stats")
def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if user is admin
    if not current_user.is_admin:
        # Return empty stats for non-admin users instead of 403
        return {
            "total_users": 0,
            "total_quizzes": 0,
            "total_submissions": 0,
            "average_score": 0,
            "message": "Admin access required for detailed statistics"
        }
    
    # Refresh user from database to get latest admin status
    db.refresh(current_user)
    
    # Double-check admin status after refresh
    if not current_user.is_admin:
        return {
            "total_users": 0,
            "total_quizzes": 0,
            "total_submissions": 0,
            "average_score": 0,
            "message": "Admin access required for detailed statistics"
        }
    
    total_users = db.query(func.count(User.id)).scalar()
    total_quizzes = db.query(func.count(Quiz.id)).scalar()
    total_submissions = db.query(func.count(Score.id)).scalar()
    avg_score = db.query(func.avg(Score.score)).scalar() or 0
    
    return {
        "total_users": total_users,
        "total_quizzes": total_quizzes,
        "total_submissions": total_submissions,
        "average_score": round(avg_score, 2)
    }
