"""Database Models and Configuration"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
import os

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://quiz_user:quiz_pass@localhost/quiz_security_db")

from sqlalchemy import create_engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="student")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    
class SecurityAudit(Base):
    __tablename__ = "security_audits"
    
    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(String, unique=True, index=True)
    status = Column(String, default="running")
    overall_score = Column(Integer, default=0)
    results_json = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    completed_at = Column(DateTime, nullable=True)

class SecurityVulnerability(Base):
    __tablename__ = "security_vulnerabilities"
    
    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(String, ForeignKey("security_audits.audit_id"))
    vulnerability_type = Column(String)
    severity = Column(String)
    description = Column(Text)
    location = Column(String)
    status = Column(String, default="open")  # open, fixed, ignored
    created_at = Column(DateTime, default=datetime.now)

def get_db() -> Session:
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)
