"""Test complete user journey for quiz completion"""
import pytest
from playwright.async_api import Page, expect
from tests.utils.test_helpers import E2ETestHelpers
from tests.config.test_config import config

class TestQuizCompletion:
    """Test complete quiz completion user journey"""
    
    @pytest.mark.asyncio
    async def test_complete_quiz_journey(self, page: Page):
        """Test full user journey from login to quiz completion"""
        
        # Step 1: Login
        await E2ETestHelpers.login_user(page)
        
        # Step 2: Navigate to quiz with performance measurement
        async def start_quiz():
            await E2ETestHelpers.navigate_to_quiz(page, "science")
        
        load_time = await E2ETestHelpers.measure_performance(
            page, start_quiz, config.max_quiz_load_time
        )
        print(f"Quiz load time: {load_time:.2f}s")
        
        # Step 3: Complete full quiz
        await E2ETestHelpers.complete_full_quiz(page, num_questions=5)
        
        # Step 4: Validate results page
        await expect(page.locator('[data-testid="final-score"]')).to_be_visible()
        score_text = await page.text_content('[data-testid="final-score"]')
        assert "Score:" in score_text, "Score not displayed properly"
        
        # Step 5: Capture final performance metrics
        metrics = await E2ETestHelpers.capture_performance_metrics(page)
        assert metrics["page_load_time"] < 5000, "Page load too slow"
        
        print(f"Performance metrics: {metrics}")
    
    @pytest.mark.asyncio
    async def test_quiz_state_persistence(self, page: Page):
        """Test that quiz state persists across page refreshes"""
        
        # Login and start quiz
        await E2ETestHelpers.login_user(page)
        await E2ETestHelpers.navigate_to_quiz(page, "history")
        
        # Answer first question
        await E2ETestHelpers.submit_quiz_answer(page, 0)
        
        # Refresh page
        await page.reload()
        
        # Verify quiz continues from correct position
        await expect(page.locator('[data-testid="question-number"]')).to_contain_text("2")
    
    @pytest.mark.asyncio
    async def test_multiple_quiz_completion(self, page: Page):
        """Test completing multiple quizzes in sequence (Quiz Marathon)"""
        
        await E2ETestHelpers.login_user(page)
        
        quiz_types = ["science", "history", "literature"]
        
        for quiz_type in quiz_types:
            print(f"Starting {quiz_type} quiz...")
            
            # Navigate to dashboard between quizzes
            await page.click('[data-testid="dashboard-link"]')
            await expect(page.locator('[data-testid="dashboard"]')).to_be_visible()
            
            # Start new quiz
            await E2ETestHelpers.navigate_to_quiz(page, quiz_type)
            
            # Complete quiz
            await E2ETestHelpers.complete_full_quiz(page, num_questions=3)
            
            # Verify completion
            await expect(page.locator('[data-testid="quiz-complete-message"]')).to_be_visible()
            
            # Check memory usage doesn't grow excessively
            memory_info = await page.evaluate("performance.memory ? performance.memory.usedJSHeapSize : 0")
            assert memory_info < 50_000_000, f"Memory usage too high: {memory_info} bytes"
        
        print("Quiz Marathon completed successfully!")
