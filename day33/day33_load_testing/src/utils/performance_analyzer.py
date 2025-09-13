import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime
import sqlite3

class PerformanceAnalyzer:
    """Analyzes load test results and identifies bottlenecks"""
    
    def __init__(self, metrics_file='reports/performance_metrics.log'):
        self.metrics_file = metrics_file
        self.load_data()
    
    def load_data(self):
        """Load performance metrics from log file"""
        try:
            self.df = pd.read_csv(self.metrics_file, 
                                 names=['timestamp', 'users', 'rps', 'failures', 'avg_response_time'])
            
            # Check if we have actual data (not just headers)
            if len(self.df) == 0 or (len(self.df) == 1 and self.df.iloc[0]['timestamp'] == 'timestamp'):
                print("No performance data found. Run load tests first.")
                self.df = pd.DataFrame()
                return
            
            # Convert timestamp column to datetime
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
        except FileNotFoundError:
            print("No performance data found. Run load tests first.")
            self.df = pd.DataFrame()
        except Exception as e:
            print(f"Error loading performance data: {e}")
            self.df = pd.DataFrame()
    
    def identify_bottlenecks(self):
        """Identify performance bottlenecks from test data"""
        if self.df.empty:
            return {}
        
        bottlenecks = {}
        
        # Response time analysis
        if self.df['avg_response_time'].max() > 1000:  # >1 second
            bottlenecks['high_response_time'] = {
                'severity': 'HIGH',
                'max_response_time': self.df['avg_response_time'].max(),
                'recommendation': 'Optimize database queries and add caching'
            }
        
        # Failure rate analysis  
        failure_rate = (self.df['failures'].sum() / len(self.df)) * 100
        if failure_rate > 5:
            bottlenecks['high_failure_rate'] = {
                'severity': 'CRITICAL',
                'failure_rate': failure_rate,
                'recommendation': 'Check error logs and fix failing endpoints'
            }
        
        # Throughput degradation
        if len(self.df) > 10:
            early_rps = self.df.head(5)['rps'].mean()
            late_rps = self.df.tail(5)['rps'].mean()
            
            if (early_rps - late_rps) / early_rps > 0.2:  # >20% degradation
                bottlenecks['throughput_degradation'] = {
                    'severity': 'MEDIUM',
                    'degradation_percent': ((early_rps - late_rps) / early_rps) * 100,
                    'recommendation': 'Check for memory leaks and connection pool exhaustion'
                }
        
        return bottlenecks
    
    def generate_report(self):
        """Generate comprehensive performance report"""
        if self.df.empty:
            return "No data available for analysis"
        
        report = f"""
🚀 QUIZ PLATFORM PERFORMANCE REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 SUMMARY STATISTICS
- Total Test Duration: {(self.df['timestamp'].max() - self.df['timestamp'].min()).seconds} seconds
- Peak Concurrent Users: {self.df['users'].max()}
- Average Response Time: {self.df['avg_response_time'].mean():.1f}ms
- Peak RPS: {self.df['rps'].max():.1f}
- Total Failures: {self.df['failures'].sum()}

🔍 BOTTLENECK ANALYSIS
"""
        
        bottlenecks = self.identify_bottlenecks()
        
        if not bottlenecks:
            report += "✅ No major bottlenecks identified\n"
        else:
            for issue, details in bottlenecks.items():
                report += f"\n❌ {issue.replace('_', ' ').title()}\n"
                report += f"   Severity: {details['severity']}\n"
                report += f"   Recommendation: {details['recommendation']}\n"
        
        report += f"""
📈 PERFORMANCE TRENDS
- Response Time Trend: {self._calculate_trend('avg_response_time')}
- Throughput Trend: {self._calculate_trend('rps')}
- Error Rate Trend: {self._calculate_trend('failures')}

🎯 OPTIMIZATION RECOMMENDATIONS
1. Implement Redis caching for frequent database queries
2. Optimize Gemini API call batching 
3. Add database connection pooling
4. Configure auto-scaling based on CPU/Memory thresholds
"""
        
        return report
    
    def _calculate_trend(self, column):
        """Calculate trend direction for a metric"""
        if len(self.df) < 2:
            return "Insufficient data"
        
        slope = np.polyfit(range(len(self.df)), self.df[column], 1)[0]
        
        if slope > 0.1:
            return "📈 Increasing"
        elif slope < -0.1:
            return "📉 Decreasing" 
        else:
            return "➡️ Stable"
    
    def save_report(self, filename='reports/performance_analysis.txt'):
        """Save performance report to file"""
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            f.write(report)
        
        print(f"Performance report saved to {filename}")
        return report

if __name__ == "__main__":
    analyzer = PerformanceAnalyzer()
    report = analyzer.save_report()
    print(report)
