#!/bin/bash

echo "🚀 Starting Quiz Platform Services"

# Check if services are already running
if lsof -i:8000 > /dev/null 2>&1; then
    echo "⚠️  Backend is already running on port 8000"
else
    echo "🔵 Starting backend server..."
    cd backend
    python3.13 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    echo "✅ Backend started with PID: $BACKEND_PID"
fi

if lsof -i:3000 > /dev/null 2>&1; then
    echo "⚠️  Frontend is already running on port 3000"
else
    echo "🔵 Starting frontend server..."
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    echo "✅ Frontend started with PID: $FRONTEND_PID"
fi

# Wait a moment for services to start
echo "⏳ Waiting for services to start..."
sleep 5

# Check if services are running
echo "🔍 Checking service status..."

if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running on http://localhost:8000"
    echo "📚 API docs available at http://localhost:8000/docs"
else
    echo "❌ Backend failed to start"
fi

if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is running on http://localhost:3000"
else
    echo "❌ Frontend failed to start"
fi

echo ""
echo "🎉 Start script completed!"
echo ""
echo "📊 Services:"
echo "   - Backend: http://localhost:8000"
echo "   - Frontend: http://localhost:3000"
echo "   - API Docs: http://localhost:8000/docs"
echo ""
echo "🛑 To stop services: ./stop.sh"
echo "🧪 To run demo: ./demo.sh" 