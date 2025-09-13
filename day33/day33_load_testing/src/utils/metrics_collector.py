#!/usr/bin/env python3
"""
Metrics Collector for Load Testing
Captures real-time performance metrics during load tests
"""

import time
import json
import csv
import os
from datetime import datetime
import psutil
import requests
from typing import Dict, List

class MetricsCollector:
    """Collects and stores performance metrics during load testing"""
    
    def __init__(self, metrics_file='reports/performance_metrics.log'):
        self.metrics_file = metrics_file
        self.ensure_reports_dir()
        self.initialize_metrics_file()
    
    def ensure_reports_dir(self):
        """Ensure reports directory exists"""
        os.makedirs('reports', exist_ok=True)
    
    def initialize_metrics_file(self):
        """Initialize metrics file with headers if it doesn't exist"""
        if not os.path.exists(self.metrics_file):
            with open(self.metrics_file, 'w') as f:
                f.write('timestamp,users,rps,failures,avg_response_time,cpu_percent,memory_percent\n')
    
    def collect_system_metrics(self) -> Dict:
        """Collect current system performance metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'timestamp': datetime.now().isoformat()
        }
    
    def collect_load_test_metrics(self, users: int, rps: float, failures: int, avg_response_time: float):
        """Collect load test specific metrics"""
        system_metrics = self.collect_system_metrics()
        
        metrics = {
            'timestamp': system_metrics['timestamp'],
            'users': users,
            'rps': rps,
            'failures': failures,
            'avg_response_time': avg_response_time,
            'cpu_percent': system_metrics['cpu_percent'],
            'memory_percent': system_metrics['memory_percent']
        }
        
        self.save_metrics(metrics)
        return metrics
    
    def save_metrics(self, metrics: Dict):
        """Save metrics to CSV file"""
        with open(self.metrics_file, 'a') as f:
            writer = csv.writer(f)
            writer.writerow([
                metrics['timestamp'],
                metrics['users'],
                metrics['rps'],
                metrics['failures'],
                metrics['avg_response_time'],
                metrics['cpu_percent'],
                metrics['memory_percent']
            ])
    
    def generate_sample_data(self):
        """Generate sample metrics data for demonstration"""
        print("📊 Generating sample load test data...")
        
        # Clear existing data
        with open(self.metrics_file, 'w') as f:
            f.write('timestamp,users,rps,failures,avg_response_time,cpu_percent,memory_percent\n')
        
        # Generate sample data over 30 seconds
        base_time = datetime.now()
        for i in range(30):
            timestamp = (base_time.timestamp() + i) * 1000  # milliseconds
            users = min(5, i // 6)  # Ramp up to 5 users
            rps = max(0.5, users * 1.5 + (i % 3) * 0.5)  # Simulate RPS
            failures = max(0, int(users * 0.1 * (i % 4)))  # Some failures
            avg_response_time = max(50, 200 - users * 20 + (i % 5) * 10)  # Response time
            cpu_percent = min(100, 20 + users * 5 + (i % 3) * 2)
            memory_percent = min(100, 30 + users * 3 + (i % 2) * 1)
            
            metrics = {
                'timestamp': datetime.fromtimestamp(timestamp / 1000).isoformat(),
                'users': users,
                'rps': rps,
                'failures': failures,
                'avg_response_time': avg_response_time,
                'cpu_percent': cpu_percent,
                'memory_percent': memory_percent
            }
            
            self.save_metrics(metrics)
        
        print(f"✅ Generated sample data in {self.metrics_file}")
    
    def get_latest_metrics(self, count: int = 100) -> List[Dict]:
        """Get latest metrics from file"""
        metrics = []
        try:
            with open(self.metrics_file, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                for row in rows[-count:]:  # Last N entries
                    try:
                        metrics.append({
                            'timestamp': row['timestamp'],
                            'users': int(row['users']),
                            'rps': float(row['rps']),
                            'failures': int(row['failures']),
                            'avg_response_time': float(row['avg_response_time']),
                            'cpu_percent': float(row.get('cpu_percent', 0)),
                            'memory_percent': float(row.get('memory_percent', 0))
                        })
                    except (ValueError, KeyError):
                        continue
        except FileNotFoundError:
            pass
        
        return metrics

if __name__ == "__main__":
    collector = MetricsCollector()
    collector.generate_sample_data()
    print("Sample metrics generated successfully!")
