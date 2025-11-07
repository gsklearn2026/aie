#!/bin/bash

echo "========================================"
echo "Starting Quiz API Optimization System"
echo "========================================"

seed_demo_data() {
    local using_docker="$1"
    local project_root="$2"
    local python_exec="$3"

    echo ""
    echo "Loading demo data for dashboard..."

    if command -v curl >/dev/null 2>&1; then
        for _ in $(seq 1 6); do
            curl -s -H "Accept-Encoding: gzip" "http://localhost:8000/api/quizzes?limit=10" >/dev/null || true
            sleep 0.3
        done

        for quiz_id in 1 2 3; do
            curl -s -H "Accept-Encoding: gzip" "http://localhost:8000/api/quiz/${quiz_id}" >/dev/null || true
            sleep 0.2
        done
    fi

    if [ "$using_docker" = true ]; then
        docker-compose exec -T backend python - <<'PY'
import asyncio
import random
from datetime import datetime, timedelta
import sys

sys.path.append('/app')

from backend.config.settings import settings
from backend.models.quiz import PerformanceMetric
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select


async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        result = await session.execute(select(PerformanceMetric).limit(1))
        if result.scalar_one_or_none():
            print("Demo metrics already present.")
            return

        samples = [
            {"endpoint": "/api/quizzes", "method": "GET", "base_size": 52000, "base_compressed": 14800, "responses": [24, 22, 25, 19, 18, 21]},
            {"endpoint": "/api/quiz/1", "method": "GET", "base_size": 40500, "base_compressed": 12600, "responses": [36, 31, 29, 32]},
            {"endpoint": "/api/quiz/2", "method": "GET", "base_size": 43200, "base_compressed": 13500, "responses": [39, 35, 34, 33]},
            {"endpoint": "/api/quiz/3", "method": "GET", "base_size": 45200, "base_compressed": 13950, "responses": [41, 37, 36, 34]},
        ]

        base_time = datetime.utcnow() - timedelta(minutes=30)
        for sample in samples:
            for idx, duration in enumerate(sample["responses"]):
                metric = PerformanceMetric(
                    endpoint=sample["endpoint"],
                    method=sample["method"],
                    response_time_ms=duration + random.uniform(-3, 3),
                    response_size_bytes=sample["base_size"] + random.randint(-1500, 1500),
                    compressed_size_bytes=sample["base_compressed"] + random.randint(-800, 800),
                    cache_hit=1 if idx > 0 else 0,
                    timestamp=base_time + timedelta(minutes=idx)
                )
                session.add(metric)

        await session.commit()

    await engine.dispose()


asyncio.run(seed())
PY
    else
        PYTHONPATH="$project_root" "$python_exec" <<'PY'
import asyncio
import random
from datetime import datetime, timedelta

from backend.config.settings import settings
from backend.models.quiz import PerformanceMetric
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select


async def seed():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        result = await session.execute(select(PerformanceMetric).limit(1))
        if result.scalar_one_or_none():
            print("Demo metrics already present.")
            return

        samples = [
            {"endpoint": "/api/quizzes", "method": "GET", "base_size": 52000, "base_compressed": 14800, "responses": [24, 22, 25, 19, 18, 21]},
            {"endpoint": "/api/quiz/1", "method": "GET", "base_size": 40500, "base_compressed": 12600, "responses": [36, 31, 29, 32]},
            {"endpoint": "/api/quiz/2", "method": "GET", "base_size": 43200, "base_compressed": 13500, "responses": [39, 35, 34, 33]},
            {"endpoint": "/api/quiz/3", "method": "GET", "base_size": 45200, "base_compressed": 13950, "responses": [41, 37, 36, 34]},
        ]

        base_time = datetime.utcnow() - timedelta(minutes=30)
        for sample in samples:
            for idx, duration in enumerate(sample["responses"]):
                metric = PerformanceMetric(
                    endpoint=sample["endpoint"],
                    method=sample["method"],
                    response_time_ms=duration + random.uniform(-3, 3),
                    response_size_bytes=sample["base_size"] + random.randint(-1500, 1500),
                    compressed_size_bytes=sample["base_compressed"] + random.randint(-800, 800),
                    cache_hit=1 if idx > 0 else 0,
                    timestamp=base_time + timedelta(minutes=idx)
                )
                session.add(metric)

        await session.commit()

    await engine.dispose()


asyncio.run(seed())
PY
    fi

    echo "Demo data ready!"
}

USE_DOCKER=false
if [ "$1" == "--docker" ]; then
    USE_DOCKER=true
fi

if [ "$USE_DOCKER" = true ]; then
    echo "Starting with Docker..."
    docker-compose up -d
    
    echo "Waiting for services to be healthy..."
    sleep 10
    
    echo ""
    echo "✅ System started!"
    echo "📊 Dashboard: http://localhost:3000"
    echo "🔌 API: http://localhost:8000"
    echo "📈 Metrics: http://localhost:8000/api/metrics/performance"

    seed_demo_data true "$PWD" "python"
    
else
    echo "Starting without Docker..."
    
    # Start Redis (assumes Redis is installed)
    redis-server --daemonize yes 2>/dev/null || echo "Redis already running or not installed locally"
    
    # Start backend
    PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    PYTHON_EXEC="$PROJECT_ROOT/backend/venv/bin/python"
    PYTHONPATH="$PROJECT_ROOT" $PYTHON_EXEC -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 > "$PROJECT_ROOT/backend.log" 2>&1 &
    BACKEND_PID=$!
    echo "Backend started (PID: $BACKEND_PID)"
    
    # Start frontend
    cd frontend
    BROWSER=none npm start > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "Frontend started (PID: $FRONTEND_PID)"
    cd ..
    
    # Save PIDs
    echo $BACKEND_PID > .backend.pid
    echo $FRONTEND_PID > .frontend.pid
    
    echo ""
    echo "Waiting for services to start..."
    sleep 15
    
    echo ""
    echo "✅ System started!"
    echo "📊 Dashboard: http://localhost:3000"
    echo "🔌 API: http://localhost:8000"
    echo "📈 Metrics: http://localhost:8000/api/metrics/performance"

    seed_demo_data false "$PROJECT_ROOT" "$PYTHON_EXEC"
    echo ""
    echo "Logs:"
    echo "  Backend: tail -f backend.log"
    echo "  Frontend: tail -f frontend.log"
fi

echo ""
echo "To stop: ./scripts/stop.sh$([ "$USE_DOCKER" = true ] && echo ' --docker')"
