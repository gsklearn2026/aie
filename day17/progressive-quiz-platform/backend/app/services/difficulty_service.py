import asyncio
import json
import numpy as np
from collections import deque
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
import redis.asyncio as redis
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc

from ..models.difficulty import Question, UserPerformance, UserResponse, DifficultySession

class PerformanceWindow:
    def __init__(self, window_size: int = 10):
        self.window_size = window_size
        self.responses = deque(maxlen=window_size)
        self.time_weights = [1.2, 1.1, 1.05, 1.0, 0.95, 0.9, 0.85, 0.8, 0.75, 0.7][:window_size]
    
    def add_response(self, is_correct: bool, response_time_ms: int, difficulty: float):
        self.responses.append({
            'correct': is_correct,
            'time_ms': response_time_ms,
            'difficulty': difficulty,
            'timestamp': datetime.utcnow()
        })
    
    def calculate_success_rate(self) -> float:
        if not self.responses:
            return 0.7  # Default neutral success rate
        
        weighted_scores = []
        for i, response in enumerate(self.responses):
            weight = self.time_weights[i] if i < len(self.time_weights) else 0.7
            score = 1.0 if response['correct'] else 0.0
            weighted_scores.append(score * weight)
        
        return sum(weighted_scores) / sum(self.time_weights[:len(self.responses)])
    
    def calculate_momentum(self) -> float:
        if len(self.responses) < 3:
            return 0.0
        
        recent_half = list(self.responses)[len(self.responses)//2:]
        early_half = list(self.responses)[:len(self.responses)//2]
        
        recent_rate = sum(1 for r in recent_half if r['correct']) / len(recent_half)
        early_rate = sum(1 for r in early_half if r['correct']) / len(early_half)
        
        return recent_rate - early_rate

class ProgressiveDifficultyService:
    def __init__(self, db: Session, redis_client: redis.Redis):
        self.db = db
        self.redis = redis_client
        self.default_difficulty = 1.0
        self.target_success_rate = 0.7
        self.adjustment_factor = 0.3
        self.momentum_factor = 0.2
        self.max_difficulty_change = 0.5
        
    async def get_user_performance_window(self, user_id: str, session_id: str) -> PerformanceWindow:
        """Retrieve or create performance window for user session"""
        cache_key = f"performance_window:{user_id}:{session_id}"
        
        # Try to get from Redis cache
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            data = json.loads(cached_data)
            window = PerformanceWindow(data.get('window_size', 10))
            for response in data.get('responses', []):
                window.responses.append(response)
            return window
        
        # Load from database
        window = PerformanceWindow()
        recent_responses = self.db.query(UserResponse).filter(
            and_(
                UserResponse.user_id == user_id,
                UserResponse.session_id == session_id
            )
        ).order_by(desc(UserResponse.timestamp)).limit(window.window_size).all()
        
        for response in reversed(recent_responses):
            window.add_response(
                response.is_correct,
                response.response_time_ms,
                response.difficulty_at_time
            )
        
        await self._cache_performance_window(cache_key, window)
        return window
    
    async def _cache_performance_window(self, cache_key: str, window: PerformanceWindow):
        """Cache performance window to Redis"""
        data = {
            'window_size': window.window_size,
            'responses': [
                {
                    'correct': r['correct'],
                    'time_ms': r['time_ms'],
                    'difficulty': r['difficulty'],
                    'timestamp': r['timestamp'].isoformat() if hasattr(r['timestamp'], 'isoformat') else str(r['timestamp'])
                } for r in window.responses
            ]
        }
        await self.redis.setex(cache_key, 300, json.dumps(data, default=str))  # 5 min TTL
    
    def calculate_next_difficulty(self, current_difficulty: float, success_rate: float, momentum: float) -> float:
        """Calculate optimal next difficulty level"""
        # Base adjustment targeting success rate
        success_deviation = success_rate - self.target_success_rate
        base_adjustment = success_deviation * self.adjustment_factor
        
        # Momentum-based adjustment for smooth transitions
        momentum_adjustment = momentum * self.momentum_factor
        
        # Calculate new difficulty
        new_difficulty = current_difficulty + base_adjustment + momentum_adjustment
        
        # Apply bounds and limits
        new_difficulty = max(0.1, min(5.0, new_difficulty))  # Keep in reasonable range
        
        # Prevent dramatic changes
        max_change = min(self.max_difficulty_change, abs(new_difficulty - current_difficulty))
        if new_difficulty > current_difficulty:
            new_difficulty = current_difficulty + max_change
        else:
            new_difficulty = current_difficulty - max_change
            
        return round(new_difficulty, 2)
    
    async def select_next_question(self, user_id: str, session_id: str, target_difficulty: float) -> Optional[Question]:
        """Select next question based on target difficulty and user history"""
        # Calculate difficulty range
        difficulty_range = 0.5
        min_difficulty = max(0.1, target_difficulty - difficulty_range)
        max_difficulty = min(10.0, target_difficulty + difficulty_range)
        
        # Get recent question IDs to avoid repetition
        recent_question_ids = self.db.query(UserResponse.question_id).filter(
            and_(
                UserResponse.user_id == user_id,
                UserResponse.timestamp > datetime.utcnow() - timedelta(hours=1)
            )
        ).subquery()
        
        # Query suitable questions
        question = self.db.query(Question).filter(
            and_(
                Question.difficulty_score >= min_difficulty,
                Question.difficulty_score <= max_difficulty,
                ~Question.id.in_(self.db.query(recent_question_ids.c.question_id))
            )
        ).order_by(
            func.abs(Question.difficulty_score - target_difficulty),
            func.random()
        ).first()
        
        return question
    
    async def record_response(self, user_id: str, session_id: str, question_id: int, 
                            user_answer: str, is_correct: bool, response_time_ms: int, 
                            difficulty_at_time: float):
        """Record user response and update performance metrics"""
        # Store response
        response = UserResponse(
            user_id=user_id,
            session_id=session_id,
            question_id=question_id,
            user_answer=user_answer,
            is_correct=is_correct,
            response_time_ms=response_time_ms,
            difficulty_at_time=difficulty_at_time
        )
        self.db.add(response)
        
        # Update performance window cache
        cache_key = f"performance_window:{user_id}:{session_id}"
        window = await self.get_user_performance_window(user_id, session_id)
        window.add_response(is_correct, response_time_ms, difficulty_at_time)
        await self._cache_performance_window(cache_key, window)
        
        # Update session performance
        await self._update_session_performance(user_id, session_id, window)
        
        self.db.commit()
    
    async def _update_session_performance(self, user_id: str, session_id: str, window: PerformanceWindow):
        """Update aggregated session performance metrics"""
        session = self.db.query(DifficultySession).filter(
            DifficultySession.session_id == session_id
        ).first()
        
        if not session:
            session = DifficultySession(
                session_id=session_id,
                user_id=user_id,
                current_difficulty=self.default_difficulty
            )
            self.db.add(session)
        
        # Calculate new difficulty
        success_rate = window.calculate_success_rate()
        momentum = window.calculate_momentum()
        new_difficulty = self.calculate_next_difficulty(
            session.current_difficulty, success_rate, momentum
        )
        
        session.current_difficulty = new_difficulty
        session.last_activity = datetime.utcnow()
    
    async def get_next_question_for_user(self, user_id: str, session_id: str, 
                                       last_response: Optional[Dict] = None) -> Tuple[Optional[Question], float]:
        """Main method to get next question with optimal difficulty"""
        # Record last response if provided
        if last_response:
            await self.record_response(
                user_id=user_id,
                session_id=session_id,
                question_id=last_response['question_id'],
                user_answer=last_response['user_answer'],
                is_correct=last_response['is_correct'],
                response_time_ms=last_response['response_time_ms'],
                difficulty_at_time=last_response['difficulty_at_time']
            )
        
        # Get current performance window
        window = await self.get_user_performance_window(user_id, session_id)
        
        # Calculate target difficulty
        success_rate = window.calculate_success_rate()
        momentum = window.calculate_momentum()
        
        # Get current session difficulty
        session = self.db.query(DifficultySession).filter(
            DifficultySession.session_id == session_id
        ).first()
        
        current_difficulty = session.current_difficulty if session else self.default_difficulty
        target_difficulty = self.calculate_next_difficulty(current_difficulty, success_rate, momentum)
        
        # Select next question
        question = await self.select_next_question(user_id, session_id, target_difficulty)
        
        return question, target_difficulty
    
    async def get_performance_analytics(self, user_id: str, session_id: str) -> Dict:
        """Get detailed performance analytics for user session"""
        window = await self.get_user_performance_window(user_id, session_id)
        session = self.db.query(DifficultySession).filter(
            DifficultySession.session_id == session_id
        ).first()
        
        return {
            'current_difficulty': session.current_difficulty if session else self.default_difficulty,
            'success_rate': window.calculate_success_rate(),
            'momentum': window.calculate_momentum(),
            'question_count': len(window.responses),
            'avg_response_time': np.mean([r['time_ms'] for r in window.responses]) if window.responses else 0,
            'recent_performance': [r['correct'] for r in window.responses]
        }
