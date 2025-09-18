"""E2E Test Helper Functions"""
import asyncio
import time
import json
from typing import Dict, Any, List
from playwright.async_api import Page, expect
from tests.config.test_config import config

class E2ETestHelpers:
    """Collection of helper functions for E2E tests"""
    
    @staticmethod
    async def login_user(page: Page, email: str = "test@example.com", password: str = "testpass123"):
        """Login a test user"""
        await page.goto(f"{config.frontend_url}/login")
        await page.fill('[data-testid="email-input"]', email)
        await page.fill('[data-testid="password-input"]', password)
        await page.click('[data-testid="login-button"]')
        
        # Wait for successful login
        await expect(page.locator('[data-testid="dashboard"]')).to_be_visible(timeout=10000)
    
    @staticmethod
    async def navigate_to_quiz(page: Page, quiz_type: str = "general"):
        """Navigate to quiz selection and start a quiz"""
        await page.click(f'[data-testid="quiz-type-{quiz_type}"]')
        await page.click('[data-testid="start-quiz-button"]')
        
        # Wait for quiz to load
        await expect(page.locator('[data-testid="question-container"]')).to_be_visible(
            timeout=config.ai_response_timeout
        )
    
    @staticmethod
    async def measure_performance(page: Page, action_fn, threshold: float = 3.0) -> float:
        """Measure performance of an action"""
        start_time = time.time()
        await action_fn()
        end_time = time.time()
        
        duration = end_time - start_time
        assert duration <= threshold, f"Action took {duration:.2f}s, expected <= {threshold}s"
        return duration
    
    @staticmethod
    async def validate_ai_response(page: Page) -> Dict[str, Any]:
        """Validate AI-generated question quality"""
        question_text = await page.text_content('[data-testid="question-text"]')
        options = await page.locator('[data-testid^="option-"]').all_text_contents()
        
        validation = {
            "has_question": len(question_text) > 10,
            "has_options": len(options) >= 2,
            "question_quality": len(question_text.split()) >= 5,
            "options_variety": len(set(opt.lower() for opt in options)) == len(options)
        }
        
        assert validation["has_question"], "Question text is too short"
        assert validation["has_options"], "Insufficient answer options"
        assert validation["question_quality"], "Question quality is poor"
        
        return validation
    
    @staticmethod
    async def submit_quiz_answer(page: Page, option_index: int = 0):
        """Submit an answer to the current question"""
        await page.click(f'[data-testid="option-{option_index}"]')
        await page.click('[data-testid="submit-answer"]')
        
        # Wait for next question or results
        await page.wait_for_timeout(1000)
    
    @staticmethod
    async def complete_full_quiz(page: Page, num_questions: int = 5):
        """Complete a full quiz journey"""
        for i in range(num_questions):
            # Wait for question to load
            await expect(page.locator('[data-testid="question-container"]')).to_be_visible()
            
            # Validate AI-generated content
            await E2ETestHelpers.validate_ai_response(page)
            
            # Submit answer
            await E2ETestHelpers.submit_quiz_answer(page, i % 4)  # Vary answers
        
        # Wait for results page
        await expect(page.locator('[data-testid="quiz-results"]')).to_be_visible(timeout=10000)
    
    @staticmethod
    async def capture_performance_metrics(page: Page) -> Dict[str, Any]:
        """Capture detailed performance metrics"""
        metrics = await page.evaluate("""
            () => {
                const navigation = performance.getEntriesByType('navigation')[0];
                const resources = performance.getEntriesByType('resource');
                
                return {
                    page_load_time: navigation.loadEventEnd - navigation.fetchStart,
                    dom_content_loaded: navigation.domContentLoadedEventEnd - navigation.fetchStart,
                    first_contentful_paint: performance.getEntriesByName('first-contentful-paint')[0]?.startTime || 0,
                    resource_count: resources.length,
                    total_transfer_size: resources.reduce((total, r) => total + (r.transferSize || 0), 0)
                }
            }
        """)
        
        return metrics
