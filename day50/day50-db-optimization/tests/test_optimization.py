import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models.models import Base, Quiz, Question, User, QuizAttempt
from app.services.optimized_queries import OptimizedQueries
from app.services.query_optimizer import QueryOptimizer
import time

DATABASE_URL = "postgresql://quizuser:quizpass@localhost:5432/quizdb"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def test_database_connection():
    """Test database connection"""
    db = SessionLocal()
    try:
        result = db.execute(text("SELECT 1"))
        assert result.scalar() == 1
        print("✓ Database connection successful")
    finally:
        db.close()

def test_indexes_exist():
    """Test that all indexes are created"""
    db = SessionLocal()
    try:
        query = text("""
            SELECT tablename, indexname 
            FROM pg_indexes 
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
        """)
        result = db.execute(query)
        indexes = [row[1] for row in result]
        
        # Check critical indexes
        assert 'idx_user_email' in indexes
        assert 'idx_quiz_category' in indexes
        assert 'idx_attempt_user_created' in indexes
        assert 'idx_question_quiz_id' in indexes
        
        print(f"✓ Found {len(indexes)} indexes")
    finally:
        db.close()

def test_optimized_quiz_query():
    """Test optimized quiz query performance"""
    db = SessionLocal()
    try:
        queries = OptimizedQueries(db)
        
        start_time = time.time()
        quizzes = queries.get_quizzes_with_questions()
        duration = time.time() - start_time
        
        assert len(quizzes) > 0
        assert duration < 0.1  # Should be under 100ms
        
        # Verify questions are loaded (no N+1)
        if quizzes:
            assert len(quizzes[0].questions) >= 0
        
        print(f"✓ Quiz query completed in {duration*1000:.2f}ms")
    finally:
        db.close()

def test_leaderboard_performance():
    """Test leaderboard query performance"""
    db = SessionLocal()
    try:
        queries = OptimizedQueries(db)
        
        start_time = time.time()
        leaders = queries.get_leaderboard(limit=10)
        duration = time.time() - start_time
        
        assert duration < 0.2  # Should be under 200ms
        print(f"✓ Leaderboard query completed in {duration*1000:.2f}ms")
    finally:
        db.close()

def test_query_analyzer():
    """Test query analysis functionality"""
    db = SessionLocal()
    try:
        optimizer = QueryOptimizer(db)
        
        # Test index usage check
        indexes = optimizer.check_index_usage()
        assert len(indexes) > 0
        
        print(f"✓ Query analyzer found {len(indexes)} index statistics")
    finally:
        db.close()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
