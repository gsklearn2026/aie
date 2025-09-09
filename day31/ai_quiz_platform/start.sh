#!/bin/bash

echo "=== AI Quiz Platform - Unit Testing Demo Start Script ==="

# Function to show options
show_options() {
    echo ""
    echo "Start Options:"
    echo "1. Run test suite only"
    echo "2. Start development server with test monitoring"
    echo "3. Interactive test exploration"
    echo "4. Coverage analysis dashboard"
    echo ""
    read -p "Select option (1-4): " START_OPTION
}

# Function to run test suite
run_test_suite() {
    echo "Running comprehensive test suite..."
    
    # Activate virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo "✓ Virtual environment activated"
    fi
    
    # Set environment variables
    export PYTHONPATH=$(pwd)/src
    export ENVIRONMENT=testing
    export GEMINI_API_KEY=test_key_for_testing
    
    # Run tests with different configurations
    echo "Running unit tests..."
    pytest tests/unit/ -v --tb=short
    
    echo "Running tests with coverage..."
    pytest tests/unit/ --cov=src --cov-report=term
    
    echo "Running performance tests..."
    pytest tests/unit/ -k "performance" -v
}

# Function to start development server with test monitoring
start_dev_server() {
    echo "Starting development server with test monitoring..."
    
    # Activate virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Install pytest-watch for continuous testing
    pip install pytest-watch
    
    echo "Starting file watcher for continuous testing..."
    echo "Tests will run automatically when files change..."
    
    # Start continuous testing
    ptw --runner "pytest tests/unit/ -x -v --tb=short"
}

# Function for interactive test exploration
interactive_test_exploration() {
    echo "Starting interactive test exploration..."
    
    # Activate virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    echo "Interactive Test Menu:"
    echo "1. Run specific test file"
    echo "2. Run tests by keyword"
    echo "3. Debug failing tests"
    echo "4. Generate detailed coverage report"
    
    read -p "Select option (1-4): " TEST_OPTION
    
    case $TEST_OPTION in
        1)
            echo "Available test files:"
            ls tests/unit/
            read -p "Enter test file name: " TEST_FILE
            pytest "tests/unit/$TEST_FILE" -v
            ;;
        2)
            read -p "Enter keyword to filter tests: " KEYWORD
            pytest tests/unit/ -k "$KEYWORD" -v
            ;;
        3)
            echo "Running tests with detailed debugging..."
            pytest tests/unit/ -vvv --tb=long --pdb-trace
            ;;
        4)
            pytest tests/unit/ --cov=src --cov-report=html
            echo "Opening coverage report..."
            open htmlcov/index.html || echo "Open htmlcov/index.html in your browser"
            ;;
    esac
}

