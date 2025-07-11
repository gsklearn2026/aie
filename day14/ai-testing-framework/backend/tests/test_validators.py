import pytest
from app.validators.content_validator import ContentValidator
from app.validators.performance_validator import PerformanceValidator

def test_content_validator_basic():
    validator = ContentValidator()
    
    content = "This is a test response with artificial intelligence concepts explained clearly."
    criteria = {
        "required_keywords": ["test", "intelligence"],
        "min_words": 5,
        "max_words": 100
    }
    
    result = validator.validate_response(content, criteria)
    
    assert result.score > 0
    assert result.details["word_count"] > 0
    assert result.details["keyword_coverage"] > 0

def test_content_validator_short_content():
    validator = ContentValidator()
    
    content = "Short"
    criteria = {"min_words": 10}
    
    result = validator.validate_response(content, criteria)
    
    assert not result.is_valid
    assert len(result.errors) > 0

@pytest.mark.asyncio
async def test_performance_validator():
    from app.services.ai_service import AIService
    
    validator = PerformanceValidator()
    ai_service = AIService()
    
    test_config = {
        "concurrent_users": 2,
        "requests_per_user": 2,
        "prompt": "Test performance",
        "max_response_time": 10000,
        "min_success_rate": 0.5
    }
    
    result = await validator.validate_performance(ai_service, test_config)
    
    assert "metrics" in result
    assert "validation" in result
    assert result["metrics"]["total_requests"] > 0
