#!/bin/bash

echo "🚀 Starting Quiz Platform API Versioning System"
echo "==============================================="

if [ -z "$1" ]; then
    echo "Usage: ./start.sh [1|2]"
    echo "  1 = Local Python environment"
    echo "  2 = Docker environment"
    exit 1
fi

if [ "$1" = "1" ]; then
    echo "🐍 Starting with local Python environment..."
    
    # Start backend
    echo "🔧 Starting backend server..."
    cd backend
    source venv/bin/activate
    nohup python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    cd ..
    
    # Wait for backend to start
    sleep 3
    
    # Start frontend
    echo "⚛️ Starting frontend server..."
    cd frontend
    nohup npm start > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    cd ..
    
    echo ""
    echo "✅ Services started successfully!"
    echo "📊 Dashboard: http://localhost:3000"
    echo "📖 API Docs: http://localhost:8000/docs"
    echo "🔍 Backend logs: tail -f backend.log"
    echo "🔍 Frontend logs: tail -f frontend.log"
    echo ""
    echo "To stop services, run: ./stop.sh"
    
elif [ "$1" = "2" ]; then
    echo "🐳 Starting with Docker..."
    
    docker-compose up -d
    
    echo ""
    echo "✅ Docker services started successfully!"
    echo "📊 Dashboard: http://localhost:3000"
    echo "📖 API Docs: http://localhost:8000/docs"
    echo "🔍 View logs: docker-compose logs -f"
    echo ""
    echo "To stop services, run: ./stop.sh 2"
    
else
    echo "❌ Invalid option. Use 1 for local or 2 for Docker."
fi

# Demo data creation
echo ""
echo "🎯 Creating demo data..."
sleep 5

# Create sample quizzes to demonstrate versioning
curl -X POST "http://localhost:8000/api/v1/quiz/create" \
     -H "Content-Type: application/json" \
     -H "X-API-Version: v1" \
     -d '{
       "title": "Basic Python Quiz (V1)",
       "description": "Simple quiz created with V1 API",
       "questions": [
         {
           "question": "What is the output of print(2+2)?",
           "options": ["3", "4", "5", "22"],
           "correct_answer": 1,
           "points": 1
         }
       ]
     }' &> /dev/null

curl -X POST "http://localhost:8000/api/v2/quiz/create" \
     -H "Content-Type: application/json" \
     -H "X-API-Version: v2" \
     -d '{
       "title": "Advanced AI Quiz (V2)",
       "description": "AI-enhanced quiz with difficulty analysis and hints",
       "questions": [
         {
           "question": "Explain the time complexity of a binary search algorithm and why it is more efficient than linear search for sorted arrays",
           "options": [
             "O(n) because it checks every element",
             "O(log n) because it halves the search space each iteration",
             "O(n²) because it compares all pairs",
             "O(1) because it finds immediately"
           ],
           "correct_answer": 1,
           "points": 2
         }
       ]
     }' &> /dev/null

echo "✅ Demo data created!"
echo ""
echo "🎉 System is ready! Visit http://localhost:3000 to explore API versioning features!"
