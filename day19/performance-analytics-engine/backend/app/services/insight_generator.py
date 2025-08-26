import google.generativeai as genai
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from ..models import QuizAttempt, PerformanceMetric, LearningInsight
from ..database import async_session

class InsightGenerator:
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')

    async def generate_user_insights(self, user_id: str) -> List[Dict[str, Any]]:
        """Generate personalized learning insights for a user"""
        async with async_session() as session:
            # Get user's recent performance data
            performance_data = await self._get_user_performance_data(session, user_id)
            
            if not performance_data:
                return []

            # Generate insights using Gemini AI
            insights = await self._analyze_performance_with_ai(performance_data)
            
            # Store insights in database
            await self._store_insights(session, user_id, insights)
            
            return insights

    async def _get_user_performance_data(self, session: AsyncSession, user_id: str) -> Dict[str, Any]:
        """Retrieve comprehensive performance data for analysis"""
        # Recent quiz attempts
        attempts_result = await session.execute(
            select(QuizAttempt)
            .where(QuizAttempt.user_id == user_id)
            .where(QuizAttempt.completed_at >= datetime.now() - timedelta(days=30))
            .order_by(QuizAttempt.completed_at.desc())
        )
        attempts = attempts_result.scalars().all()

        # Performance metrics
        metrics_result = await session.execute(
            select(PerformanceMetric)
            .where(PerformanceMetric.user_id == user_id)
            .where(PerformanceMetric.calculated_at >= datetime.now() - timedelta(days=7))
        )
        metrics = metrics_result.scalars().all()

        # Topic performance summary
        topic_stats = {}
        for attempt in attempts:
            if attempt.topic_id not in topic_stats:
                topic_stats[attempt.topic_id] = {
                    "attempts": 0,
                    "total_score": 0,
                    "max_possible": 0,
                    "time_spent": 0
                }
            
            stats = topic_stats[attempt.topic_id]
            stats["attempts"] += 1
            stats["total_score"] += attempt.score
            stats["max_possible"] += attempt.max_score
            stats["time_spent"] += attempt.time_spent

        # Calculate averages
        for topic_id, stats in topic_stats.items():
            stats["avg_score_percentage"] = (stats["total_score"] / stats["max_possible"]) * 100
            stats["avg_time_per_attempt"] = stats["time_spent"] / stats["attempts"]

        return {
            "user_id": user_id,
            "total_attempts": len(attempts),
            "topics_attempted": len(topic_stats),
            "topic_performance": topic_stats,
            "recent_metrics": [
                {
                    "type": metric.metric_type,
                    "value": metric.value,
                    "topic": metric.topic_id,
                    "metadata": metric.metadata_json or {}
                }
                for metric in metrics
            ]
        }

    async def _analyze_performance_with_ai(self, performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Use Gemini AI to analyze performance and generate insights"""
        
        prompt = f"""
        Analyze this student's learning performance data and provide actionable insights:

        Performance Summary:
        - Total quiz attempts: {performance_data['total_attempts']}
        - Topics attempted: {performance_data['topics_attempted']}
        
        Topic Performance:
        {json.dumps(performance_data['topic_performance'], indent=2)}
        
        Recent Metrics:
        {json.dumps(performance_data['recent_metrics'], indent=2)}

        Please provide insights in JSON format with the following structure:
        {{
            "insights": [
                {{
                    "type": "strength|weakness|recommendation|trend",
                    "title": "Brief insight title",
                    "description": "Detailed explanation",
                    "confidence": 0.85,
                    "action_items": ["specific action 1", "specific action 2"],
                    "topics_involved": ["topic1", "topic2"]
                }}
            ]
        }}

        Focus on:
        1. Learning strengths and weaknesses
        2. Study pattern recommendations
        3. Topics that need more attention
        4. Positive trends to encourage
        5. Specific, actionable next steps
        """

        try:
            response = self.model.generate_content(prompt)
            insights_data = json.loads(response.text)
            return insights_data.get("insights", [])
        except Exception as e:
            # Fallback to rule-based insights if AI fails
            return await self._generate_fallback_insights(performance_data)

    async def _generate_fallback_insights(self, performance_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate basic insights using rule-based logic"""
        insights = []
        
        # Identify strongest topic
        best_topic = None
        best_score = 0
        for topic_id, stats in performance_data['topic_performance'].items():
            if stats['avg_score_percentage'] > best_score:
                best_score = stats['avg_score_percentage']
                best_topic = topic_id

        if best_topic and best_score > 80:
            insights.append({
                "type": "strength",
                "title": f"Excelling in {best_topic}",
                "description": f"You're performing very well in {best_topic} with an average score of {best_score:.1f}%",
                "confidence": 0.9,
                "action_items": ["Continue practicing to maintain mastery", "Consider helping others with this topic"],
                "topics_involved": [best_topic]
            })

        # Identify weakest topic
        worst_topic = None
        worst_score = 100
        for topic_id, stats in performance_data['topic_performance'].items():
            if stats['avg_score_percentage'] < worst_score:
                worst_score = stats['avg_score_percentage']
                worst_topic = topic_id

        if worst_topic and worst_score < 60:
            insights.append({
                "type": "weakness",
                "title": f"Need more practice with {worst_topic}",
                "description": f"Your average score in {worst_topic} is {worst_score:.1f}%, which indicates room for improvement",
                "confidence": 0.85,
                "action_items": ["Review fundamental concepts", "Take more practice quizzes", "Seek additional resources"],
                "topics_involved": [worst_topic]
            })

        return insights

    async def _store_insights(self, session: AsyncSession, user_id: str, insights: List[Dict[str, Any]]):
        """Store generated insights in the database"""
        for insight_data in insights:
            insight = LearningInsight(
                user_id=user_id,
                insight_type=insight_data.get("type", "general"),
                title=insight_data.get("title", ""),
                description=insight_data.get("description", ""),
                confidence_score=insight_data.get("confidence", 0.5),
                action_items=insight_data.get("action_items", []),
                metadata={
                    "topics_involved": insight_data.get("topics_involved", []),
                    "generated_by": "gemini_ai"
                }
            )
            session.add(insight)
        
        await session.commit()

    async def generate_system_insights(self) -> Dict[str, Any]:
        """Generate system-wide insights for administrators"""
        async with async_session() as session:
            # Get system performance metrics
            today = datetime.now().date()
            week_ago = datetime.now() - timedelta(days=7)
            
            # Overall statistics
            stats_result = await session.execute(
                select(func.count(QuizAttempt.id).label('total_attempts'),
                       func.avg(QuizAttempt.score / QuizAttempt.max_score).label('avg_score'),
                       func.count(func.distinct(QuizAttempt.user_id)).label('active_users'))
                .where(QuizAttempt.completed_at >= week_ago)
            )
            stats = stats_result.first()
            
            # Topic difficulty analysis
            topic_difficulty = await session.execute(
                select(QuizAttempt.topic_id,
                       func.avg(QuizAttempt.score / QuizAttempt.max_score).label('avg_score'))
                .where(QuizAttempt.completed_at >= week_ago)
                .group_by(QuizAttempt.topic_id)
                .order_by(func.avg(QuizAttempt.score / QuizAttempt.max_score))
            )
            
            return {
                "system_performance": {
                    "total_attempts": stats.total_attempts,
                    "average_score": float(stats.avg_score) if stats.avg_score else 0,
                    "active_users": stats.active_users
                },
                "difficult_topics": [
                    {"topic": topic, "avg_score": float(score)}
                    for topic, score in topic_difficulty.fetchall()
                    if score < 0.6
                ]
            }
