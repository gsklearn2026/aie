import pytest
import asyncio
from services.difficulty.classifier import DifficultyClassifier
from models.schemas.difficulty import QuestionRequest, DifficultyLevel, QuestionType

@pytest.fixture
def classifier():
    return DifficultyClassifier()

@pytest.fixture
def sample_questions():
    return [
        QuestionRequest(
            question_text="What is 2 + 2?",
            subject="mathematics",
            question_type=QuestionType.MULTIPLE_CHOICE
        ),
        QuestionRequest(
            question_text="Explain the philosophical implications of quantum mechanics on deterministic worldviews in modern physics.",
            subject="physics", 
            question_type=QuestionType.ESSAY
        ),
        QuestionRequest(
            question_text="What is the capital of France?",
            subject="geography",
            question_type=QuestionType.MULTIPLE_CHOICE
        )
    ]

@pytest.mark.asyncio
async def test_classifier_initialization(classifier):
    await classifier.initialize()
    assert classifier.feature_extractor is not None

@pytest.mark.asyncio
async def test_basic_classification(classifier, sample_questions):
    await classifier.initialize()
    
    # Test easy question
    easy_result = await classifier.classify_question(sample_questions[0])
    assert easy_result.difficulty_level == DifficultyLevel.BEGINNER
    assert 0 <= easy_result.difficulty_score <= 1
    assert easy_result.processing_time_ms > 0
    
    # Test hard question  
    hard_result = await classifier.classify_question(sample_questions[1])
    assert hard_result.difficulty_level in [DifficultyLevel.ADVANCED, DifficultyLevel.EXPERT]
    assert hard_result.difficulty_score > easy_result.difficulty_score

@pytest.mark.asyncio
async def test_batch_classification(classifier, sample_questions):
    await classifier.initialize()
    
    results = await classifier.classify_batch(sample_questions)
    assert len(results) == len(sample_questions)
    
    for result in results:
        assert isinstance(result.difficulty_level, DifficultyLevel)
        assert 0 <= result.difficulty_score <= 1
        assert result.confidence > 0

def test_feature_extraction(classifier):
    features = classifier.feature_extractor.extract_all_features(
        "What is the capital of France?", 
        "multiple_choice",
        "geography"
    )
    
    assert 'flesch_kincaid' in features
    assert 'difficult_word_ratio' in features
    assert 'question_type_complexity' in features
    assert features['question_type_complexity'] == 0.3  # multiple choice complexity

def test_score_to_level_conversion(classifier):
    assert classifier._score_to_difficulty_level(0.1) == DifficultyLevel.BEGINNER
    assert classifier._score_to_difficulty_level(0.3) == DifficultyLevel.INTERMEDIATE
    assert classifier._score_to_difficulty_level(0.6) == DifficultyLevel.ADVANCED
    assert classifier._score_to_difficulty_level(0.9) == DifficultyLevel.EXPERT

@pytest.mark.asyncio
async def test_caching(classifier, sample_questions):
    await classifier.initialize()
    
    # First classification
    result1 = await classifier.classify_question(sample_questions[0])
    cache_size_after_first = len(classifier.cache)
    
    # Second classification of same question
    result2 = await classifier.classify_question(sample_questions[0])
    cache_size_after_second = len(classifier.cache)
    
    # Cache should not grow and results should be identical
    assert cache_size_after_first == cache_size_after_second
    assert result1.difficulty_score == result2.difficulty_score
