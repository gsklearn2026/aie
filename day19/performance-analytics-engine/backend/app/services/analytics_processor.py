import asyncio
import json
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, List, Any
import redis.asyncio as redis
import pandas as pd
import numpy as np

from ..database import async_session
from ..models import QuizAttempt, AnalyticsEvent, PerformanceMetric
from ..utils.websocket_manager import WebSocketManager

class AnalyticsProcessor:
    def __init__(self):
        self.redis_client = redis.from_url("redis://localhost:6379/0")
        self.websocket_manager = WebSocketManager()

    async def process_events(self):
        """Process unprocessed analytics events"""
        async with async_session() as session:
            # Get unprocessed events
            result = await session.execute(
                select(AnalyticsEvent).where(AnalyticsEvent.processed == False)
            )
            events = result.scalars().all()
            
            if events:
                await self._process_quiz_completion_events(session, events)
                await self._calculate_performance_metrics(session)
                await self._update_real_time_dashboards(session)
                
                # Mark events as processed
                for event in events:
                    event.processed = True
                await session.commit()

    async def _process_quiz_completion_events(self, session: AsyncSession, events: List[AnalyticsEvent]):
        """Process quiz completion events into structured analytics"""
        for event in events:
            if event.event_type == "quiz_completed":
                # Create QuizAttempt record from AnalyticsEvent
                quiz_attempt = QuizAttempt(
                    user_id=event.user_id,
                    quiz_id=event.quiz_id,
                    topic_id=event.topic_id,
                    score=event.data.get("score", 0),
                    max_score=event.data.get("max_score", 100),
                    time_spent=event.data.get("time_spent", 0),
                    completed_at=event.timestamp,
                    answers=event.data.get("answers", {}),
                    metadata_json=event.data
                )
                session.add(quiz_attempt)
                
                await self._aggregate_user_performance(session, event)
                await self._update_topic_analytics(session, event)

    async def _aggregate_user_performance(self, session: AsyncSession, event: AnalyticsEvent):
        """Aggregate user performance metrics"""
        # Calculate mastery level
        recent_attempts = await session.execute(
            select(QuizAttempt)
            .where(QuizAttempt.user_id == event.user_id)
            .where(QuizAttempt.topic_id == event.topic_id)
            .where(QuizAttempt.completed_at >= datetime.now() - timedelta(days=7))
            .order_by(QuizAttempt.completed_at.desc())
            .limit(5)
        )
        attempts = recent_attempts.scalars().all()
        
        if attempts:
            scores = [attempt.score / attempt.max_score for attempt in attempts]
            mastery_level = np.mean(scores) * 100
            
            # Store metric
            metric = PerformanceMetric(
                user_id=event.user_id,
                topic_id=event.topic_id,
                metric_type="mastery_level",
                value=mastery_level,
                aggregation_window="weekly",
                metadata={"sample_size": len(attempts), "trend": self._calculate_trend(scores)}
            )
            session.add(metric)

    async def _update_topic_analytics(self, session: AsyncSession, event: AnalyticsEvent):
        """Update topic-level analytics"""
        # Cache topic performance in Redis for fast access
        key = f"topic_analytics:{event.topic_id}"
        
        # Get topic performance data
        result = await session.execute(
            select(func.avg(QuizAttempt.score / QuizAttempt.max_score).label('avg_score'),
                   func.count(QuizAttempt.id).label('attempt_count'))
            .where(QuizAttempt.topic_id == event.topic_id)
            .where(QuizAttempt.completed_at >= datetime.now() - timedelta(days=1))
        )
        stats = result.first()
        
        analytics_data = {
            "average_score": float(stats.avg_score) if stats.avg_score else 0,
            "total_attempts": stats.attempt_count,
            "updated_at": datetime.now().isoformat()
        }
        
        await self.redis_client.setex(key, 3600, json.dumps(analytics_data))

    async def _calculate_performance_metrics(self, session: AsyncSession):
        """Calculate advanced performance metrics"""
        # Learning velocity calculation
        await self._calculate_learning_velocity(session)
        
        # Knowledge gap identification
        await self._identify_knowledge_gaps(session)

    async def _calculate_learning_velocity(self, session: AsyncSession):
        """Calculate how quickly users are improving"""
        # Get users with multiple attempts
        result = await session.execute(
            select(QuizAttempt.user_id, QuizAttempt.topic_id)
            .group_by(QuizAttempt.user_id, QuizAttempt.topic_id)
            .having(func.count(QuizAttempt.id) >= 3)
        )
        
        for user_id, topic_id in result:
            # Get attempts for this user/topic
            attempts_result = await session.execute(
                select(QuizAttempt)
                .where(QuizAttempt.user_id == user_id)
                .where(QuizAttempt.topic_id == topic_id)
                .order_by(QuizAttempt.completed_at)
            )
            attempts = attempts_result.scalars().all()
            
            if len(attempts) >= 3:
                scores = [attempt.score / attempt.max_score for attempt in attempts]
                velocity = self._calculate_improvement_rate(scores)
                
                metric = PerformanceMetric(
                    user_id=user_id,
                    topic_id=topic_id,
                    metric_type="learning_velocity",
                    value=velocity,
                    aggregation_window="daily",
                    metadata={"attempts_analyzed": len(attempts)}
                )
                session.add(metric)

    def _calculate_improvement_rate(self, scores: List[float]) -> float:
        """Calculate rate of improvement using linear regression"""
        if len(scores) < 2:
            return 0.0
        
        x = np.arange(len(scores))
        slope, _ = np.polyfit(x, scores, 1)
        return float(slope * 100)  # Convert to percentage improvement per attempt

    def _calculate_trend(self, scores: List[float]) -> str:
        """Calculate trend direction"""
        if len(scores) < 2:
            return "insufficient_data"
        
        slope = self._calculate_improvement_rate(scores)
        if slope > 5:
            return "improving"
        elif slope < -5:
            return "declining"
        else:
            return "stable"

    async def _identify_knowledge_gaps(self, session: AsyncSession):
        """Identify topics where users consistently struggle"""
        result = await session.execute(
            select(QuizAttempt.topic_id,
                   func.avg(QuizAttempt.score / QuizAttempt.max_score).label('avg_score'),
                   func.count(QuizAttempt.id).label('attempt_count'))
            .where(QuizAttempt.completed_at >= datetime.now() - timedelta(days=7))
            .group_by(QuizAttempt.topic_id)
            .having(func.count(QuizAttempt.id) >= 10)
        )
        
        for topic_id, avg_score, attempt_count in result:
            if avg_score < 0.6:  # Less than 60% average
                # Store as performance metric
                metric = PerformanceMetric(
                    user_id="system",
                    topic_id=topic_id,
                    metric_type="knowledge_gap",
                    value=float(avg_score),
                    aggregation_window="weekly",
                    metadata={"severity": "high" if avg_score < 0.4 else "medium"}
                )
                session.add(metric)

    async def _update_real_time_dashboards(self, session: AsyncSession):
        """Update real-time dashboard data"""
        # Calculate current metrics
        today = datetime.now().date()
        result = await session.execute(
            select(func.count(QuizAttempt.id).label('total_attempts'),
                   func.avg(QuizAttempt.score / QuizAttempt.max_score).label('avg_score'))
            .where(func.date(QuizAttempt.completed_at) == today)
        )
        stats = result.first()
        
        dashboard_data = {
            "total_attempts_today": stats.total_attempts,
            "average_score_today": float(stats.avg_score) if stats.avg_score else 0,
            "timestamp": datetime.now().isoformat()
        }
        
        # Broadcast to connected WebSocket clients
        await self.websocket_manager.broadcast(json.dumps({
            "type": "dashboard_update",
            "data": dashboard_data
        }))
