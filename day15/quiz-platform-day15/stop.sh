#!/bin/bash

echo "🛑 Stopping Quiz Platform Services"

# Stop uvicorn processes
echo "🔴 Stopping backend server..."
pkill -f uvicorn
pkill -f "python.*app.main:app"

# Stop npm processes (frontend)
echo "🔴 Stopping frontend server..."
pkill -f "npm start"
pkill -f "react-scripts"

# Stop any node processes on port 3000
echo "🔴 Stopping processes on port 3000..."
lsof -ti:3000 | xargs kill -9 2>/dev/null

# Stop any processes on port 8000
echo "🔴 Stopping processes on port 8000..."
lsof -ti:8000 | xargs kill -9 2>/dev/null

# Stop any remaining Python processes related to the project
echo "🔴 Stopping remaining Python processes..."
pkill -f "quiz-platform-day15"

# Wait a moment for processes to stop
sleep 2

# Check if any processes are still running
echo "🔍 Checking for remaining processes..."

if pgrep -f uvicorn > /dev/null; then
    echo "⚠️  Some uvicorn processes may still be running"
    pgrep -f uvicorn
else
    echo "✅ All uvicorn processes stopped"
fi

if pgrep -f "npm start" > /dev/null; then
    echo "⚠️  Some npm processes may still be running"
    pgrep -f "npm start"
else
    echo "✅ All npm processes stopped"
fi

# Check ports
if lsof -i:3000 > /dev/null 2>&1; then
    echo "⚠️  Port 3000 is still in use"
else
    echo "✅ Port 3000 is free"
fi

if lsof -i:8000 > /dev/null 2>&1; then
    echo "⚠️  Port 8000 is still in use"
else
    echo "✅ Port 8000 is free"
fi

echo "🎉 Stop script completed!"
echo ""
echo "📊 Services stopped:"
echo "   - Backend (uvicorn) on port 8000"
echo "   - Frontend (npm) on port 3000"
echo ""
echo "🚀 To restart services:"
echo "   - Backend: cd backend && python3.13 -m uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo "   - Frontend: cd frontend && npm start"
echo "   - Or use: ./demo.sh" 