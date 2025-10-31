import streamlit as st
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import psutil
import sqlite3
import redis
import time
import sys
from datetime import datetime, timedelta
import json
import os

# Page config
st.set_page_config(page_title="Quiz Platform Performance Monitor", 
                   page_icon="📊", layout="wide")

class PerformanceMonitor:
    def __init__(self):
        self.redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
        self.db_path = 'quiz_platform.db'
    
    def get_system_metrics(self):
        """Get current system performance metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'active_connections': len(psutil.net_connections())
        }
    
    def get_load_test_metrics(self):
        """Parse load test results from log files"""
        metrics = []
        
        try:
            with open('reports/performance_metrics.log', 'r') as f:
                lines = f.readlines()
                
                # Skip header row and empty lines
                for line in lines:
                    line = line.strip()
                    if not line or line.startswith('timestamp,users,rps,failures,avg_response_time'):
                        continue
                        
                    parts = line.split(',')
                    # Handle both old format (5 columns) and new format (7 columns)
                    if len(parts) >= 5:
                        try:
                            metric = {
                                'timestamp': parts[0],
                                'users': int(parts[1]),
                                'rps': float(parts[2]),
                                'failures': int(parts[3]),
                                'avg_response_time': float(parts[4])
                            }
                            
                            # Add optional columns if they exist
                            if len(parts) >= 7:
                                metric['cpu_percent'] = float(parts[5])
                                metric['memory_percent'] = float(parts[6])
                            
                            metrics.append(metric)
                        except ValueError:
                            # Skip invalid data lines
                            continue
                            
        except FileNotFoundError:
            st.warning("No load test metrics found. Run load tests first.")
        
        return pd.DataFrame(metrics)
    
    def get_database_metrics(self):
        """Get database performance metrics"""
        try:
            # Check if database file exists
            if not os.path.exists(self.db_path):
                return {"error": "Database file not found"}
            
            conn = sqlite3.connect(self.db_path)
            
            # Query execution stats with error handling
            queries = [
                "SELECT COUNT(*) as total_users FROM users",
                "SELECT COUNT(*) as total_quizzes FROM quizzes", 
                "SELECT COUNT(*) as active_sessions FROM quiz_sessions WHERE status='active'"
            ]
            
            metrics = {}
            for query in queries:
                try:
                    result = conn.execute(query).fetchone()
                    key = query.split('as ')[1].split(' FROM')[0]
                    metrics[key] = result[0]
                except sqlite3.OperationalError as e:
                    # Table doesn't exist
                    key = query.split('as ')[1].split(' FROM')[0]
                    metrics[key] = 0
            
            conn.close()
            return metrics
            
        except Exception as e:
            return {"error": f"Database connection error: {e}"}

# Initialize monitor
monitor = PerformanceMonitor()

# Dashboard header
st.title("🚀 Quiz Platform Performance Dashboard")
st.markdown("Real-time monitoring for load testing and system performance")

# Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Metrics", "🔥 Load Testing", "💾 Database", "⚙️ System Health"])

# Tab 1: Live Metrics
with tab1:
    col1, col2, col3, col4 = st.columns(4)
    
    system_metrics = monitor.get_system_metrics()
    
    with col1:
        st.metric("CPU Usage", f"{system_metrics['cpu_percent']}%", 
                 delta=None, delta_color="inverse")
    
    with col2:
        st.metric("Memory Usage", f"{system_metrics['memory_percent']}%",
                 delta=None, delta_color="inverse")
    
    with col3:
        st.metric("Disk Usage", f"{system_metrics['disk_usage']}%",
                 delta=None, delta_color="inverse")
    
    with col4:
        st.metric("Active Connections", system_metrics['active_connections'])
    
    # Auto-refresh every 5 seconds
    if st.button("🔄 Refresh Metrics"):
        st.rerun()

# Tab 2: Load Testing Results
with tab2:
    load_metrics_df = monitor.get_load_test_metrics()
    
    if not load_metrics_df.empty:
        # Convert timestamp to datetime for better plotting
        load_metrics_df['timestamp'] = pd.to_datetime(load_metrics_df['timestamp'])
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Peak Users", load_metrics_df['users'].max())
        
        with col2:
            st.metric("Peak RPS", f"{load_metrics_df['rps'].max():.1f}")
        
        with col3:
            st.metric("Avg Response Time", f"{load_metrics_df['avg_response_time'].mean():.1f}ms")
        
        with col4:
            st.metric("Total Failures", load_metrics_df['failures'].sum())
        
        # Response time chart
        fig_response_time = px.line(load_metrics_df, x='timestamp', y='avg_response_time',
                                   title='Average Response Time Over Time',
                                   labels={'avg_response_time': 'Response Time (ms)', 'timestamp': 'Time'})
        st.plotly_chart(fig_response_time, use_container_width=True)
        
        # Requests per second
        fig_rps = px.line(load_metrics_df, x='timestamp', y='rps',
                         title='Requests Per Second',
                         labels={'rps': 'RPS', 'timestamp': 'Time'})
        st.plotly_chart(fig_rps, use_container_width=True)
        
        # User load vs failures
        fig_failures = px.scatter(load_metrics_df, x='users', y='failures',
                                 size='avg_response_time', 
                                 title='User Load vs Failures',
                                 labels={'users': 'Concurrent Users', 'failures': 'Failures'})
        st.plotly_chart(fig_failures, use_container_width=True)
        
        # System metrics if available
        if 'cpu_percent' in load_metrics_df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                fig_cpu = px.line(load_metrics_df, x='timestamp', y='cpu_percent',
                                 title='CPU Usage Over Time',
                                 labels={'cpu_percent': 'CPU %', 'timestamp': 'Time'})
                st.plotly_chart(fig_cpu, use_container_width=True)
            
            with col2:
                fig_memory = px.line(load_metrics_df, x='timestamp', y='memory_percent',
                                   title='Memory Usage Over Time',
                                   labels={'memory_percent': 'Memory %', 'timestamp': 'Time'})
                st.plotly_chart(fig_memory, use_container_width=True)
        
        # Show latest metrics table
        st.subheader("📋 Latest Test Results")
        display_df = load_metrics_df[['timestamp', 'users', 'rps', 'failures', 'avg_response_time']].tail(10)
        st.dataframe(display_df, use_container_width=True)
    
    else:
        st.info("No load testing data available. Run load tests to see results here.")
        st.info("💡 You can generate sample data by running: `python src/utils/metrics_collector.py`")

# Tab 3: Database Performance
with tab3:
    db_metrics = monitor.get_database_metrics()
    
    if "error" in db_metrics:
        st.error(f"❌ {db_metrics['error']}")
        st.info("💡 This is normal if no quiz platform database has been created yet.")
        
        # Show sample database structure
        st.subheader("📋 Expected Database Schema")
        st.code("""
        Tables:
        - users (id, username, email, created_at)
        - quizzes (id, title, description, created_at)
        - quiz_sessions (id, user_id, quiz_id, status, started_at)
        """, language="sql")
        
    elif db_metrics:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Users", db_metrics.get('total_users', 0))
        
        with col2:
            st.metric("Total Quizzes", db_metrics.get('total_quizzes', 0))
        
        with col3:
            st.metric("Active Sessions", db_metrics.get('active_sessions', 0))
        
        # Connection pool status
        st.subheader("🔗 Database Connection Health")
        st.success("Database connections: Normal")
    
    else:
        st.error("Unable to connect to database")

# Tab 4: System Health
with tab4:
    st.subheader("🏥 System Health Check")
    
    # Service status checks
    services = {
        "Quiz API": "http://localhost:8000/health",
        "Redis Cache": os.getenv('REDIS_URL', 'redis://localhost:6379'),
        "Database": "sqlite:///quiz_platform.db"
    }
    
    for service, endpoint in services.items():
        try:
            if "redis" in str(endpoint):
                try:
                    monitor.redis_client.ping()
                    st.success(f"✅ {service}: Online")
                except Exception:
                    st.warning(f"⚠️ {service}: Not running (Redis server not started)")
            elif "sqlite" in str(endpoint):
                if os.path.exists('quiz_platform.db'):
                    conn = sqlite3.connect('quiz_platform.db')
                    conn.execute("SELECT 1")
                    conn.close()
                    st.success(f"✅ {service}: Online")
                else:
                    st.info(f"ℹ️ {service}: Database file not found (normal for load testing)")
            else:
                import requests
                try:
                    response = requests.get(endpoint, timeout=3)
                    if response.status_code == 200:
                        st.success(f"✅ {service}: Online")
                    else:
                        st.warning(f"⚠️ {service}: Responding but status {response.status_code}")
                except requests.exceptions.ConnectionError:
                    st.warning(f"⚠️ {service}: Not running (expected for load testing)")
                except Exception as e:
                    st.warning(f"⚠️ {service}: Connection error - {str(e)}")
        
        except Exception as e:
            st.warning(f"⚠️ {service}: Check failed - {str(e)}")
    
    # Additional system info
    st.subheader("📊 System Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Python Version", f"{sys.version.split()[0]}")
        st.metric("Streamlit Version", st.__version__)
    
    with col2:
        st.metric("Working Directory", os.getcwd())
        st.metric("Load Test Reports", "Available" if os.path.exists('reports/') else "Not found")

# Auto-refresh the dashboard
if st.checkbox("🔄 Auto-refresh (5s)"):
    time.sleep(5)
    st.rerun()
