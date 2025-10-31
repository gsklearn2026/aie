"""Performance and load testing for Quiz Platform"""
import pytest
import asyncio
from playwright.async_api import Page, Browser, BrowserContext
from tests.utils.test_helpers import E2ETestHelpers
from tests.config.test_config import config

class TestPerformance:
    """Performance testing suite"""
    
    @pytest.mark.asyncio
    async def test_concurrent_users(self, browser: Browser):
        """Test system performance with multiple concurrent users"""
        
        concurrent_users = 5
        contexts = []
        pages = []
        
        try:
            # Create multiple browser contexts (simulating different users)
            for i in range(concurrent_users):
                context = await browser.new_context()
                page = await context.new_page()
                contexts.append(context)
                pages.append(page)
            
            # Simulate concurrent user actions
            async def user_session(page, user_id):
                try:
                    await E2ETestHelpers.login_user(page, f"user{user_id}@example.com")
                    await E2ETestHelpers.navigate_to_quiz(page, "science")
                    await E2ETestHelpers.complete_full_quiz(page, num_questions=3)
                    return True
                except Exception as e:
                    print(f"User {user_id} failed: {e}")
                    return False
            
            # Run concurrent sessions
            tasks = [user_session(page, i) for i, page in enumerate(pages)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verify most sessions completed successfully
            success_count = sum(1 for r in results if r is True)
            print(f"Successful concurrent sessions: {success_count}/{concurrent_users}")
            
            assert success_count >= concurrent_users * 0.8, "Too many concurrent session failures"
            
        finally:
            # Cleanup
            for context in contexts:
                await context.close()
    
    @pytest.mark.asyncio
    async def test_memory_usage_monitoring(self, page: Page):
        """Monitor memory usage during extended quiz sessions"""
        
        await E2ETestHelpers.login_user(page)
        
        initial_memory = await page.evaluate("performance.memory ? performance.memory.usedJSHeapSize : 0")
        print(f"Initial memory usage: {initial_memory / 1024 / 1024:.2f} MB")
        
        # Complete multiple quizzes to test for memory leaks
        for i in range(5):
            await E2ETestHelpers.navigate_to_quiz(page, "general")
            await E2ETestHelpers.complete_full_quiz(page, num_questions=2)
            
            current_memory = await page.evaluate("performance.memory ? performance.memory.usedJSHeapSize : 0")
            memory_growth = (current_memory - initial_memory) / 1024 / 1024
            
            print(f"Quiz {i+1} - Memory usage: {current_memory / 1024 / 1024:.2f} MB (growth: {memory_growth:.2f} MB)")
            
            # Alert if memory growth is excessive
            assert memory_growth < 50, f"Excessive memory growth detected: {memory_growth:.2f} MB"
    
    @pytest.mark.asyncio
    async def test_network_performance(self, page: Page):
        """Test network request performance and optimization"""
        
        # Track network requests
        requests = []
        
        def handle_request(request):
            requests.append({
                'url': request.url,
                'method': request.method,
                'resource_type': request.resource_type
            })
        
        page.on('request', handle_request)
        
        # Perform typical user journey
        await E2ETestHelpers.login_user(page)
        await E2ETestHelpers.navigate_to_quiz(page, "science")
        await E2ETestHelpers.submit_quiz_answer(page, 0)
        
        # Analyze network requests
        api_requests = [r for r in requests if '/api/' in r['url']]
        static_requests = [r for r in requests if r['resource_type'] in ['image', 'stylesheet', 'script']]
        
        print(f"API requests: {len(api_requests)}")
        print(f"Static resource requests: {len(static_requests)}")
        
        # Verify reasonable request counts
        assert len(api_requests) < 20, "Too many API requests detected"
        assert len(static_requests) < 50, "Too many static resource requests"
