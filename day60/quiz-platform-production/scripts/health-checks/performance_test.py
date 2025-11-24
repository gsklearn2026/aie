from locust import HttpUser, task, between
import random

class QuizPlatformUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Register and login
        username = f"user_{random.randint(1000, 9999)}"
        response = self.client.post("/api/auth/register", json={
            "username": username,
            "email": f"{username}@test.com",
            "password": "test123"
        })
        self.token = response.json()["access_token"]
    
    @task(3)
    def generate_quiz(self):
        topics = ["Python", "JavaScript", "AI", "Databases", "DevOps"]
        self.client.post("/api/quiz/generate",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "topic": random.choice(topics),
                "difficulty": random.choice(["easy", "medium", "hard"]),
                "num_questions": 5
            }
        )
    
    @task(1)
    def view_leaderboard(self):
        self.client.get("/api/leaderboard/")
    
    @task(1)
    def health_check(self):
        self.client.get("/api/health")
