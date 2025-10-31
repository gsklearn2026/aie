"""Test AI response quality and consistency"""
import pytest
from playwright.async_api import Page, expect
from tests.utils.test_helpers import E2ETestHelpers
from tests.config.test_config import config

class TestAIValidation:
    """Test AI-generated content quality and performance"""
    
    @pytest.mark.asyncio
    async def test_ai_question_generation_speed(self, page: Page):
        """Test AI question generation meets performance requirements"""
        
        await E2ETestHelpers.login_user(page)
        
        # Measure AI response time
        async def generate_question():
            await E2ETestHelpers.navigate_to_quiz(page, "science")
        
        generation_time = await E2ETestHelpers.measure_performance(
            page, generate_question, config.max_ai_generation_time
        )
        
        print(f"AI generation time: {generation_time:.2f}s")
        
        # Validate question quality
        validation = await E2ETestHelpers.validate_ai_response(page)
        print(f"AI validation results: {validation}")
    
    @pytest.mark.asyncio
    async def test_ai_response_consistency(self, page: Page):
        """Test that AI generates consistent quality across multiple requests"""
        
        await E2ETestHelpers.login_user(page)
        
        validation_results = []
        
        # Generate multiple questions
        for i in range(3):
            await page.click('[data-testid="dashboard-link"]')
            await E2ETestHelpers.navigate_to_quiz(page, "mathematics")
            
            validation = await E2ETestHelpers.validate_ai_response(page)
            validation_results.append(validation)
            
            # Answer question to proceed
            await E2ETestHelpers.submit_quiz_answer(page, 0)
        
        # Verify consistency
        assert all(v["has_question"] for v in validation_results), "Inconsistent question generation"
        assert all(v["question_quality"] for v in validation_results), "Poor question quality detected"
        
        print(f"AI consistency test passed: {len(validation_results)} questions validated")
    
    @pytest.mark.asyncio
    async def test_ai_error_handling(self, page: Page):
        """Test graceful handling of AI service issues"""
        
        await E2ETestHelpers.login_user(page)
        
        # Navigate to quiz
        await page.goto(f"{config.frontend_url}/quiz/advanced")
        
        # Check for error handling UI
        error_indicator = page.locator('[data-testid="ai-loading-error"]')
        
        if await error_indicator.is_visible():
            # Verify error message is user-friendly
            error_text = await error_indicator.text_content()
            assert "temporarily unavailable" in error_text.lower() or "please try again" in error_text.lower()
            
            # Verify retry mechanism exists
            await expect(page.locator('[data-testid="retry-button"]')).to_be_visible()
