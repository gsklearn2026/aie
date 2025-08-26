import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..models.relationship import Base, Topic, TopicRelationship
from ..models.schemas import TopicCreate, RelationshipCreate
from ..services.relationship_service import RelationshipService

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def relationship_service():
    return RelationshipService()

@pytest.mark.asyncio
async def test_create_topic(db, relationship_service):
    topic_data = TopicCreate(
        name="Linear Algebra",
        description="Mathematical foundations",
        category="Mathematics",
        difficulty_level=3
    )
    
    topic = await relationship_service.create_topic(db, topic_data)
    assert topic.name == "Linear Algebra"
    assert topic.difficulty_level == 3

@pytest.mark.asyncio
async def test_create_relationship(db, relationship_service):
    # Create topics first
    topic1_data = TopicCreate(name="Basic Math", category="Mathematics", difficulty_level=1)
    topic2_data = TopicCreate(name="Algebra", category="Mathematics", difficulty_level=2)
    
    topic1 = await relationship_service.create_topic(db, topic1_data)
    topic2 = await relationship_service.create_topic(db, topic2_data)
    
    # Create relationship
    rel_data = RelationshipCreate(
        source_topic_id=topic1.id,
        target_topic_id=topic2.id,
        relationship_type="prerequisite",
        strength=0.9
    )
    
    relationship = await relationship_service.create_relationship(db, rel_data)
    assert relationship.relationship_type == "prerequisite"
    assert relationship.strength == 0.9

@pytest.mark.asyncio
async def test_get_related_topics(db, relationship_service):
    # Create test data
    topic1_data = TopicCreate(name="Programming Basics", category="CS", difficulty_level=1)
    topic2_data = TopicCreate(name="Object Oriented Programming", category="CS", difficulty_level=2)
    
    topic1 = await relationship_service.create_topic(db, topic1_data)
    topic2 = await relationship_service.create_topic(db, topic2_data)
    
    rel_data = RelationshipCreate(
        source_topic_id=topic1.id,
        target_topic_id=topic2.id,
        relationship_type="prerequisite",
        strength=0.8
    )
    
    await relationship_service.create_relationship(db, rel_data)
    
    # Test getting related topics
    related = await relationship_service.get_related_topics(db, topic1.id)
    assert related["topic_id"] == topic1.id
    assert len(related["relationships"]) > 0
