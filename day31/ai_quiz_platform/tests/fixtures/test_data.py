"""Test fixtures and sample data for unit tests."""

from datetime import datetime, timedelta
from typing import List

from src.models import (
    DifficultyLevel,
    Question,
    QuestionType,
    Quiz,
    QuizGenerationRequest,
    UserPerformance,
)


class TestDataFactory:
    """Factory for creating test data objects."""

    @staticmethod
    def create_question(
        question_id: str = "test_q1",
        text: str = "What is Python?",
        question_type: QuestionType = QuestionType.MULTIPLE_CHOICE,
        difficulty: DifficultyLevel = DifficultyLevel.BEGINNER,
        options: List[str] = None,
        correct_answer: str = "A programming language",
        points: int = 1,
        tags: List[str] = None,
    ) -> Question:
        """Create a test question."""
        if options is None:
            options = ["A programming language", "A snake", "A framework", "A database"]
        if tags is None:
            tags = ["python", "basics"]

        return Question(
            id=question_id,
            text=text,
            type=question_type,
            difficulty=difficulty,
            options=options,
            correct_answer=correct_answer,
            points=points,
            tags=tags,
        )

    @staticmethod
    def create_quiz(
        quiz_id: str = "test_quiz_1",
        title: str = "Python Basics Quiz",
        description: str = "Test your Python knowledge",
        questions: List[Question] = None,
        difficulty: DifficultyLevel = DifficultyLevel.BEGINNER,
        time_limit: int = 600,
    ) -> Quiz:
        """Create a test quiz."""
        if questions is None:
            questions = [TestDataFactory.create_question()]

        return Quiz(
            id=quiz_id,
            title=title,
            description=description,
            questions=questions,
            difficulty=difficulty,
            time_limit=time_limit,
        )

    @staticmethod
    def create_performance(
        user_id: str = "test_user_1",
        quiz_id: str = "test_quiz_1",
        score: int = 80,
        max_score: int = 100,
        completion_time: int = 300,
        difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE,
        days_ago: int = 0,
    ) -> UserPerformance:
        """Create a test user performance record."""
        timestamp = datetime.utcnow() - timedelta(days=days_ago)

        return UserPerformance(
            user_id=user_id,
            quiz_id=quiz_id,
            score=score,
            max_score=max_score,
            completion_time=completion_time,
            difficulty=difficulty,
            timestamp=timestamp,
        )

    @staticmethod
    def create_quiz_request(
        topic: str = "Python Programming",
        difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE,
        question_count: int = 5,
        question_types: List[QuestionType] = None,
        time_limit: int = 1800,
        focus_areas: List[str] = None,
    ) -> QuizGenerationRequest:
        """Create a test quiz generation request."""
        if question_types is None:
            question_types = [QuestionType.MULTIPLE_CHOICE]
        if focus_areas is None:
            focus_areas = ["basics", "fundamentals"]

        return QuizGenerationRequest(
            topic=topic,
            difficulty=difficulty,
            question_count=question_count,
            question_types=question_types,
            time_limit=time_limit,
            focus_areas=focus_areas,
        )

    @staticmethod
    def create_performance_history(
        user_id: str = "test_user",
        count: int = 10,
        score_range: tuple = (60, 90),
        difficulty: DifficultyLevel = DifficultyLevel.INTERMEDIATE,
    ) -> List[UserPerformance]:
        """Create a series of performance records."""
        import random

        performances = []

        for i in range(count):
            score = random.randint(score_range[0], score_range[1])
            performance = TestDataFactory.create_performance(
                user_id=user_id, quiz_id=f"quiz_{i}", score=score, difficulty=difficulty, days_ago=i
            )
            performances.append(performance)

        return performances


