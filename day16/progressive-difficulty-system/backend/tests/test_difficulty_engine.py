import pytest
from datetime import datetime, timedelta
from backend.app.services.difficulty_engine import ProgressiveDifficultyEngine
from backend.app.models.schemas import *
from backend.app.config.settings import Settings

@pytest.fixture
def engine():
    settings = Settings()
    return ProgressiveDifficultyEngine(settings)

@pytest.fixture
def sample_responses():
    return [
        QuestionResponse(
            question_id="q1",
            is_correct=True,
            response_time_ms=15000,
            confidence_score=0.8,
            timestamp=datetime.now()
        ),
        QuestionResponse(
            question_id="q2",
            is_correct=True,
            response_time_ms=12000,
            confidence_score=0.9,
            timestamp=datetime.now()
        ),
        QuestionResponse(
            question_id="q3",
            is_correct=False,
            response_time_ms=25000,
            confidence_score=0.4,
            timestamp=datetime.now()
        )
    ]

@pytest.fixture
def session_data():
    return SessionData(
        session_id="test_session",
        start_time=datetime.now() - timedelta(minutes=10),
        questions_answered=3,
        current_streak=2,
        session_duration_ms=600000
    )

class TestDifficultyEngine:
    def test_analyze_performance_basic(self, engine, sample_responses):
        """Test basic performance analysis"""
        metrics = engine._analyze_performance(sample_responses)
        
        assert metrics['accuracy'] == 2/3  # 2 correct out of 3
        assert metrics['sample_size'] == 3
        assert 0 <= metrics['consistency'] <= 1
        assert isinstance(metrics['avg_response_time'], float)

    def test_analyze_performance_empty(self, engine):
        """Test performance analysis with empty responses"""
        metrics = engine._analyze_performance([])
        
        assert metrics['accuracy'] == 0.5  # Default
        assert metrics['sample_size'] == 0

    def test_determine_learning_state_warming_up(self, engine):
        """Test learning state determination for new users"""
        performance_metrics = {
            'accuracy': 0.8,
            'consistency': 0.7,
            'trend': 0.0,
            'sample_size': 3  # Less than 5
        }
        confidence_metrics = {'overall_confidence': 0.7}
        user_state = {}
        
        state = engine._determine_learning_state(performance_metrics, confidence_metrics, user_state)
        assert state == LearningState.WARMING_UP

    def test_determine_learning_state_struggling(self, engine):
        """Test learning state determination for struggling users"""
        performance_metrics = {
            'accuracy': 0.4,  # Low accuracy
            'consistency': 0.3,
            'trend': -0.3,  # Declining
            'sample_size': 10
        }
        confidence_metrics = {'overall_confidence': 0.4}
        user_state = {}
        
        state = engine._determine_learning_state(performance_metrics, confidence_metrics, user_state)
        assert state == LearningState.STRUGGLING

    def test_determine_learning_state_mastery(self, engine):
        """Test learning state determination for mastery users"""
        performance_metrics = {
            'accuracy': 0.95,  # Very high accuracy
            'consistency': 0.9,  # Very consistent
            'trend': 0.1,  # Improving
            'sample_size': 10
        }
        confidence_metrics = {'overall_confidence': 0.9}
        user_state = {}
        
        state = engine._determine_learning_state(performance_metrics, confidence_metrics, user_state)
        assert state == LearningState.MASTERY

    def test_calculate_difficulty_adjustment_struggling(self, engine):
        """Test difficulty adjustment for struggling users"""
        learning_state = LearningState.STRUGGLING
        performance_metrics = {'accuracy': 0.4, 'trend': -0.2}
        user_state = {'difficulty_level': DifficultyLevel.MEDIUM}
        
        new_difficulty = engine._calculate_difficulty_adjustment(learning_state, performance_metrics, user_state)
        
        # Should decrease difficulty
        assert new_difficulty in [DifficultyLevel.BEGINNER, DifficultyLevel.EASY]

    def test_calculate_difficulty_adjustment_mastery(self, engine):
        """Test difficulty adjustment for mastery users"""
        learning_state = LearningState.MASTERY
        performance_metrics = {'accuracy': 0.95, 'trend': 0.1}
        user_state = {'difficulty_level': DifficultyLevel.MEDIUM}
        
        new_difficulty = engine._calculate_difficulty_adjustment(learning_state, performance_metrics, user_state)
        
        # Should increase difficulty
        assert new_difficulty in [DifficultyLevel.HARD, DifficultyLevel.EXPERT]

    def test_score_to_difficulty_mapping(self, engine):
        """Test difficulty score to level mapping"""
        assert engine._score_to_difficulty(0.1) == DifficultyLevel.BEGINNER
        assert engine._score_to_difficulty(0.3) == DifficultyLevel.EASY
        assert engine._score_to_difficulty(0.5) == DifficultyLevel.MEDIUM
        assert engine._score_to_difficulty(0.7) == DifficultyLevel.HARD
        assert engine._score_to_difficulty(0.9) == DifficultyLevel.EXPERT

    def test_generate_reasoning(self, engine):
        """Test reasoning generation"""
        learning_state = LearningState.STRUGGLING
        performance_metrics = {'accuracy': 0.4, 'trend': -0.1}
        difficulty = DifficultyLevel.EASY
        
        reasoning = engine._generate_reasoning(learning_state, performance_metrics, difficulty)
        
        assert isinstance(reasoning, str)
        assert len(reasoning) > 10
        assert "easy" in reasoning.lower()

    def test_confidence_metrics_calculation(self, engine, sample_responses):
        """Test confidence metrics calculation"""
        metrics = engine._calculate_confidence_metrics(sample_responses)
        
        assert 'overall_confidence' in metrics
        assert 'confidence_accuracy_correlation' in metrics
        assert 0 <= metrics['overall_confidence'] <= 1

    def test_get_difficulty_range(self, engine):
        """Test difficulty range calculation"""
        range_dict = engine._get_difficulty_range(DifficultyLevel.MEDIUM)
        
        assert 'min' in range_dict
        assert 'max' in range_dict
        assert range_dict['min'] < range_dict['max']
        assert 0 <= range_dict['min'] <= 1
        assert 0 <= range_dict['max'] <= 1

if __name__ == "__main__":
    pytest.main([__file__])
