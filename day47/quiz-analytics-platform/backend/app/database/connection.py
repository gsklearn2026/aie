from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./quiz_analytics.db")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    try:
        from app.models.quiz import Base
        Base.metadata.create_all(bind=engine)
        print("Database initialized successfully!")
    except Exception as e:
        print(f"Warning: Database initialization failed: {e}")
        print("Server will continue to start, but database operations may fail.")
        print("Using SQLite as fallback. Set DATABASE_URL in .env for PostgreSQL.")
