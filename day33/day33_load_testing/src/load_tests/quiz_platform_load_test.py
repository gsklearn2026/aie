import random
import time
import json
import os
from locust import HttpUser, task, between
from locust.env import Environment
from locust.stats import stats_printer, stats_history
from locust.log import setup_logging
import google.generativeai as genai
from datetime import datetime

# Configure Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

class QuizPlatformUser(HttpUser):
    """Simulates realistic user behavior on Quiz Platform"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Initialize user session"""
        self.user_id = f"load_test_user_{random.randint(1000, 9999)}"
        self.current_quiz_id = None
        self.current_question_index = 0
        self.session_start = time.time()
        
        # Authenticate user
        self.login()
    
    def login(self):
        """User login simulation"""
        response = self.client.post("/api/auth/login", json={
            "username": self.user_id,
            "password": "test_password"
        })
        
        if response.status_code == 200:
            self.token = response.json().get('access_token')
            self.client.headers.update({'Authorization': f'Bearer {self.token}'})
    
    @task(3)
    def browse_quizzes(self):
        """Browse available quizzes - most common action"""
        with self.client.get("/api/quizzes", catch_response=True) as response:
            if response.status_code == 200:
                quizzes = response.json()
                if quizzes:
                    response.success()
                else:
                    response.failure("No quizzes available")
            else:
                response.failure(f"Failed to load quizzes: {response.status_code}")
    
    @task(2)
    def start_quiz(self):
        """Start a quiz session"""
        # Get available quizzes first
        response = self.client.get("/api/quizzes")
        if response.status_code == 200:
            quizzes = response.json()
            if quizzes:
                quiz = random.choice(quizzes)
                self.current_quiz_id = quiz['id']
                
                # Start quiz session
                start_response = self.client.post(f"/api/quizzes/{self.current_quiz_id}/start", 
                                                json={"user_id": self.user_id})
                
                if start_response.status_code == 201:
                    session_data = start_response.json()
                    self.session_id = session_data.get('session_id')
    
    @task(4)
    def answer_question(self):
        """Answer quiz questions - core functionality"""
        if not self.current_quiz_id:
            self.start_quiz()
            return
        
        # Get current question
        response = self.client.get(f"/api/quizzes/{self.current_quiz_id}/questions/{self.current_question_index}")
        
        if response.status_code == 200:
            question_data = response.json()
            
            # Simulate thinking time
            time.sleep(random.uniform(2, 8))
            
            # Generate AI-powered answer using Gemini (simulates real usage)
            try:
                model = genai.GenerativeModel('gemini-pro')
                ai_response = model.generate_content(f"Answer this question: {question_data['question']}")
                ai_answer = ai_response.text[:100]  # Truncate for load testing
            except:
                ai_answer = "Generated answer"
            
            # Submit answer
            answer_response = self.client.post(f"/api/quizzes/{self.current_quiz_id}/answers", json={
                "question_id": question_data['id'],
                "answer": random.choice(question_data.get('options', ['A', 'B', 'C', 'D'])),
                "ai_assistance": ai_answer,
                "time_taken": random.uniform(10, 60)
            })
            
            if answer_response.status_code == 200:
                self.current_question_index += 1
    
    @task(1)
    def get_leaderboard(self):
        """Check leaderboard - resource intensive"""
        response = self.client.get("/api/leaderboard")
        
        if response.status_code == 200:
            leaderboard = response.json()
            # Simulate user scrolling through results
            time.sleep(random.uniform(0.5, 2))
    
    @task(1) 
    def get_results(self):
        """Get quiz results and analytics"""
        if self.current_quiz_id:
            response = self.client.get(f"/api/quizzes/{self.current_quiz_id}/results")
            
            if response.status_code == 200:
                results = response.json()
                # Simulate user reviewing detailed results
                time.sleep(random.uniform(3, 8))

class StressTestUser(HttpUser):
    """Aggressive user for stress testing"""
    
    wait_time = between(0.1, 0.5)  # Very fast requests
    
    @task
    def rapid_fire_requests(self):
        """Rapid succession of requests to find breaking point"""
        endpoints = ["/api/quizzes", "/api/leaderboard", "/api/health"]
        endpoint = random.choice(endpoints)
        self.client.get(endpoint)

# Performance monitoring functions
def setup_performance_monitoring(environment):
    """Setup real-time performance monitoring"""
    
    def log_performance_metrics(environment, **kwargs):
        stats = environment.stats
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Log key metrics
        print(f"[{current_time}] Users: {environment.runner.user_count}, "
              f"RPS: {stats.total.current_rps:.1f}, "
              f"Failures: {stats.total.num_failures}, "
              f"Avg Response: {stats.total.avg_response_time:.1f}ms")
        
        # Save metrics to file for analysis
        with open('reports/performance_metrics.log', 'a') as f:
            f.write(f"{current_time},{environment.runner.user_count},"
                   f"{stats.total.current_rps},{stats.total.num_failures},"
                   f"{stats.total.avg_response_time}\n")
    
    # Setup periodic logging
    environment.events.request_success.add_listener(log_performance_metrics)
    environment.events.request_failure.add_listener(log_performance_metrics)

# Load testing scenarios
def run_baseline_test():
    """Run baseline performance test"""
    print("🔥 Running Baseline Load Test...")
    os.system(f"locust -f src/load_tests/quiz_platform_load_test.py --headless "
             f"-u 10 -r 2 -t 60s --host={os.getenv('QUIZ_API_BASE_URL')} "
             f"--html reports/baseline_test_report.html")

def run_stress_test():
    """Run stress test to find breaking point"""
    print("⚡ Running Stress Test...")
    os.system(f"locust -f src/load_tests/quiz_platform_load_test.py --headless "
             f"-u 500 -r 50 -t 300s --host={os.getenv('QUIZ_API_BASE_URL')} "
             f"--html reports/stress_test_report.html")

def run_spike_test():
    """Run spike test for sudden traffic increases"""
    print("📈 Running Spike Test...")
    os.system(f"locust -f src/load_tests/quiz_platform_load_test.py --headless "
             f"-u 1000 -r 100 -t 120s --host={os.getenv('QUIZ_API_BASE_URL')} "
             f"--html reports/spike_test_report.html")

if __name__ == "__main__":
    # Run different test scenarios
    run_baseline_test()
    time.sleep(30)  # Cool down period
    run_stress_test()
    time.sleep(30)
    run_spike_test()
