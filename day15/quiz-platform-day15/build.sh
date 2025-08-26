#!/bin/bash

echo "🔨 Building Quiz Platform - Day 15: Question Difficulty Classification"

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
python -m pip install --upgrade pip
pip install -r requirements.txt

# Download NLTK data
echo "📚 Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt', quiet=True); nltk.download('stopwords', quiet=True)"

# Download spaCy model
echo "🧠 Downloading spaCy model..."
python -m spacy download en_core_web_sm

cd ..

# Install frontend dependencies  
echo "🎨 Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "✅ Build completed successfully!"
echo ""
echo "🚀 Next steps:"
echo "1. Run backend: cd backend && python -m uvicorn app.main:app --reload"
echo "2. Run frontend: cd frontend && npm start"
echo "3. Run tests: ./test.sh"
echo "4. Run with Docker: cd docker && docker-compose up"
