from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from faker import Faker
import random
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import SessionLocal
from app.models.quiz_models import QuizResult, QuestionAnalytics

fake = Faker()

def generate_sample_data():
    """Generate sample quiz data for testing"""
    db = SessionLocal()
    
    try:
        # Clear existing data
        db.query(QuizResult).delete()
        db.query(QuestionAnalytics).delete()
        
        # Generate quiz results
        subjects = ['Mathematics', 'Science', 'History', 'Literature', 'Geography']
        difficulties = ['Easy', 'Medium', 'Hard']
        learning_patterns = ['Visual', 'Auditory', 'Kinesthetic', 'Reading/Writing']
        
        print("Generating quiz results...")
        for i in range(1000):
            result = QuizResult(
                user_id=f"user_{random.randint(1, 100)}",
                quiz_id=f"quiz_{random.randint(1, 50)}",
                score=round(random.uniform(40, 100), 2),
                total_questions=random.randint(10, 50),
                correct_answers=random.randint(5, 45),
                time_taken=random.randint(300, 3600),  # 5 minutes to 1 hour
                difficulty_level=random.choice(difficulties),
                subject_area=random.choice(subjects),
                ai_difficulty_prediction=round(random.uniform(1, 10), 2),
                learning_pattern=random.choice(learning_patterns),
                improvement_areas=fake.sentence(),
                completed_at=fake.date_time_between(start_date='-30d', end_date='now')
            )
            db.add(result)
            
            if i % 100 == 0:
                print(f"Generated {i} quiz results...")
        
        # Generate question analytics
        print("Generating question analytics...")
        for i in range(500):
            analytics = QuestionAnalytics(
                question_id=f"q_{random.randint(1, 200)}",
                quiz_id=f"quiz_{random.randint(1, 50)}",
                correct_rate=round(random.uniform(0.3, 0.95), 3),
                avg_time_spent=round(random.uniform(30, 300), 2),
                difficulty_rating=round(random.uniform(1, 10), 2),
                ai_complexity_score=round(random.uniform(1, 10), 2),
                common_mistakes=fake.sentence()
            )
            db.add(analytics)
        
        db.commit()
        print("Sample data generated successfully!")
        
    except Exception as e:
        print(f"Error generating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    generate_sample_data()
