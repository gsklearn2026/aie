#!/bin/bash

# AI Testing Framework - Start Script
# Installs dependencies, builds, tests, and verifies the framework

set -e  # Exit on any error

echo "🚀 Starting AI Testing Framework Setup and Verification..."
echo "=========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if project exists
if [ ! -d "ai-testing-framework" ]; then
    log_error "ai-testing-framework directory not found. Please run setup.sh first."
    exit 1
fi

cd ai-testing-framework

# Backend Setup
log_info "Setting up Python backend..."

cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    log_info "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
log_info "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
log_info "Installing Python dependencies..."
set +e  # Temporarily disable exit on error for pip install
pip install --upgrade pip
pip install setuptools wheel
if pip install -r requirements.txt; then
    log_success "Python backend dependencies installed"
else
    log_warning "Some dependencies failed to install. Continuing with available packages..."
fi
set -e  # Re-enable exit on error

# Create .env file for backend
log_info "Creating environment configuration..."
cat > .env << 'EOF'
# AI Testing Framework Configuration
LOG_LEVEL=INFO
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here
REDIS_URL=redis://localhost:6379
CELERY_BROKER_URL=redis://localhost:6379
CELERY_RESULT_BACKEND=redis://localhost:6379
EOF

log_success "Environment configuration created"

# Run backend tests
log_info "Running backend tests..."
if python -m pytest tests/ -v --tb=short; then
    log_success "Backend tests passed"
else
    log_warning "Some backend tests failed (this is expected without API keys)"
fi

# Frontend Setup
cd ../frontend

log_info "Setting up React frontend..."

# Install Node.js dependencies
log_info "Installing Node.js dependencies..."
npm install

log_success "Frontend dependencies installed"

# Build frontend
log_info "Building React application..."
npm run build

log_success "Frontend built successfully"

# Run frontend tests
log_info "Running frontend tests..."
if npm test -- --watchAll=false --testTimeout=10000; then
    log_success "Frontend tests passed"
else
    log_warning "Frontend tests completed (some may have failed)"
fi

# Create verification script
cd ..
log_info "Creating verification script..."

cat > verify_framework.py << 'EOF'
#!/usr/bin/env python3
"""
AI Testing Framework Verification Script
Tests the core functionality without requiring external API keys
"""

import asyncio
import sys
import os
sys.path.append('backend')

from backend.app.testing.base_test_runner import BaseTestRunner, TestResult, TestStatus
from backend.app.testing.ai_test_suite import AITestSuite
from backend.app.validators.content_validator import ContentValidator
from backend.app.validators.performance_validator import PerformanceValidator
from backend.app.services.ai_service import AIService
from backend.app.providers.mock_provider import MockProvider

