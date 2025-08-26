import pytest
from sqlalchemy.orm import Session
from app.services.path_generator import LearningPathGenerator
from app.models.learning_path import Topic, User, UserProgress, TopicRelationship
from app.database.connection import SessionLocal, engine
import networkx as nx

@pytest.fixture
def db_session():
    """Create test database session"""
    from app.models.learning_path import Base
    Base.metadata.create_all(bind=engine)
    
    session = SessionLocal()
    yield session
    
    # Clean up after each test
    session.rollback()
    session.close()

@pytest.fixture
def sample_topics(db_session):
    """Create sample topics for testing"""
    # Clean up any existing data first
    db_session.query(TopicRelationship).delete()
    db_session.query(UserProgress).delete()
    db_session.query(Topic).delete()
    db_session.commit()
    
    topics = [
        Topic(name="Basics", difficulty_level=2.0, estimated_duration=60),
        Topic(name="Intermediate", difficulty_level=5.0, estimated_duration=90),
        Topic(name="Advanced", difficulty_level=8.0, estimated_duration=120)
    ]
    
    for topic in topics:
        db_session.add(topic)
    
    db_session.commit()
    
    # Add relationships
    rel = TopicRelationship(
        source_topic_id=topics[0].id, target_topic_id=topics[1].id, 
        relationship_type="prerequisite", strength=0.8
    )
    db_session.add(rel)
    
    db_session.commit()
    return topics

def test_path_generation_basic(db_session, sample_topics):
    """Test basic path generation"""
    generator = LearningPathGenerator(db_session)
    
    topic_ids = [topic.id for topic in sample_topics]
    result = generator.generate_personalized_path(
        user_id=1,
        target_topics=topic_ids
    )
    
    assert "topic_sequence" in result
    assert "estimated_duration" in result
    assert len(result["topic_sequence"]) == 3

def test_prerequisite_ordering(db_session, sample_topics):
    """Test that prerequisites are properly ordered"""
    generator = LearningPathGenerator(db_session)
    
    # Request in wrong order (Intermediate before Basics)
    topic_ids = [sample_topics[1].id, sample_topics[0].id]
    result = generator.generate_personalized_path(
        user_id=1,
        target_topics=topic_ids
    )
    
    # Should reorder to respect prerequisites
    sequence = result["topic_sequence"]
    assert sequence.index(sample_topics[0].id) < sequence.index(sample_topics[1].id)

def test_difficulty_progression(db_session, sample_topics):
    """Test difficulty progression constraints"""
    generator = LearningPathGenerator(db_session)
    
    topic_ids = [topic.id for topic in sample_topics]
    result = generator.generate_personalized_path(
        user_id=1,
        target_topics=topic_ids,
        max_difficulty_jump=3.0
    )
    
    difficulty_curve = result["difficulty_progression"]
    
    # Check that difficulty jumps are reasonable
    for i in range(1, len(difficulty_curve)):
        jump = difficulty_curve[i] - difficulty_curve[i-1]
        assert jump <= 3.0

def test_user_progress_integration(db_session, sample_topics):
    """Test integration with user progress data"""
    # Add user progress
    progress = UserProgress(
        user_id=1, topic_id=sample_topics[0].id, 
        mastery_level=0.9, completion_status="completed"
    )
    db_session.add(progress)
    db_session.commit()
    
    generator = LearningPathGenerator(db_session)
    topic_ids = [topic.id for topic in sample_topics]
    result = generator.generate_personalized_path(
        user_id=1,
        target_topics=topic_ids
    )
    
    # Should account for existing progress
    assert result["completion_probability"] > 0.5

def test_collaborative_filtering(db_session, sample_topics):
    """Test collaborative filtering enhancement"""
    from app.services.path_generator import CollaborativePathGenerator
    
    generator = CollaborativePathGenerator(db_session)
    topic_ids = [topic.id for topic in sample_topics]
    result = generator.generate_collaborative_path(
        user_id=1,
        target_topics=topic_ids
    )
    
    assert "collaborative_insights" in result
    assert "similar_users_count" in result["collaborative_insights"]

def test_path_metrics_calculation(db_session, sample_topics):
    """Test path metrics calculation"""
    generator = LearningPathGenerator(db_session)
    
    topic_ids = [topic.id for topic in sample_topics]
    result = generator.generate_personalized_path(
        user_id=1,
        target_topics=topic_ids
    )
    
    metrics = result["path_analysis"]
    assert "prerequisite_coverage" in metrics
    assert "difficulty_balance" in metrics
    assert "knowledge_gaps" in metrics
    
    # Coverage should be between 0 and 1
    assert 0 <= metrics["prerequisite_coverage"] <= 1

if __name__ == "__main__":
    pytest.main([__file__])
