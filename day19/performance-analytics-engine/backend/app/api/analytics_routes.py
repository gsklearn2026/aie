from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from ..database import get_db
from ..models import QuizAttempt, PerformanceMetric, LearningInsight, AnalyticsEvent
from ..services.insight_generator import InsightGenerator
from ..services.analytics_processor import AnalyticsProcessor

router = APIRouter()

@router.post("/events")
async def create_analytics_event(
    event_data: dict,
    db: AsyncSession = Depends(get_db)
):
    """Create a new analytics event"""
    event = AnalyticsEvent(
        event_type=event_data.get("event_type"),
        user_id=event_data.get("user_id"),
        quiz_id=event_data.get("quiz_id"),
        topic_id=event_data.get("topic_id"),
        data=event_data.get("data", {})
    )
    
    db.add(event)
    await db.commit()
    await db.refresh(event)
    
    return {"message": "Event created", "event_id": event.id}

@router.get("/user/{user_id}/performance")
async def get_user_performance(
    user_id: str,
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get user performance analytics"""
    start_date = datetime.now() - timedelta(days=days)
    
    # Get quiz attempts
    attempts_result = await db.execute(
        select(QuizAttempt)
        .where(QuizAttempt.user_id == user_id)
        .where(QuizAttempt.completed_at >= start_date)
        .order_by(QuizAttempt.completed_at.desc())
    )
    attempts = attempts_result.scalars().all()
    
    # Get performance metrics
    metrics_result = await db.execute(
        select(PerformanceMetric)
        .where(PerformanceMetric.user_id == user_id)
        .where(PerformanceMetric.calculated_at >= start_date)
    )
    metrics = metrics_result.scalars().all()
    
    # Calculate summary statistics
    if attempts:
        total_score = sum(attempt.score for attempt in attempts)
        total_possible = sum(attempt.max_score for attempt in attempts)
        average_score = (total_score / total_possible) * 100 if total_possible > 0 else 0
        
        topic_performance = {}
        for attempt in attempts:
            if attempt.topic_id not in topic_performance:
                topic_performance[attempt.topic_id] = {
                    "attempts": 0,
                    "total_score": 0,
                    "max_score": 0
                }
            
            perf = topic_performance[attempt.topic_id]
            perf["attempts"] += 1
            perf["total_score"] += attempt.score
            perf["max_score"] += attempt.max_score
        
        # Calculate topic averages
        for topic_id, perf in topic_performance.items():
            perf["average_percentage"] = (perf["total_score"] / perf["max_score"]) * 100
    else:
        average_score = 0
        topic_performance = {}
    
    return {
        "user_id": user_id,
        "period_days": days,
        "summary": {
            "total_attempts": len(attempts),
            "average_score_percentage": average_score,
            "topics_attempted": len(topic_performance)
        },
        "topic_performance": topic_performance,
        "recent_metrics": [
            {
                "type": metric.metric_type,
                "value": metric.value,
                "topic_id": metric.topic_id,
                "calculated_at": metric.calculated_at.isoformat(),
                "metadata": metric.metadata_json or {}
            }
            for metric in metrics
        ]
    }

@router.get("/user/{user_id}/insights")
async def get_user_insights(
    user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get AI-generated learning insights for a user"""
    insight_generator = InsightGenerator()
    insights = await insight_generator.generate_user_insights(user_id)
    
    # Also get stored insights from database
    stored_insights_result = await db.execute(
        select(LearningInsight)
        .where(LearningInsight.user_id == user_id)
        .where(LearningInsight.is_active == True)
        .order_by(LearningInsight.generated_at.desc())
        .limit(10)
    )
    stored_insights = stored_insights_result.scalars().all()
    
    return {
        "fresh_insights": insights,
        "stored_insights": [
            {
                "id": insight.id,
                "type": insight.insight_type,
                "title": insight.title,
                "description": insight.description,
                "confidence": insight.confidence_score,
                "action_items": insight.action_items,
                "generated_at": insight.generated_at.isoformat()
            }
            for insight in stored_insights
        ]
    }

@router.get("/dashboard")
async def get_dashboard_metrics(
    days: int = Query(7, description="Number of days for metrics"),
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard metrics for system overview"""
    start_date = datetime.now() - timedelta(days=days)
    
    # Overall statistics
    stats_result = await db.execute(
        select(func.count(QuizAttempt.id).label('total_attempts'),
               func.avg(QuizAttempt.score / QuizAttempt.max_score).label('avg_score'),
               func.count(func.distinct(QuizAttempt.user_id)).label('active_users'))
        .where(QuizAttempt.completed_at >= start_date)
    )
    stats = stats_result.first()
    
    # Daily attempt counts
    daily_attempts = await db.execute(
        select(func.date(QuizAttempt.completed_at).label('date'),
               func.count(QuizAttempt.id).label('attempts'))
        .where(QuizAttempt.completed_at >= start_date)
        .group_by(func.date(QuizAttempt.completed_at))
        .order_by(func.date(QuizAttempt.completed_at))
    )
    
    # Topic performance
    topic_performance = await db.execute(
        select(QuizAttempt.topic_id,
               func.count(QuizAttempt.id).label('attempts'),
               func.avg(QuizAttempt.score / QuizAttempt.max_score).label('avg_score'))
        .where(QuizAttempt.completed_at >= start_date)
        .group_by(QuizAttempt.topic_id)
        .order_by(func.avg(QuizAttempt.score / QuizAttempt.max_score).desc())
    )
    
    return {
        "period_days": days,
        "overview": {
            "total_attempts": stats.total_attempts or 0,
            "average_score_percentage": float(stats.avg_score * 100) if stats.avg_score else 0,
            "active_users": stats.active_users or 0
        },
        "daily_activity": [
            {"date": str(date), "attempts": attempts}
            for date, attempts in daily_attempts.fetchall()
        ],
        "topic_performance": [
            {
                "topic_id": topic,
                "attempts": attempts,
                "average_score_percentage": float(avg_score * 100)
            }
            for topic, attempts, avg_score in topic_performance.fetchall()
        ]
    }

@router.get("/topics/{topic_id}/analytics")
async def get_topic_analytics(
    topic_id: str,
    days: int = Query(30, description="Number of days to analyze"),
    db: AsyncSession = Depends(get_db)
):
    """Get detailed analytics for a specific topic"""
    start_date = datetime.now() - timedelta(days=days)
    
    try:
        # First, let's check if there are any attempts at all for this topic
        basic_check = await db.execute(
            select(QuizAttempt.id, QuizAttempt.user_id, QuizAttempt.score, QuizAttempt.max_score)
            .where(QuizAttempt.topic_id == topic_id)
            .limit(5)
        )
        basic_results = basic_check.fetchall()
        
        # Topic statistics
        stats_result = await db.execute(
            select(func.count(QuizAttempt.id).label('total_attempts'),
                   func.avg(QuizAttempt.score / QuizAttempt.max_score).label('avg_score'),
                   func.avg(QuizAttempt.time_spent).label('avg_time'),
                   func.count(func.distinct(QuizAttempt.user_id)).label('unique_learners'))
            .where(QuizAttempt.topic_id == topic_id)
        )
        stats = stats_result.first()
        
        # Performance distribution - using a simpler approach
        score_distribution_result = await db.execute(
            select(QuizAttempt.score, QuizAttempt.max_score)
            .where(QuizAttempt.topic_id == topic_id)
        )
        score_data = score_distribution_result.fetchall()
        
        # Calculate distribution manually
        distribution = {}
        for score, max_score in score_data:
            if max_score > 0:
                percentage = (score / max_score) * 100
                bucket = int(percentage // 10) * 10
                bucket_key = f"{bucket}-{bucket+9}%"
                distribution[bucket_key] = distribution.get(bucket_key, 0) + 1
        
        score_distribution = [{"score_range": k, "count": v} for k, v in sorted(distribution.items())]
        
        return {
            "topic_id": topic_id,
            "period_days": days,
            "debug_basic_results": len(basic_results),
            "statistics": {
                "total_attempts": stats.total_attempts or 0,
                "average_score_percentage": float(stats.avg_score * 100) if stats.avg_score else 0,
                "average_time_minutes": float(stats.avg_time / 60) if stats.avg_time else 0,
                "unique_learners": stats.unique_learners or 0
            },
            "score_distribution": score_distribution
        }
    except Exception as e:
        # Return empty data if there's an error
        return {
            "topic_id": topic_id,
            "period_days": days,
            "error": str(e),
            "statistics": {
                "total_attempts": 0,
                "average_score_percentage": 0,
                "average_time_minutes": 0,
                "unique_learners": 0
            },
            "score_distribution": []
        }

@router.post("/process-events")
async def process_analytics_events(db: AsyncSession = Depends(get_db)):
    """Manually trigger processing of analytics events"""
    try:
        processor = AnalyticsProcessor()
        await processor.process_events()
        return {"message": "Events processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing events: {str(e)}")

@router.post("/create-demo-data")
async def create_demo_data(db: AsyncSession = Depends(get_db)):
    """Create demo quiz attempt data for testing"""
    try:
        # Create multiple demo quiz attempts for mathematics topic
        demo_attempts = [
            QuizAttempt(
                user_id="demo-user-1",
                quiz_id="quiz-1",
                topic_id="mathematics",
                score=85,
                max_score=100,
                time_spent=300,
                completed_at=datetime.now() - timedelta(hours=2),
                answers={"q1": "A", "q2": "B", "q3": "C"},
                metadata_json={"difficulty": "medium"}
            ),
            QuizAttempt(
                user_id="demo-user-2",
                quiz_id="quiz-2",
                topic_id="mathematics",
                score=92,
                max_score=100,
                time_spent=240,
                completed_at=datetime.now() - timedelta(hours=1),
                answers={"q1": "A", "q2": "A", "q3": "B"},
                metadata_json={"difficulty": "easy"}
            ),
            QuizAttempt(
                user_id="demo-user-3",
                quiz_id="quiz-3",
                topic_id="mathematics",
                score=78,
                max_score=100,
                time_spent=420,
                completed_at=datetime.now() - timedelta(minutes=30),
                answers={"q1": "B", "q2": "C", "q3": "A"},
                metadata_json={"difficulty": "hard"}
            ),
            QuizAttempt(
                user_id="demo-user-1",
                quiz_id="quiz-4",
                topic_id="mathematics",
                score=95,
                max_score=100,
                time_spent=180,
                completed_at=datetime.now() - timedelta(minutes=15),
                answers={"q1": "A", "q2": "A", "q3": "A"},
                metadata_json={"difficulty": "medium"}
            ),
            QuizAttempt(
                user_id="demo-user-2",
                quiz_id="quiz-5",
                topic_id="mathematics",
                score=88,
                max_score=100,
                time_spent=360,
                completed_at=datetime.now() - timedelta(minutes=5),
                answers={"q1": "A", "q2": "B", "q3": "A"},
                metadata_json={"difficulty": "easy"}
            )
        ]
        
        for attempt in demo_attempts:
            db.add(attempt)
        
        await db.commit()
        return {"message": f"Created {len(demo_attempts)} demo quiz attempts"}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creating demo data: {str(e)}")

@router.get("/debug/data")
async def debug_data(db: AsyncSession = Depends(get_db)):
    """Debug endpoint to check current data in database"""
    try:
        # Check QuizAttempt records
        attempts_result = await db.execute(select(QuizAttempt))
        attempts = attempts_result.scalars().all()
        
        # Check AnalyticsEvent records
        events_result = await db.execute(select(AnalyticsEvent))
        events = events_result.scalars().all()
        
        return {
            "quiz_attempts_count": len(attempts),
            "analytics_events_count": len(events),
            "quiz_attempts": [
                {
                    "id": attempt.id,
                    "user_id": attempt.user_id,
                    "topic_id": attempt.topic_id,
                    "score": attempt.score,
                    "max_score": attempt.max_score,
                    "completed_at": attempt.completed_at.isoformat()
                }
                for attempt in attempts[:5]  # Show first 5
            ],
            "analytics_events": [
                {
                    "id": event.id,
                    "event_type": event.event_type,
                    "user_id": event.user_id,
                    "topic_id": event.topic_id,
                    "processed": event.processed,
                    "timestamp": event.timestamp.isoformat()
                }
                for event in events[:5]  # Show first 5
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking data: {str(e)}")
