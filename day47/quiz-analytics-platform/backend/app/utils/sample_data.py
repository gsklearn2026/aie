from sqlalchemy.orm import Session
from app.database.connection import SessionLocal
from app.models.quiz import User, Quiz, Question, QuizSession, QuestionResponse
from datetime import datetime, timedelta
import random
import json

def create_sample_data():
    """Create sample data for testing and demonstration"""
    db = SessionLocal()
    
    try:
        # Create sample users
        users_data = [
            {"username": "alice_student", "email": "alice@example.com", "full_name": "Alice Johnson"},
            {"username": "bob_learner", "email": "bob@example.com", "full_name": "Bob Smith"},
            {"username": "carol_quiz", "email": "carol@example.com", "full_name": "Carol Davis"},
            {"username": "david_study", "email": "david@example.com", "full_name": "David Wilson"},
            {"username": "eve_practice", "email": "eve@example.com", "full_name": "Eve Brown"}
        ]
        
        users = []
        for user_data in users_data:
            existing = db.query(User).filter(User.username == user_data["username"]).first()
            if not existing:
                user = User(**user_data)
                db.add(user)
                db.flush()
                users.append(user)
            else:
                users.append(existing)
        
        # Create sample quizzes
        quizzes_data = [
            {
                "title": "Python Basics",
                "description": "Test your knowledge of Python fundamentals",
                "category": "Programming",
                "difficulty_level": "beginner",
                "total_questions": 10,
                "time_limit": 30
            },
            {
                "title": "Data Structures",
                "description": "Arrays, Lists, and Trees concepts",
                "category": "Computer Science",
                "difficulty_level": "intermediate",
                "total_questions": 15,
                "time_limit": 45
            },
            {
                "title": "Machine Learning Fundamentals",
                "description": "Basic ML concepts and algorithms",
                "category": "AI/ML",
                "difficulty_level": "intermediate",
                "total_questions": 12,
                "time_limit": 40
            }
        ]
        
        quizzes = []
        for quiz_data in quizzes_data:
            existing = db.query(Quiz).filter(Quiz.title == quiz_data["title"]).first()
            if not existing:
                quiz = Quiz(**quiz_data)
                db.add(quiz)
                db.flush()
                quizzes.append(quiz)
            else:
                quizzes.append(existing)
        
        # Create sample questions for each quiz
        questions_data = {
            "Python Basics": [
                {
                    "question_text": "What is the correct way to define a function in Python?",
                    "question_type": "multiple_choice",
                    "options": json.dumps(["function myFunc():", "def myFunc():", "define myFunc():", "func myFunc():"]),
                    "correct_answer": "def myFunc():",
                    "difficulty_score": 0.2,
                    "topic": "Functions"
                },
                {
                    "question_text": "Python is case-sensitive",
                    "question_type": "true_false",
                    "options": json.dumps(["True", "False"]),
                    "correct_answer": "True",
                    "difficulty_score": 0.1,
                    "topic": "Syntax"
                }
            ]
        }
        
        for quiz in quizzes:
            if quiz.title in questions_data:
                for q_data in questions_data[quiz.title]:
                    existing = db.query(Question).filter(
                        Question.quiz_id == quiz.id,
                        Question.question_text == q_data["question_text"]
                    ).first()
                    if not existing:
                        question = Question(quiz_id=quiz.id, **q_data)
                        db.add(question)
        
        # Create sample quiz sessions with random data
        for user in users:
            for quiz in quizzes:
                # Create 3-7 sessions per user per quiz
                num_sessions = random.randint(3, 7)
                for i in range(num_sessions):
                    # Random date within last 30 days
                    days_ago = random.randint(1, 30)
                    started_at = datetime.utcnow() - timedelta(days=days_ago)
                    completed_at = started_at + timedelta(minutes=random.randint(10, quiz.time_limit))
                    
                    # Random performance metrics
                    correct_answers = random.randint(3, quiz.total_questions)
                    score = (correct_answers / quiz.total_questions) * 100
                    time_taken = random.randint(600, quiz.time_limit * 60)  # seconds
                    
                    session = QuizSession(
                        user_id=user.id,
                        quiz_id=quiz.id,
                        started_at=started_at,
                        completed_at=completed_at,
                        score=score,
                        total_questions=quiz.total_questions,
                        correct_answers=correct_answers,
                        time_taken=time_taken,
                        is_completed=True
                    )
                    db.add(session)
        
        db.commit()
        print("Sample data created successfully!")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating sample data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
