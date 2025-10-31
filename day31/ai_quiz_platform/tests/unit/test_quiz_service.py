"""Comprehensive unit tests for quiz service."""

from unittest.mock import AsyncMock, patch

import pytest

from src.models import (
    DifficultyLevel,
    Question,
    QuestionType,
    Quiz,
    QuizGenerationRequest,
    UserPerformance,
)
from src.services.ai_service import AIServiceError
from src.services.quiz_service import QuizService, QuizServiceError


class TestQuizService:
    """Test suite for QuizService class."""

    @pytest.fixture
    def quiz_service(self):
        """Create fresh quiz service instance for each test."""
        return QuizService()

    @pytest.fixture
    def sample_quiz_request(self):
        """Sample quiz generation request."""
        return QuizGenerationRequest(
            topic="Python Programming",
            difficulty=DifficultyLevel.INTERMEDIATE,
            question_count=5,
            question_types=[QuestionType.MULTIPLE_CHOICE],
            time_limit=1800,
        )

    @pytest.fixture
    def sample_question(self):
        """Sample question for testing."""
        return Question(
            id="q1",
            text="What is Python?",
            type=QuestionType.MULTIPLE_CHOICE,
            difficulty=DifficultyLevel.BEGINNER,
            options=["A language", "A snake", "A framework", "A database"],
            correct_answer="A language",
            explanation="Python is a programming language",
            points=1,
            tags=["python", "basics"],
        )

    @pytest.fixture
    def sample_quiz(self, sample_question):
        """Sample quiz for testing."""
        return Quiz(
            id="quiz1",
            title="Python Basics",
            description="Test your Python knowledge",
            questions=[sample_question],
            difficulty=DifficultyLevel.BEGINNER,
            time_limit=600,
        )

    @pytest.fixture
    def sample_performance(self):
        """Sample user performance data."""
        return UserPerformance(
            user_id="user123",
            quiz_id="quiz1",
            score=80,
            max_score=100,
            completion_time=300,
            difficulty=DifficultyLevel.INTERMEDIATE,
        )

    # Quiz Creation Tests
    @pytest.mark.asyncio
    async def test_create_quiz_success(self, quiz_service, sample_quiz_request):
        """Test successful quiz creation."""
        # Mock AI service response
        mock_quiz = Quiz(
            title="Python Programming Quiz",
            description="Test your Python skills",
            questions=[
                Question(
                    text="What is Python?",
                    type=QuestionType.MULTIPLE_CHOICE,
                    difficulty=DifficultyLevel.INTERMEDIATE,
                    options=["Language", "Snake", "Framework", "Tool"],
                    correct_answer="Language",
                    explanation="Python is a programming language",
                    points=1,
                    tags=["python"],
                )
            ],
            difficulty=DifficultyLevel.INTERMEDIATE,
            time_limit=1800,
        )

        with patch(
            "src.services.quiz_service.ai_service.generate_quiz", new_callable=AsyncMock
        ) as mock_generate:
            mock_generate.return_value = mock_quiz

            result = await quiz_service.create_quiz(sample_quiz_request)

            assert result is not None
            assert result.id is not None
            assert result.title == "Python Programming Quiz"
            assert len(result.questions) == 1
            assert result.difficulty == DifficultyLevel.INTERMEDIATE
            mock_generate.assert_called_once_with(sample_quiz_request)

    @pytest.mark.asyncio
    async def test_create_quiz_ai_service_error(self, quiz_service, sample_quiz_request):
        """Test quiz creation with AI service error."""
        with patch(
            "src.services.quiz_service.ai_service.generate_quiz", new_callable=AsyncMock
        ) as mock_generate:
            mock_generate.side_effect = AIServiceError("AI service unavailable")

            with pytest.raises(QuizServiceError) as exc_info:
                await quiz_service.create_quiz(sample_quiz_request)

            assert "Failed to create quiz" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_quiz_invalid_request(self, quiz_service):
        """Test quiz creation with invalid request."""
        # Test with a topic that's too short - this will be caught by Pydantic validation
        with pytest.raises(Exception):  # Pydantic validation error
            QuizGenerationRequest(topic="", difficulty=DifficultyLevel.BEGINNER, question_count=5)

    @pytest.mark.asyncio
    async def test_create_quiz_question_count_validation(self, quiz_service):
        """Test quiz creation with invalid question count."""
        # Test with question count > 20 - this will be caught by Pydantic validation
        with pytest.raises(Exception):  # Pydantic validation error
            QuizGenerationRequest(
                topic="Python",
                difficulty=DifficultyLevel.BEGINNER,
                question_count=25,  # Invalid count > 20
            )

    # Quiz Retrieval Tests
    def test_get_quiz_exists(self, quiz_service, sample_quiz):
        """Test retrieving existing quiz."""
        quiz_service._quiz_store[sample_quiz.id] = sample_quiz

        result = quiz_service.get_quiz(sample_quiz.id)

        assert result == sample_quiz

    def test_get_quiz_not_exists(self, quiz_service):
        """Test retrieving non-existent quiz."""
        result = quiz_service.get_quiz("nonexistent")

        assert result is None

    def test_list_quizzes_empty(self, quiz_service):
        """Test listing quizzes when store is empty."""
        result = quiz_service.list_quizzes()

        assert result == []

    def test_list_quizzes_with_data(self, quiz_service, sample_quiz):
        """Test listing quizzes with data."""
        quiz_service._quiz_store[sample_quiz.id] = sample_quiz

        result = quiz_service.list_quizzes()

        assert len(result) == 1
        assert result[0] == sample_quiz

    def test_list_quizzes_filtered_by_difficulty(self, quiz_service):
        """Test listing quizzes filtered by difficulty."""
        # Create a sample question for the quizzes
        sample_question = Question(
            text="What is Python?",
            type=QuestionType.MULTIPLE_CHOICE,
            difficulty=DifficultyLevel.BEGINNER,
            options=["Language", "Snake"],
            correct_answer="Language",
            points=1,
        )

        beginner_quiz = Quiz(
            id="quiz1",
            title="Beginner Quiz",
            questions=[sample_question],
            difficulty=DifficultyLevel.BEGINNER,
        )

        intermediate_quiz = Quiz(
            id="quiz2",
            title="Intermediate Quiz",
            questions=[sample_question],
            difficulty=DifficultyLevel.INTERMEDIATE,
        )

        quiz_service._quiz_store["quiz1"] = beginner_quiz
        quiz_service._quiz_store["quiz2"] = intermediate_quiz

        result = quiz_service.list_quizzes(difficulty=DifficultyLevel.BEGINNER)

        assert len(result) == 1
        assert result[0].difficulty == DifficultyLevel.BEGINNER

    # Adaptive Difficulty Tests
    def test_calculate_adaptive_difficulty_no_history(self, quiz_service):
        """Test adaptive difficulty calculation with no performance history."""
        result = quiz_service.calculate_adaptive_difficulty("new_user")

        assert result == DifficultyLevel.BEGINNER

    def test_calculate_adaptive_difficulty_excellent_performance(self, quiz_service):
        """Test adaptive difficulty with excellent performance."""
        user_id = "user123"

        # Add high-scoring performances
        for i in range(5):
            performance = UserPerformance(
                user_id=user_id,
                quiz_id=f"quiz{i}",
                score=90,
                max_score=100,
                completion_time=300,
                difficulty=DifficultyLevel.INTERMEDIATE,
            )
            quiz_service.record_performance(performance)

        result = quiz_service.calculate_adaptive_difficulty(user_id)

        assert result == DifficultyLevel.EXPERT

    def test_calculate_adaptive_difficulty_poor_performance(self, quiz_service):
        """Test adaptive difficulty with poor performance."""
        user_id = "user123"

        # Add low-scoring performances
        for i in range(5):
            performance = UserPerformance(
                user_id=user_id,
                quiz_id=f"quiz{i}",
                score=40,
                max_score=100,
                completion_time=300,
                difficulty=DifficultyLevel.BEGINNER,
            )
            quiz_service.record_performance(performance)

        result = quiz_service.calculate_adaptive_difficulty(user_id)

        assert result == DifficultyLevel.BEGINNER

    def test_calculate_adaptive_difficulty_mixed_performance(self, quiz_service):
        """Test adaptive difficulty with mixed performance."""
        user_id = "user123"

        # Add mixed scoring performances
        scores = [75, 80, 70, 85, 75]
        for i, score in enumerate(scores):
            performance = UserPerformance(
                user_id=user_id,
                quiz_id=f"quiz{i}",
                score=score,
                max_score=100,
                completion_time=300,
                difficulty=DifficultyLevel.INTERMEDIATE,
            )
            quiz_service.record_performance(performance)

        result = quiz_service.calculate_adaptive_difficulty(user_id)

        assert result == DifficultyLevel.ADVANCED

    # Performance Recording Tests
    def test_record_performance_new_user(self, quiz_service, sample_performance):
        """Test recording performance for new user."""
        quiz_service.record_performance(sample_performance)

        performances = quiz_service._performance_store.get(sample_performance.user_id, [])
        assert len(performances) == 1
        assert performances[0] == sample_performance

    def test_record_performance_existing_user(self, quiz_service, sample_performance):
        """Test recording additional performance for existing user."""
        # Record first performance
        quiz_service.record_performance(sample_performance)

        # Record second performance
        second_performance = UserPerformance(
            user_id=sample_performance.user_id,
            quiz_id="quiz2",
            score=90,
            max_score=100,
            completion_time=250,
            difficulty=DifficultyLevel.ADVANCED,
        )
        quiz_service.record_performance(second_performance)

        performances = quiz_service._performance_store.get(sample_performance.user_id, [])
        assert len(performances) == 2

    def test_record_performance_limit_history(self, quiz_service):
        """Test that performance history is limited to 50 entries."""
        user_id = "user123"

        # Record 55 performances
        for i in range(55):
            performance = UserPerformance(
                user_id=user_id,
                quiz_id=f"quiz{i}",
                score=80,
                max_score=100,
                completion_time=300,
                difficulty=DifficultyLevel.INTERMEDIATE,
            )
            quiz_service.record_performance(performance)

        performances = quiz_service._performance_store.get(user_id, [])
        assert len(performances) == 50

    # User Statistics Tests
    def test_get_user_statistics_no_data(self, quiz_service):
        """Test user statistics with no performance data."""
        result = quiz_service.get_user_statistics("new_user")

        expected = {
            "total_attempts": 0,
            "average_score": 0,
            "best_score": 0,
            "current_streak": 0,
            "recommended_difficulty": DifficultyLevel.BEGINNER.value,
        }

        for key, value in expected.items():
            assert result[key] == value

    def test_get_user_statistics_with_data(self, quiz_service):
        """Test user statistics with performance data."""
        user_id = "user123"

        # Add varied performances
        scores = [70, 80, 75, 85, 90]
        for i, score in enumerate(scores):
            performance = UserPerformance(
                user_id=user_id,
                quiz_id=f"quiz{i}",
                score=score,
                max_score=100,
                completion_time=300,
                difficulty=DifficultyLevel.INTERMEDIATE,
            )
            quiz_service.record_performance(performance)

        result = quiz_service.get_user_statistics(user_id)

        assert result["total_attempts"] == 5
        assert result["average_score"] == 80.0
        assert result["best_score"] == 90.0
        assert result["current_streak"] == 5  # All scores >= 70%
        assert "performance_trend" in result

    # Answer Validation Tests
    def test_validate_quiz_answers_all_correct(self, quiz_service, sample_quiz):
        """Test answer validation with all correct answers."""
        user_answers = {"q1": "A language"}

        result = quiz_service.validate_quiz_answers(sample_quiz, user_answers)

        assert result["total_questions"] == 1
        assert result["correct_answers"] == 1
        assert result["total_points"] == 1
        assert result["percentage_score"] == 100.0
        assert len(result["question_results"]) == 1
        assert result["question_results"][0]["is_correct"] is True

    def test_validate_quiz_answers_all_wrong(self, quiz_service, sample_quiz):
        """Test answer validation with all wrong answers."""
        user_answers = {"q1": "A snake"}

        result = quiz_service.validate_quiz_answers(sample_quiz, user_answers)

        assert result["total_questions"] == 1
        assert result["correct_answers"] == 0
        assert result["total_points"] == 0
        assert result["percentage_score"] == 0.0
        assert result["question_results"][0]["is_correct"] is False

    def test_validate_quiz_answers_mixed(self, quiz_service):
        """Test answer validation with mixed correct/incorrect answers."""
        questions = [
            Question(
                id="q1",
                text="What is Python?",
                type=QuestionType.MULTIPLE_CHOICE,
                difficulty=DifficultyLevel.BEGINNER,
                options=["Language", "Snake"],
                correct_answer="Language",
                points=1,
            ),
            Question(
                id="q2",
                text="Is Python interpreted?",
                type=QuestionType.TRUE_FALSE,
                difficulty=DifficultyLevel.BEGINNER,
                options=["True", "False"],
                correct_answer="True",
                points=2,
            ),
        ]

        quiz = Quiz(
            id="quiz1", title="Mixed Quiz", questions=questions, difficulty=DifficultyLevel.BEGINNER
        )

        user_answers = {"q1": "Language", "q2": "False"}  # First correct, second wrong

        result = quiz_service.validate_quiz_answers(quiz, user_answers)

        assert result["total_questions"] == 2
        assert result["correct_answers"] == 1
        assert result["total_points"] == 1  # Only first question points
        assert result["max_points"] == 3
        assert result["percentage_score"] == pytest.approx(33.33, rel=1e-2)

    def test_validate_quiz_answers_empty_quiz(self, quiz_service):
        """Test answer validation with empty quiz."""
        # Create a quiz with one question to test the validation logic
        sample_question = Question(
            text="What is Python?",
            type=QuestionType.MULTIPLE_CHOICE,
            difficulty=DifficultyLevel.BEGINNER,
            options=["Language", "Snake"],
            correct_answer="Language",
            points=1,
        )

        # Test with None quiz (which should trigger the validation error)
        with pytest.raises(QuizServiceError):
            quiz_service.validate_quiz_answers(None, {})

    def test_validate_quiz_answers_case_insensitive(self, quiz_service, sample_quiz):
        """Test that answer validation is case insensitive."""
        user_answers = {"q1": "A LANGUAGE"}  # Different case

        result = quiz_service.validate_quiz_answers(sample_quiz, user_answers)

        assert result["question_results"][0]["is_correct"] is True

    def test_validate_quiz_answers_whitespace_handling(self, quiz_service, sample_quiz):
        """Test that answer validation handles whitespace."""
        user_answers = {"q1": "  A language  "}  # Extra whitespace

        result = quiz_service.validate_quiz_answers(sample_quiz, user_answers)

        assert result["question_results"][0]["is_correct"] is True

    # Performance Trend Tests
    def test_performance_trend_insufficient_data(self, quiz_service):
        """Test performance trend with insufficient data."""
        user_id = "user123"

        # Add only 2 performances (less than minimum 3)
        for i in range(2):
            performance = UserPerformance(
                user_id=user_id,
                quiz_id=f"quiz{i}",
                score=80,
                max_score=100,
                completion_time=300,
                difficulty=DifficultyLevel.INTERMEDIATE,
            )
            quiz_service.record_performance(performance)

        stats = quiz_service.get_user_statistics(user_id)
        assert stats["performance_trend"] == "insufficient_data"

    def test_performance_trend_improving(self, quiz_service):
        """Test performance trend detection for improving performance."""
        user_id = "user123"

        # Add performances showing improvement (older scores lower, recent higher)
        older_scores = [60, 65, 70, 70, 75]  # Average: 68
        recent_scores = [80, 85, 80, 85, 90]  # Average: 84

        all_scores = older_scores + recent_scores
        for i, score in enumerate(all_scores):
            performance = UserPerformance(
                user_id=user_id,
                quiz_id=f"quiz{i}",
                score=score,
                max_score=100,
                completion_time=300,
                difficulty=DifficultyLevel.INTERMEDIATE,
            )
            quiz_service.record_performance(performance)

        stats = quiz_service.get_user_statistics(user_id)
        assert stats["performance_trend"] == "improving"

    def test_performance_trend_declining(self, quiz_service):
        """Test performance trend detection for declining performance."""
        user_id = "user123"

        # Add performances showing decline (older scores higher, recent lower)
        older_scores = [90, 85, 88, 90, 87]  # Average: 88
        recent_scores = [75, 70, 80, 75, 70]  # Average: 74

        all_scores = older_scores + recent_scores
        for i, score in enumerate(all_scores):
            performance = UserPerformance(
                user_id=user_id,
                quiz_id=f"quiz{i}",
                score=score,
                max_score=100,
                completion_time=300,
                difficulty=DifficultyLevel.INTERMEDIATE,
            )
            quiz_service.record_performance(performance)

        stats = quiz_service.get_user_statistics(user_id)
        assert stats["performance_trend"] == "declining"

    def test_performance_trend_stable(self, quiz_service):
        """Test performance trend detection for stable performance."""
        user_id = "user123"

        # Add performances showing stability (similar scores throughout)
        stable_scores = [80, 78, 82, 80, 81, 79, 80, 82, 78, 80]

        for i, score in enumerate(stable_scores):
            performance = UserPerformance(
                user_id=user_id,
                quiz_id=f"quiz{i}",
                score=score,
                max_score=100,
                completion_time=300,
                difficulty=DifficultyLevel.INTERMEDIATE,
            )
            quiz_service.record_performance(performance)

        stats = quiz_service.get_user_statistics(user_id)
        assert stats["performance_trend"] == "stable"

    # Edge Case Tests
    def test_quiz_service_initialization(self):
        """Test quiz service initializes with empty stores."""
        service = QuizService()

        assert len(service._quiz_store) == 0
        assert len(service._performance_store) == 0
        assert len(service._question_bank) == 0

    def test_generate_quiz_id_uniqueness(self, quiz_service):
        """Test that generated quiz IDs are unique."""
        id1 = quiz_service._generate_quiz_id()
        id2 = quiz_service._generate_quiz_id()

        assert id1 != id2
        assert len(id1) > 0
        assert len(id2) > 0

    def test_update_question_bank(self, quiz_service, sample_question):
        """Test question bank is updated when quiz is created."""
        questions = [sample_question]
        quiz_service._update_question_bank(questions)

        # Check that question was added to bank
        topic_key = "_".join(sample_question.tags)
        assert topic_key in quiz_service._question_bank
        assert sample_question in quiz_service._question_bank[topic_key]

    def test_update_question_bank_no_tags(self, quiz_service):
        """Test question bank update with questions that have no tags."""
        question = Question(
            text="Test question",
            type=QuestionType.TRUE_FALSE,
            difficulty=DifficultyLevel.BEGINNER,
            correct_answer="True",
            tags=[],  # No tags
        )

        quiz_service._update_question_bank([question])

        assert "general" in quiz_service._question_bank
        assert question in quiz_service._question_bank["general"]
