import pytest
import asyncio
from app.testing.ai_test_suite import AITestSuite
from app.services.ai_service import AIService
from app.providers.mock_provider import MockProvider

@pytest.mark.asyncio
async def test_ai_test_suite_basic_generation():
    # Setup
    ai_service = AIService()
    test_suite = AITestSuite(ai_service)
    
    test_cases = [
        {
            "name": "basic_test",
            "type": "generation",
            "prompt": "Test prompt",
            "expected_keywords": ["test"],
            "min_length": 10
        }
    ]
    
    # Execute
    results = await test_suite.run_suite(test_cases)
    summary = test_suite.get_summary()
    
    # Verify
    assert len(results) == 1
    assert summary["summary"]["total"] == 1
    assert summary["summary"]["passed"] >= 0

@pytest.mark.asyncio
async def test_ai_test_suite_performance():
    ai_service = AIService()
    test_suite = AITestSuite(ai_service)
    
    test_cases = [
        {
            "name": "performance_test",
            "type": "performance", 
            "prompt": "Performance test",
            "concurrent_requests": 3,
            "max_response_time": 5000
        }
    ]
    
    results = await test_suite.run_suite(test_cases)
    assert len(results) == 1
    assert results[0].test_name == "performance_test"

@pytest.mark.asyncio
async def test_ai_test_suite_semantic_quality():
    ai_service = AIService()
    test_suite = AITestSuite(ai_service)
    
    test_cases = [
        {
            "name": "semantic_test",
            "type": "semantic",
            "prompt": "Explain machine learning",
            "expected_topics": ["machine", "learning"],
            "min_quality_score": 0.5
        }
    ]
    
    results = await test_suite.run_suite(test_cases)
    assert len(results) == 1
    assert results[0].details.get("quality_score") is not None
