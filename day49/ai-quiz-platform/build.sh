#!/bin/bash

echo "🏗️  Building AI Quiz Platform - End-to-End Integration"
echo "======================================================="

# Build option selection
echo "Choose build option:"
echo "1) Build with Docker"
echo "2) Build without Docker (Local Environment)"
read -p "Enter your choice (1 or 2): " choice

case $choice in
    1)
        echo "🐳 Building with Docker..."
        
        # Build and start services
        docker-compose down
        docker-compose build
        docker-compose up -d
        
        echo "⏳ Waiting for services to start..."
        sleep 15
        
        echo "🧪 Running integration tests..."
        docker-compose exec backend python -m pytest tests/ -v
        
        echo "✅ Docker build complete!"
        echo "🌐 Frontend: http://localhost:3000"
        echo "🔧 Backend API: http://localhost:8000"
        echo "📋 API Docs: http://localhost:8000/docs"
        ;;
    2)
        echo "💻 Building without Docker..."
        
        # Backend setup
        echo "Setting up backend..."
        cd backend
        python -m venv venv
        
        # Activate virtual environment
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
            source venv/Scripts/activate
        else
            source venv/bin/activate
        fi
        
        pip install -r requirements.txt
        
        # Start backend in background
        echo "Starting backend server..."
        python app/main.py &
        BACKEND_PID=$!
        cd ..
        
        # Frontend setup
        echo "Setting up frontend..."
        cd frontend
        npm install
        
        # Start frontend in background
        echo "Starting frontend server..."
        npm start &
        FRONTEND_PID=$!
        cd ..
        
        echo "⏳ Waiting for services to start..."
        sleep 10
        
        # Run tests
        echo "🧪 Running tests..."
        cd backend
        if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
            source venv/Scripts/activate
        else
            source venv/bin/activate
        fi
        python -m pytest tests/ -v
        cd ..
        
        echo "✅ Local build complete!"
        echo "🌐 Frontend: http://localhost:3000"
        echo "🔧 Backend API: http://localhost:8000"
        echo "📋 API Docs: http://localhost:8000/docs"
        
        # Save PIDs for cleanup
        echo $BACKEND_PID > .backend.pid
        echo $FRONTEND_PID > .frontend.pid
        ;;
    *)
        echo "Invalid choice. Please run the script again and choose 1 or 2."
        exit 1
        ;;
esac

echo ""
echo "🎉 Build completed successfully!"
echo ""
echo "📖 Next steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Register a new account or login"
echo "3. Create your first AI-generated quiz"
echo "4. Take quizzes and see the integration in action"
echo ""
echo "🛠️  Integration Features Demonstrated:"
echo "• Frontend-Backend API communication"
echo "• Real-time AI quiz generation with Gemini"
echo "• JWT authentication flow"
echo "• Database integration with SQLAlchemy"
echo "• Error handling across the full stack"
echo "• Responsive Material-UI components"
