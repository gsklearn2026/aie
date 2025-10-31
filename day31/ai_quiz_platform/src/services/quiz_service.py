"""Core quiz service containing business logic."""

import logging
from typing import Any, Dict, List, Optional

from src.models import (
    DifficultyLevel,
    Question,
    Quiz,
    QuizGenerationRequest,
    UserPerformance,
)
from src.services.ai_service import AIServiceError, ai_service

logger = logging.getLogger(__name__)


class QuizServiceError(Exception):
    """Custom exception for quiz service errors."""

    pass


class QuizService:
    """Service for quiz management and business logic."""

    def __init__(self):
        """Initialize quiz service."""
        self._quiz_store: Dict[str, Quiz] = {}
        self._performance_store: Dict[str, List[UserPerformance]] = {}
        self._question_bank: Dict[str, List[Question]] = {}

    async def create_quiz(self, request: QuizGenerationRequest) -> Quiz:
        """Create a new quiz using AI generation."""
        try:
            # Validate request
            self._validate_quiz_request(request)

            # Generate quiz using AI service
            quiz = await ai_service.generate_quiz(request)

            # Assign unique ID
            quiz.id = self._generate_quiz_id()

            # Store quiz
            self._quiz_store[quiz.id] = quiz

            # Update question bank
            self._update_question_bank(quiz.questions)

            logger.info(f"Created quiz: {quiz.id} - {quiz.title}")
            return quiz

        except AIServiceError as e:
            logger.error(f"AI service error in quiz creation: {str(e)}")
            raise QuizServiceError(f"Failed to create quiz: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in quiz creation: {str(e)}")
            raise QuizServiceError(f"Quiz creation failed: {str(e)}")

    def get_quiz(self, quiz_id: str) -> Optional[Quiz]:
        """Retrieve a quiz by ID."""
        return self._quiz_store.get(quiz_id)

    def list_quizzes(self, difficulty: Optional[DifficultyLevel] = None) -> List[Quiz]:
        """List all quizzes, optionally filtered by difficulty."""
        quizzes = list(self._quiz_store.values())

        if difficulty:
            quizzes = [q for q in quizzes if q.difficulty == difficulty]

        # Sort by creation date (newest first)
        return sorted(quizzes, key=lambda q: q.created_at, reverse=True)

    def calculate_adaptive_difficulty(self, user_id: str) -> DifficultyLevel:
        """Calculate appropriate difficulty level based on user performance."""
        performances = self._performance_store.get(user_id, [])

        if not performances:
            return DifficultyLevel.BEGINNER

        # Get recent performance (last 10 attempts)
        recent_performances = sorted(performances, key=lambda p: p.timestamp, reverse=True)[:10]

        if not recent_performances:
            return DifficultyLevel.BEGINNER

        # Calculate average performance
        avg_percentage = sum(p.percentage_score for p in recent_performances) / len(
            recent_performances
        )

        # Determine difficulty based on performance
        if avg_percentage >= 85:
            return DifficultyLevel.EXPERT
        elif avg_percentage >= 75:
            return DifficultyLevel.ADVANCED
        elif avg_percentage >= 60:
            return DifficultyLevel.INTERMEDIATE
        else:
            return DifficultyLevel.BEGINNER

    def record_performance(self, performance: UserPerformance) -> None:
        """Record user performance data."""
        if performance.user_id not in self._performance_store:
            self._performance_store[performance.user_id] = []

        self._performance_store[performance.user_id].append(performance)

        # Keep only last 50 performances per user
        if len(self._performance_store[performance.user_id]) > 50:
            self._performance_store[performance.user_id] = self._performance_store[
                performance.user_id
            ][-50:]

        logger.info(
            f"Recorded performance for user {performance.user_id}: "
            f"{performance.percentage_score:.1f}%"
        )

    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user statistics."""
        performances = self._performance_store.get(user_id, [])

        if not performances:
            return {
                "total_attempts": 0,
                "average_score": 0,
                "best_score": 0,
                "current_streak": 0,
                "recommended_difficulty": DifficultyLevel.BEGINNER.value,
            }

        # Calculate statistics
        total_attempts = len(performances)
        avg_score = sum(p.percentage_score for p in performances) / total_attempts
        best_score = max(p.percentage_score for p in performances)

        # Calculate current streak (consecutive scores >= 70%)
        current_streak = 0
        for performance in reversed(performances):
            if performance.percentage_score >= 70:
                current_streak += 1
            else:
                break

        return {
            "total_attempts": total_attempts,
            "average_score": round(avg_score, 1),
            "best_score": round(best_score, 1),
            "current_streak": current_streak,
            "recommended_difficulty": self.calculate_adaptive_difficulty(user_id).value,
            "performance_trend": self._calculate_performance_trend(performances),
        }

    def validate_quiz_answers(self, quiz: Quiz, user_answers: Dict[str, str]) -> Dict[str, Any]:
        """Validate user answers against quiz questions."""
        if not quiz or not quiz.questions:
            raise QuizServiceError("Invalid quiz data")

        results = {
            "total_questions": len(quiz.questions),
            "correct_answers": 0,
            "total_points": 0,
            "max_points": quiz.total_points,
            "question_results": [],
        }

        for question in quiz.questions:
            user_answer = user_answers.get(question.id, "").strip().lower()
            correct_answer = question.correct_answer.strip().lower()
            is_correct = user_answer == correct_answer

            if is_correct:
                results["correct_answers"] += 1
                results["total_points"] += question.points

            results["question_results"].append(
                {
                    "question_id": question.id,
                    "user_answer": user_answers.get(question.id, ""),
                    "correct_answer": question.correct_answer,
                    "is_correct": is_correct,
                    "points_earned": question.points if is_correct else 0,
                    "explanation": question.explanation,
                }
            )

        results["percentage_score"] = (results["total_points"] / results["max_points"]) * 100
        return results

    def _validate_quiz_request(self, request: QuizGenerationRequest) -> None:
        """Validate quiz generation request."""
        if not request.topic or len(request.topic.strip()) < 2:
            raise QuizServiceError("Topic must be at least 2 characters long")

        if request.question_count < 1 or request.question_count > 20:
            raise QuizServiceError("Question count must be between 1 and 20")

        if request.time_limit and (request.time_limit < 60 or request.time_limit > 7200):
            raise QuizServiceError("Time limit must be between 60 and 7200 seconds")

    def _generate_quiz_id(self) -> str:
        """Generate unique quiz ID."""
        import uuid

        return str(uuid.uuid4())

    def _update_question_bank(self, questions: List[Question]) -> None:
        """Update question bank with new questions."""
        for question in questions:
            topic_key = "_".join(question.tags) if question.tags else "general"
            if topic_key not in self._question_bank:
                self._question_bank[topic_key] = []
            self._question_bank[topic_key].append(question)

    def _calculate_performance_trend(self, performances: List[UserPerformance]) -> str:
        """Calculate performance trend (improving, declining, stable)."""
        if len(performances) < 3:
            return "insufficient_data"

        recent_scores = [p.percentage_score for p in performances[-5:]]
        older_scores = (
            [p.percentage_score for p in performances[-10:-5]] if len(performances) >= 10 else []
        )

        if not older_scores:
            return "insufficient_data"

        recent_avg = sum(recent_scores) / len(recent_scores)
        older_avg = sum(older_scores) / len(older_scores)

        difference = recent_avg - older_avg

        if difference > 5:
            return "improving"
        elif difference < -5:
            return "declining"
        else:
            return "stable"


# Service instance
quiz_service = QuizService()
