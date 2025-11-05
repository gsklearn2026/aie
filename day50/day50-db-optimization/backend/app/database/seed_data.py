from sqlalchemy.orm import Session
from ..models.models import User, Quiz, Question, QuizAttempt
from passlib.context import CryptContext
from datetime import datetime, timedelta
import random
import hashlib

# Initialize password context with fallback
try:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
except Exception:
    # Fallback to simple hash if bcrypt fails
    pwd_context = None

def _hash_password(password: str) -> str:
    """Hash password with fallback"""
    if pwd_context:
        try:
            return pwd_context.hash(password)
        except Exception:
            pass
    # Fallback to simple hash
    return hashlib.sha256(password.encode()).hexdigest()

def seed_database(db: Session):
    """Seed database with test data"""
    
    # Check if data exists
    if db.query(User).count() > 0:
        print("Database already seeded")
        return
    
    print("Seeding database...")
    
    # Create users
    users = []
    for i in range(10):
        user = User(
            email=f"user{i}@test.com",
            username=f"user{i}",
            hashed_password=_hash_password("password123")
        )
        users.append(user)
        db.add(user)
    
    db.commit()
    
    # Create quizzes
    categories = ["Python", "JavaScript", "Databases", "AI/ML", "DevOps"]
    difficulties = ["easy", "medium", "hard"]
    
    quizzes = []
    for i in range(20):
        quiz = Quiz(
            title=f"Quiz {i+1}: {random.choice(categories)}",
            description=f"Test your knowledge of {random.choice(categories)}",
            category=random.choice(categories),
            difficulty=random.choice(difficulties),
            created_by=users[0].id
        )
        quizzes.append(quiz)
        db.add(quiz)
    
    db.commit()
    
    # Create questions
    for quiz in quizzes:
        for j in range(5):
            question = Question(
                quiz_id=quiz.id,
                question_text=f"Question {j+1} for {quiz.title}?",
                option_a="Option A",
                option_b="Option B",
                option_c="Option C",
                option_d="Option D",
                correct_answer=random.choice(['A', 'B', 'C', 'D']),
                explanation="Explanation text here"
            )
            db.add(question)
    
    db.commit()
    
    # Create quiz attempts
    for user in users:
        for _ in range(random.randint(3, 10)):
            quiz = random.choice(quizzes)
            attempt = QuizAttempt(
                user_id=user.id,
                quiz_id=quiz.id,
                score=random.uniform(50, 100),
                total_questions=5,
                time_taken=random.randint(60, 300),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            db.add(attempt)
    
    db.commit()
    print("Database seeded successfully!")