# Sample data collections
SAMPLE_QUESTIONS = [
    {
        "text": "What keyword is used to define a function in Python?",
        "type": QuestionType.MULTIPLE_CHOICE,
        "difficulty": DifficultyLevel.BEGINNER,
        "options": ["def", "function", "define", "func"],
        "correct_answer": "def",
        "explanation": "The 'def' keyword is used to define functions in Python",
        "points": 1,
        "tags": ["python", "functions", "syntax"],
    },
    {
        "text": "Python is an interpreted language.",
        "type": QuestionType.TRUE_FALSE,
        "difficulty": DifficultyLevel.BEGINNER,
        "options": ["True", "False"],
        "correct_answer": "True",
        "explanation": "Python is an interpreted language, not compiled",
        "points": 1,
        "tags": ["python", "interpretation"],
    },
    {
        "text": "What does 'len()' function return?",
        "type": QuestionType.SHORT_ANSWER,
        "difficulty": DifficultyLevel.INTERMEDIATE,
        "correct_answer": "length",
        "explanation": "The len() function returns the length of an object",
        "points": 2,
        "tags": ["python", "built-in", "functions"],
    },
]

SAMPLE_AI_RESPONSES = {
    "quiz_generation": {
        "title": "Python Programming Fundamentals",
        "description": "Test your understanding of Python basics",
        "questions": [
            {
                "text": "Which of the following is a mutable data type in Python?",
                "type": "multiple_choice",
                "difficulty": "intermediate",
                "options": ["tuple", "string", "list", "int"],
                "correct_answer": "list",
                "explanation": "Lists are mutable in Python, unlike tuples and strings",
                "points": 1,
                "tags": ["python", "data-types", "mutability"],
            },
            {
                "text": "What is the output of 'print(type([]))'?",
                "type": "multiple_choice",
                "difficulty": "intermediate",
                "options": ["<class 'list'>", "<class 'tuple'>", "<class 'dict'>", "<class 'set'>"],
                "correct_answer": "<class 'list'>",
                "explanation": "Empty brackets create a list object",
                "points": 1,
                "tags": ["python", "data-types", "built-in"],
            },
        ],
    },
    "single_question": {
        "text": "What is list comprehension in Python?",
        "type": "short_answer",
        "difficulty": "advanced",
        "correct_answer": "A concise way to create lists",
        "explanation": "List comprehension provides a concise way to create lists "
        "based on existing lists",
        "points": 2,
        "tags": ["python", "list-comprehension", "advanced"],
    },
}

# Performance scenarios for testing
PERFORMANCE_SCENARIOS = {
    "improving_user": [
        {"score": 60, "days_ago": 20},
        {"score": 65, "days_ago": 18},
        {"score": 70, "days_ago": 15},
        {"score": 75, "days_ago": 12},
        {"score": 80, "days_ago": 10},
        {"score": 85, "days_ago": 7},
        {"score": 90, "days_ago": 5},
        {"score": 88, "days_ago": 3},
        {"score": 92, "days_ago": 1},
        {"score": 95, "days_ago": 0},
    ],
    "declining_user": [
        {"score": 90, "days_ago": 20},
        {"score": 88, "days_ago": 18},
        {"score": 85, "days_ago": 15},
        {"score": 80, "days_ago": 12},
        {"score": 75, "days_ago": 10},
        {"score": 70, "days_ago": 7},
        {"score": 65, "days_ago": 5},
        {"score": 60, "days_ago": 3},
        {"score": 55, "days_ago": 1},
        {"score": 50, "days_ago": 0},
    ],
    "stable_user": [
        {"score": 78, "days_ago": 20},
        {"score": 80, "days_ago": 18},
        {"score": 82, "days_ago": 15},
        {"score": 79, "days_ago": 12},
        {"score": 81, "days_ago": 10},
        {"score": 80, "days_ago": 7},
        {"score": 78, "days_ago": 5},
        {"score": 83, "days_ago": 3},
        {"score": 79, "days_ago": 1},
        {"score": 80, "days_ago": 0},
    ],
}
