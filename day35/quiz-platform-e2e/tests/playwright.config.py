"""Playwright configuration for E2E tests"""
from playwright.async_api import expect
expect.set_options(timeout=10_000)

# Test configuration
TEST_CONFIG = {
    'base_url': 'http://localhost:3000',
    'timeout': 30_000,
    'expect_timeout': 5_000,
    'browsers': ['chromium', 'firefox', 'webkit'],
    'headless': True,
    'screenshot': 'only-on-failure',
    'video': 'retain-on-failure',
    'trace': 'retain-on-failure'
}