# Function to start coverage analysis dashboard
start_coverage_dashboard() {
    echo "Starting coverage analysis dashboard..."
    
    # Activate virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # Generate comprehensive coverage report
    pytest tests/unit/ --cov=src --cov-report=html --cov-report=json
    
    # Create coverage dashboard script
    cat > coverage_dashboard.py << 'DASHBOARD'
#!/usr/bin/env python3
"""Coverage analysis dashboard."""

import json
import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

def create_dashboard_html():
    """Create interactive coverage dashboard."""
    
    # Load coverage data
    try:
        with open('coverage.json') as f:
            coverage_data = json.load(f)
    except FileNotFoundError:
        print("No coverage data found. Run tests with coverage first.")
        return
    
    total_coverage = coverage_data['totals']['percent_covered']
    
    html_content = f'''
<!DOCTYPE html>
<html>
<head>
    <title>AI Quiz Platform - Test Coverage Dashboard</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background: #f0f8ff; padding: 20px; border-radius: 8px; }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; 
                  background: white; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .coverage-bar {{ width: 300px; height: 20px; background: #eee; border-radius: 10px; overflow: hidden; }}
        .coverage-fill {{ height: 100%; background: {'#4CAF50' if total_coverage >= 80 else '#ff9800' if total_coverage >= 60 else '#f44336'}; 
                          width: {total_coverage}%; transition: width 0.3s ease; }}
        .file-list {{ margin-top: 20px; }}
        .file-item {{ padding: 8px; border-bottom: 1px solid #eee; }}
        .status-good {{ color: #4CAF50; }}
        .status-ok {{ color: #ff9800; }}
        .status-poor {{ color: #f44336; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 AI Quiz Platform - Unit Testing Coverage</h1>
        <p>Comprehensive test coverage analysis for Day 31: Unit Testing Services</p>
    </div>
    
    <div class="metrics">
        <div class="metric">
            <h3>Overall Coverage</h3>
            <div class="coverage-bar">
                <div class="coverage-fill"></div>
            </div>
            <p><strong>{total_coverage:.1f}%</strong></p>
        </div>
        
        <div class="metric">
            <h3>Lines Covered</h3>
            <p><strong>{coverage_data['totals']['covered_lines']}</strong> of {coverage_data['totals']['num_statements']}</p>
        </div>
        
        <div class="metric">
            <h3>Test Status</h3>
            <p class="{'status-good' if total_coverage >= 80 else 'status-ok' if total_coverage >= 60 else 'status-poor'}">
                {'✅ Target Achieved' if total_coverage >= 80 else '⚠️ Needs Improvement' if total_coverage >= 60 else '❌ Below Target'}
            </p>
        </div>
    </div>
    
    <div class="file-list">
        <h2>📁 File Coverage Details</h2>
        <p><a href="htmlcov/index.html" target="_blank">View Detailed HTML Coverage Report</a></p>
        
        <h3>Quick Actions</h3>
        <ul>
            <li><a href="#" onclick="alert('Run: pytest tests/unit/ -v')">Run All Tests</a></li>
            <li><a href="#" onclick="alert('Run: pytest tests/unit/test_quiz_service.py -v')">Test Quiz Service</a></li>
            <li><a href="#" onclick="alert('Run: pytest tests/unit/test_ai_service.py -v')">Test AI Service</a></li>
            <li><a href="#" onclick="alert('Run: pytest tests/unit/ --cov=src --cov-report=html')">Update Coverage</a></li>
        </ul>
    </div>
    
    <div style="margin-top: 40px; padding: 20px; background: #f9f9f9; border-radius: 5px;">
        <h3>🚀 Next Steps</h3>
        <ul>
            <li>Maintain 80%+ coverage on core business logic</li>
            <li>Add integration tests for Day 32</li>
            <li>Implement automated test pipeline</li>
            <li>Add performance regression tests</li>
        </ul>
    </div>
    
    <script>
        // Auto-refresh every 30 seconds if tests are running
        setTimeout(function() {{
            location.reload();
        }}, 30000);
    </script>
</body>
</html>
'''
    
    # Write dashboard HTML
    with open('coverage_dashboard.html', 'w') as f:
        f.write(html_content)
    
    return 'coverage_dashboard.html'

if __name__ == "__main__":
    dashboard_file = create_dashboard_html()
    if dashboard_file:
        print(f"Coverage dashboard created: {dashboard_file}")
        
        # Start simple HTTP server
        PORT = 8080
        Handler = http.server.SimpleHTTPRequestHandler
        
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            print(f"Dashboard server running at http://localhost:{PORT}")
            print(f"Opening dashboard...")
            
            # Try to open browser
            try:
                webbrowser.open(f'http://localhost:{PORT}/coverage_dashboard.html')
            except:
                print("Please open http://localhost:8080/coverage_dashboard.html in your browser")
            
            print("Press Ctrl+C to stop server")
            httpd.serve_forever()
DASHBOARD
    
    # Run dashboard
    python3 coverage_dashboard.py
}

# Main execution
main() {
    echo "🎯 AI Quiz Platform Unit Testing Demo"
    
    # Check if build was completed
    if [ ! -d "venv" ] && [ ! -f "requirements.txt" ]; then
        echo "❌ Please run ./build.sh first to set up the environment"
        exit 1
    fi
    
    # Show options if not specified
    if [ -z "$START_OPTION" ]; then
        show_options
    fi
    
    case $START_OPTION in
        1)
            run_test_suite
            ;;
        2)
            start_dev_server
            ;;
        3)
            interactive_test_exploration
            ;;
        4)
            start_coverage_dashboard
            ;;
        *)
            echo "Invalid option selected"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
