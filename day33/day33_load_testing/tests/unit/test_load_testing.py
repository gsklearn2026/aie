import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

from load_tests.quiz_platform_load_test import QuizPlatformUser
from utils.performance_analyzer import PerformanceAnalyzer
import tempfile
import pandas as pd

class TestLoadTesting:
    
    def test_quiz_platform_user_initialization(self):
        """Test QuizPlatformUser initializes correctly"""
        user = QuizPlatformUser()
        assert hasattr(user, 'wait_time')
        assert hasattr(user, 'on_start')
    
    def test_performance_analyzer_empty_data(self):
        """Test PerformanceAnalyzer handles empty data gracefully"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            # Create empty file
            pass
        
        analyzer = PerformanceAnalyzer(f.name)
        bottlenecks = analyzer.identify_bottlenecks()
        assert isinstance(bottlenecks, dict)
        
        os.unlink(f.name)
    
    def test_performance_analyzer_with_data(self):
        """Test PerformanceAnalyzer processes data correctly"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("2024-01-01 10:00:00,10,50.0,0,200.0\n")
            f.write("2024-01-01 10:01:00,20,45.0,1,250.0\n")
            f.write("2024-01-01 10:02:00,30,40.0,2,300.0\n")
        
        analyzer = PerformanceAnalyzer(f.name)
        assert len(analyzer.df) == 3
        
        report = analyzer.generate_report()
        assert "PERFORMANCE REPORT" in report
        assert "SUMMARY STATISTICS" in report
        
        os.unlink(f.name)
    
    def test_bottleneck_detection_high_response_time(self):
        """Test bottleneck detection for high response times"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("2024-01-01 10:00:00,10,50.0,0,1500.0\n")  # High response time
        
        analyzer = PerformanceAnalyzer(f.name)
        bottlenecks = analyzer.identify_bottlenecks()
        
        assert 'high_response_time' in bottlenecks
        assert bottlenecks['high_response_time']['severity'] == 'HIGH'
        
        os.unlink(f.name)

if __name__ == "__main__":
    pytest.main([__file__])
