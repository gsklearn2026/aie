import pytest
import json
from unittest.mock import Mock, AsyncMock
from app.services.scoring_service import ScoringService
from app.models.scoring_models import QuizSubmission, QuestionAnswer, ScoringStrategy

@pytest.fixture
def mock_redis():
    redis_mock = Mock()
    redis_mock.get = Mock(return_value=None)
    redis_mock.setex = Mock()
    redis_mock.lpush = Mock()
    redis_mock.ltrim = Mock()
    redis_mock.lrange = Mock(return_value=[])
    return redis_mock

@pytest.fixture
def scoring_service(mock_redis):
    return ScoringService(mock_redis)

@pytest.fixture
def sample_submission():
    answers = [
        QuestionAnswer(
            question_id="q1",
            answer="correct",
            is_correct=True,
            time_taken=15.0,
            difficulty=2.0,
            weight=1.0
        ),
        QuestionAnswer(
            question_id="q2",
            answer="wrong",
            is_correct=False,
            time_taken=25.0,
            difficulty=3.0,
            weight=1.5
        )
    ]
    
    return QuizSubmission(
        quiz_id="test-quiz",
        user_id="test-user",
        answers=answers,
        total_time=40.0,
        strategy=ScoringStrategy.WEIGHTED
    )

@pytest.mark.asyncio
async def test_basic_scoring_calculation(scoring_service, sample_submission):
    """Test basic scoring calculation"""
    sample_submission.strategy = ScoringStrategy.BASIC
    result = await scoring_service.calculate_score(sample_submission)
    
    assert result.quiz_id == "test-quiz"
    assert result.user_id == "test-user"
    assert result.strategy_used == ScoringStrategy.BASIC
    assert result.raw_score == 50.0  # 1 correct out of 2 questions

@pytest.mark.asyncio
async def test_weighted_scoring_calculation(scoring_service, sample_submission):
    """Test weighted scoring calculation"""
    result = await scoring_service.calculate_score(sample_submission)
    
    assert result.quiz_id == "test-quiz"
    assert result.user_id == "test-user"
    assert result.strategy_used == ScoringStrategy.WEIGHTED
    # Weighted score should be different from basic
    assert result.raw_score != 50.0

@pytest.mark.asyncio
async def test_fallback_scoring(scoring_service, sample_submission, mock_redis):
    """Test fallback to basic scoring when main scoring fails"""
    # Mock redis to raise exception
    mock_redis.get.side_effect = Exception("Redis error")
    
    result = await scoring_service.calculate_score(sample_submission)
    
    # Should fallback to basic scoring
    assert result.strategy_used == ScoringStrategy.BASIC
    assert "fallback" in result.breakdown

def test_empty_submission():
    """Test handling of empty submission"""
    from app.services.scoring_strategies import BasicScoringStrategy
    
    strategy = BasicScoringStrategy()
    result = strategy.calculate_score([])
    
    assert result["raw_score"] == 0
    assert result["details"]["total"] == 0
