from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from ..config.settings import get_settings

settings = get_settings()

# Database URL - using SQLite for demo, PostgreSQL for production
SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """Initialize database with sample data"""
    from ..models.learning_path import Base, Topic, User, TopicRelationship
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Add sample data
    db = SessionLocal()
    
    try:
        # Check if we already have data
        if db.query(Topic).count() > 0:
            return
        
        # Sample topics
        topics_data = [
            {"name": "Python Basics", "description": "Introduction to Python programming", 
             "difficulty_level": 2.0, "estimated_duration": 120, "content_type": "video"},
            {"name": "Variables and Data Types", "description": "Understanding Python data types", 
             "difficulty_level": 2.5, "estimated_duration": 90, "content_type": "interactive"},
            {"name": "Control Structures", "description": "Loops and conditionals in Python", 
             "difficulty_level": 3.0, "estimated_duration": 150, "content_type": "text"},
            {"name": "Functions", "description": "Creating and using functions", 
             "difficulty_level": 4.0, "estimated_duration": 180, "content_type": "video"},
            {"name": "Object-Oriented Programming", "description": "Classes and objects", 
             "difficulty_level": 6.0, "estimated_duration": 240, "content_type": "interactive"},
            {"name": "Data Structures", "description": "Lists, dictionaries, sets", 
             "difficulty_level": 4.5, "estimated_duration": 200, "content_type": "text"},
            {"name": "File Handling", "description": "Reading and writing files", 
             "difficulty_level": 3.5, "estimated_duration": 100, "content_type": "video"},
            {"name": "Error Handling", "description": "Exception handling in Python", 
             "difficulty_level": 5.0, "estimated_duration": 120, "content_type": "interactive"},
            {"name": "Web Development with Flask", "description": "Building web applications", 
             "difficulty_level": 7.0, "estimated_duration": 300, "content_type": "video"},
            {"name": "Database Integration", "description": "Working with databases", 
             "difficulty_level": 6.5, "estimated_duration": 250, "content_type": "text"}
        ]
        
        topics = []
        for topic_data in topics_data:
            topic = Topic(**topic_data)
            db.add(topic)
            topics.append(topic)
        
        db.commit()
        
        # Add topic relationships
        relationships = [
            (1, 2, "prerequisite", 0.9),  # Python Basics -> Variables
            (2, 3, "prerequisite", 0.8),  # Variables -> Control Structures
            (3, 4, "prerequisite", 0.7),  # Control -> Functions
            (4, 5, "prerequisite", 0.6),  # Functions -> OOP
            (2, 6, "prerequisite", 0.5),  # Variables -> Data Structures
            (4, 7, "related", 0.4),       # Functions -> File Handling
            (3, 8, "related", 0.6),       # Control -> Error Handling
            (5, 9, "prerequisite", 0.8),  # OOP -> Web Development
            (6, 10, "prerequisite", 0.7), # Data Structures -> Database
        ]
        
        for source, target, rel_type, strength in relationships:
            relationship = TopicRelationship(
                source_topic_id=source,
                target_topic_id=target,
                relationship_type=rel_type,
                strength=strength
            )
            db.add(relationship)
        
        # Sample users
        users_data = [
            {"username": "alice_learner", "email": "alice@example.com", 
             "learning_preferences": {"pace": "fast", "style": "visual"}},
            {"username": "bob_student", "email": "bob@example.com", 
             "learning_preferences": {"pace": "medium", "style": "hands-on"}},
            {"username": "charlie_dev", "email": "charlie@example.com", 
             "learning_preferences": {"pace": "slow", "style": "theoretical"}}
        ]
        
        for user_data in users_data:
            user = User(**user_data)
            db.add(user)
        
        db.commit()
        print("Database initialized with sample data")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()