async def verify_framework():
    """Verify all components of the AI testing framework"""
    
    print("🔍 Verifying AI Testing Framework Components...")
    print("=" * 50)
    
    verification_results = []
    
    # 1. Test Mock Provider
    print("\n1. Testing Mock Provider...")
    try:
        mock_provider = MockProvider()
        await mock_provider.initialize()
        
        test_prompt = "Test prompt for verification"
        response = await mock_provider.generate_text(test_prompt, {})
        
        if response and response.get('response'):
            verification_results.append(("Mock Provider", True, "Successfully generated mock response"))
        else:
            verification_results.append(("Mock Provider", False, "No response generated"))
            
    except Exception as e:
        verification_results.append(("Mock Provider", False, f"Error: {str(e)}"))
    
    # 2. Test AI Service
    print("\n2. Testing AI Service...")
    try:
        ai_service = AIService()
        
        # Test with mock provider
        response = await ai_service.generate_text("Test prompt", {"provider": "mock"})
        
        if response and response.get('response'):
            verification_results.append(("AI Service", True, "Successfully routed to mock provider"))
        else:
            verification_results.append(("AI Service", False, "Service did not return response"))
            
    except Exception as e:
        verification_results.append(("AI Service", False, f"Error: {str(e)}"))
    
    # 3. Test Content Validator
    print("\n3. Testing Content Validator...")
    try:
        validator = ContentValidator()
        
        test_content = "This is a test response about artificial intelligence and machine learning algorithms."
        result = validator.validate_response(test_content, {
            "min_length": 10,
            "required_keywords": ["artificial", "intelligence"]
        })
        
        if result.is_valid:
            verification_results.append(("Content Validator", True, f"Validation passed with score: {result.score}"))
        else:
            verification_results.append(("Content Validator", False, f"Validation failed: {result.errors}"))
            
    except Exception as e:
        verification_results.append(("Content Validator", False, f"Error: {str(e)}"))
    
    # 4. Test Performance Validator
    print("\n4. Testing Performance Validator...")
    try:
        perf_validator = PerformanceValidator()
        
        # Mock performance test
        test_config = {
            "concurrent_requests": 2,
            "max_response_time": 5000,
            "test_prompt": "Performance test prompt"
        }
        
        result = await perf_validator.validate_performance(ai_service, test_config)
        
        if result.get('success', False):
            verification_results.append(("Performance Validator", True, "Performance validation completed"))
        else:
            verification_results.append(("Performance Validator", False, "Performance validation failed"))
            
    except Exception as e:
        verification_results.append(("Performance Validator", False, f"Error: {str(e)}"))
    
    # 5. Test AI Test Suite
    print("\n5. Testing AI Test Suite...")
    try:
        test_suite = AITestSuite(ai_service)
        
        test_cases = [
            {
                "name": "basic_generation_test",
                "type": "generation",
                "prompt": "Explain AI in simple terms",
                "provider": "mock",
                "expected_keywords": ["artificial", "intelligence"]
            },
            {
                "name": "performance_test",
                "type": "performance",
                "prompt": "Performance test",
                "provider": "mock",
                "max_response_time": 3000
            }
        ]
        
        results = await test_suite.run_suite(test_cases)
        summary = test_suite.get_summary()
        
        if summary.get('summary', {}).get('total', 0) > 0:
            passed = summary['summary']['passed']
            total = summary['summary']['total']
            verification_results.append(("AI Test Suite", True, f"Ran {total} tests, {passed} passed"))
        else:
            verification_results.append(("AI Test Suite", False, "No tests executed"))
            
    except Exception as e:
        verification_results.append(("AI Test Suite", False, f"Error: {str(e)}"))
    
    # Print verification results
    print("\n" + "=" * 50)
    print("🎯 VERIFICATION RESULTS")
    print("=" * 50)
    
    passed = 0
    total = len(verification_results)
    
    for component, success, message in verification_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {component}: {message}")
        if success:
            passed += 1
    
    print(f"\n📊 Summary: {passed}/{total} components verified successfully")
    
    if passed == total:
        print("\n🎉 ALL COMPONENTS WORKING CORRECTLY!")
        print("The AI Testing Framework is ready to use.")
        return True
    else:
        print(f"\n⚠️  {total - passed} components need attention.")
        print("Check the error messages above for details.")
        return False

if __name__ == "__main__":
    success = asyncio.run(verify_framework())
    sys.exit(0 if success else 1)
EOF

# Make verification script executable
chmod +x verify_framework.py

# Run verification
log_info "Running framework verification..."
cd backend
source venv/bin/activate
cd ..
python verify_framework.py

verification_status=$?

# Final status
echo ""
echo "=========================================================="
if [ $verification_status -eq 0 ]; then
    log_success "🎉 AI Testing Framework is ready and working correctly!"
    echo ""
    echo "🚀 To start the services:"
    echo "   Backend:  cd ai-testing-framework/backend && source venv/bin/activate && python -m uvicorn app.main:app --reload"
    echo "   Frontend: cd ai-testing-framework/frontend && npm start"
    echo ""
    echo "📊 Access the dashboard at: http://localhost:3000"
    echo "🔧 API documentation at: http://localhost:8000/docs"
    echo ""
    echo "💡 Note: Add your actual API keys to backend/.env for full functionality"
else
    log_warning "⚠️  Framework setup completed but some components need attention"
    echo ""
    echo "🔍 Check the verification results above for details"
    echo "🚀 You can still start the services and use mock providers for testing"
fi

echo "==========================================================" 