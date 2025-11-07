from locust import HttpUser, task, between
import random

class QuizAPIUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def get_quizzes(self):
        self.client.get("/api/quizzes?limit=10")
    
    @task(2)
    def get_quiz_detail(self):
        quiz_id = random.randint(1, 3)
        self.client.get(f"/api/quiz/{quiz_id}")
    
    @task(1)
    def get_quiz_with_fields(self):
        self.client.get("/api/quizzes?fields=id,title&limit=10")
    
    @task(1)
    def get_metrics(self):
        self.client.get("/api/metrics/performance")
