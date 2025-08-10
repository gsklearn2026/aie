#!/bin/bash

echo "🚀 Starting Topic Relationship Mapping Service..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies  
cd frontend
npm install
cd ..

# Set environment variables
export GEMINI_API_KEY="${GEMINI_API_KEY:-demo-key}"
export DATABASE_URL="${DATABASE_URL:-sqlite:///./quiz_platform.db}"
export REDIS_URL="${REDIS_URL:-redis://localhost:6379}"

echo "✅ Dependencies installed"

# Start services with Docker
cd docker
docker-compose up -d postgres redis
echo "⏳ Waiting for services to start..."
sleep 10

cd ..

# Run database migrations
cd backend
python -c "import sys; sys.path.append('..'); from backend.database import create_tables; create_tables()"
echo "✅ Database initialized"

# Seed some test data
python -c "
import sys
sys.path.append('..')
import asyncio
from backend.database import SessionLocal
from backend.models.schemas import TopicCreate
from backend.services.relationship_service import RelationshipService

async def seed_data():
    db = SessionLocal()
    service = RelationshipService()
    
    topics = [
        TopicCreate(name='Linear Algebra', description='Mathematical foundations for ML', category='Mathematics', difficulty_level=3),
        TopicCreate(name='Statistics', description='Statistical concepts and methods', category='Mathematics', difficulty_level=2),
        TopicCreate(name='Python Programming', description='Programming fundamentals', category='Programming', difficulty_level=1),
        TopicCreate(name='Machine Learning', description='ML algorithms and concepts', category='AI', difficulty_level=4),
        TopicCreate(name='Deep Learning', description='Neural networks and deep learning', category='AI', difficulty_level=5),
        TopicCreate(name='Data Structures', description='Fundamental data structures', category='Computer Science', difficulty_level=2),
        TopicCreate(name='Algorithms', description='Algorithm design and analysis', category='Computer Science', difficulty_level=3)
    ]
    
    for topic_data in topics:
        await service.create_topic(db, topic_data)
    
    db.close()
    print('✅ Test data seeded')

asyncio.run(seed_data())
"

# Start backend
cd ..
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

cd ../frontend

# Start frontend
npm start &
FRONTEND_PID=$!

echo "🎉 Services started!"
echo "📊 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"

# Wait for services
wait $BACKEND_PID $FRONTEND_PID
