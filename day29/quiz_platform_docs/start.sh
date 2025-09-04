#!/bin/bash

echo "🚀 Starting Quiz Platform API Documentation System..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install Node.js dependencies
cd frontend
npm install
cd ..

# Set environment variables
export FLASK_APP=backend/app.py
export FLASK_ENV=development
export GEMINI_API_KEY=demo-key

echo "📚 Starting Flask API with OpenAPI documentation..."
cd backend
python app.py &
FLASK_PID=$!
cd ..

# Wait for Flask to start
sleep 5

echo "🌐 Starting React documentation UI..."
cd frontend
npm start &
REACT_PID=$!
cd ..

echo "🧪 Running tests..."
sleep 3
source venv/bin/activate
pytest tests/ -v

echo "
✅ API Documentation System Started Successfully!

🌐 Swagger UI Documentation: http://localhost:3000
📖 API Documentation: http://localhost:5000/docs/
🔗 OpenAPI Specification: http://localhost:5000/swagger.json
🏥 Health Check: http://localhost:5000/health

API Endpoints Available:
- GET /api/v1/quizzes/ - List all quizzes
- POST /api/v1/quizzes/ - Create new quiz
- GET /api/v1/quizzes/{id} - Get specific quiz
- PUT /api/v1/quizzes/{id} - Update quiz
- DELETE /api/v1/quizzes/{id} - Delete quiz
- GET /api/v1/analytics/stats - Get analytics
- POST /api/v1/ai/generate-questions - Generate AI questions

Process IDs:
- Flask API: $FLASK_PID
- React UI: $REACT_PID

Use 'bash stop.sh' to stop all services.
"

# Keep script running
wait
