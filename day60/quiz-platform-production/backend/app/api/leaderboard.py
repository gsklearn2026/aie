from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.utils.database import get_db
from app.models.models import Score, User

router = APIRouter()

@router.get("/")
def get_leaderboard(limit: int = 10, db: Session = Depends(get_db)):
    leaderboard = db.query(
        User.username,
        func.avg(Score.score).label('avg_score'),
        func.count(Score.id).label('quiz_count')
    ).join(Score, User.id == Score.user_id)\
     .group_by(User.id, User.username)\
     .order_by(desc('avg_score'))\
     .limit(limit)\
     .all()
    
    return [
        {
            "username": row.username,
            "avg_score": round(row.avg_score, 2),
            "quiz_count": row.quiz_count
        }
        for row in leaderboard
    ]
