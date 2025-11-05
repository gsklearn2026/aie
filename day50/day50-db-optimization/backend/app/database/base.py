from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import os
import time
from typing import Generator

# Default to port 5433 if using Docker PostgreSQL (to avoid conflict with local PostgreSQL on 5432)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://quizuser:quizpass@localhost:5433/quizdb")

# Optimized engine with connection pooling
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,  # Connection pool size
    max_overflow=10,  # Additional connections when pool exhausted
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections after 1 hour
    echo=False  # Set to True for query logging
)

# Query performance tracking
query_stats = {}

@event.listens_for(engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total_time = time.time() - conn.info['query_start_time'].pop()
    
    # Log slow queries (>100ms)
    if total_time > 0.1:
        print(f"SLOW QUERY ({total_time:.3f}s): {statement[:100]}")
    
    # Track query statistics
    query_key = statement[:50]
    if query_key not in query_stats:
        query_stats[query_key] = {'count': 0, 'total_time': 0, 'max_time': 0}
    
    query_stats[query_key]['count'] += 1
    query_stats[query_key]['total_time'] += total_time
    query_stats[query_key]['max_time'] = max(query_stats[query_key]['max_time'], total_time)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_query_stats():
    """Return query performance statistics"""
    return query_stats
