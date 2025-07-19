# Day 15: Question Difficulty Classification

AI-powered system for automatically analyzing and classifying educational question difficulty levels.

## Quick Start

### Without Docker
```bash
# Build and install dependencies
./build.sh

# Run backend (Terminal 1)
cd backend
python -m uvicorn app.main:app --reload

# Run frontend (Terminal 2)  
cd frontend
npm start

# Run tests
./test.sh

# Run demo
./demo.sh
```

### With Docker
```bash
cd docker
docker-compose up --build
```

## Features

- 🎯 Multi-dimensional difficulty analysis
- 🧠 AI-enhanced classification using Claude
- 📊 Real-time feature visualization
- ⚡ Sub-200ms response times
- 🔄 Intelligent caching
- 📈 Batch processing support

## API Endpoints

- `POST /api/v1/classify` - Classify single question
- `POST /api/v1/classify-batch` - Batch classification
- `GET /api/v1/features/{question_id}` - Get feature analysis
- `GET /health` - Health check

## Testing

The system includes comprehensive test coverage:
- Unit tests for feature extraction
- Integration tests for classification pipeline
- API endpoint testing
- Performance benchmarks

## Architecture

The classifier uses a three-stage pipeline:
1. **Feature Extraction** - Linguistic and cognitive analysis
2. **Model Inference** - ML-based difficulty scoring  
3. **Contextual Adjustment** - Domain-specific calibration

## Configuration

Set environment variables in `backend/.env`:
```
ANTHROPIC_API_KEY=your-anthropic-api-key
REDIS_URL=redis://localhost:6379
```

## Web Interface

Access the interactive analyzer at http://localhost:3000
- Analyze individual questions
- View detailed feature breakdowns
- Monitor system performance
