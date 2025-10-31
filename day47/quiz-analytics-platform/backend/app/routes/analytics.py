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
