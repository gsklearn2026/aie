"""Visual regression testing for UI consistency"""
import pytest
from playwright.async_api import Page, expect
from tests.utils.test_helpers import E2ETestHelpers

class TestVisualRegression:
    """Visual regression testing suite"""
    
    @pytest.mark.asyncio
    async def test_login_page_visual(self, page: Page):
        """Test login page visual consistency"""
        
        await page.goto("http://localhost:3000/login")
        await page.wait_for_load_state('networkidle')
        
        # Take screenshot for visual comparison
        await expect(page).to_have_screenshot('login-page.png')
    
    @pytest.mark.asyncio
    async def test_dashboard_visual(self, page: Page):
        """Test dashboard visual consistency"""
        
        await E2ETestHelpers.login_user(page)
        await page.wait_for_load_state('networkidle')
        
        # Take screenshot of dashboard
        await expect(page).to_have_screenshot('dashboard.png')
    
    @pytest.mark.asyncio
    async def test_quiz_interface_visual(self, page: Page):
        """Test quiz interface visual consistency"""
        
        await E2ETestHelpers.login_user(page)
        await E2ETestHelpers.navigate_to_quiz(page, "science")
        
        # Wait for AI-generated content to load
        await expect(page.locator('[data-testid="question-text"]')).to_be_visible()
        
        # Take screenshot of quiz interface
        await expect(page).to_have_screenshot('quiz-interface.png')
    
    @pytest.mark.asyncio
    async def test_responsive_design(self, page: Page):
        """Test responsive design across different viewports"""
        
        viewports = [
            {'width': 1920, 'height': 1080, 'name': 'desktop'},
            {'width': 768, 'height': 1024, 'name': 'tablet'},
            {'width': 375, 'height': 667, 'name': 'mobile'}
        ]
        
        await E2ETestHelpers.login_user(page)
        
        for viewport in viewports:
            await page.set_viewport_size(width=viewport['width'], height=viewport['height'])
            await page.wait_for_timeout(1000)  # Allow layout to settle
            
            # Take screenshot for each viewport
            await expect(page).to_have_screenshot(f'dashboard-{viewport["name"]}.png')
