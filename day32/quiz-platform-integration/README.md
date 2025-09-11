# Quiz Platform Integration Testing

Day 32 implementation of integration testing for AI-powered Quiz Platform.

## Quick Start

1. **Build Environment:**
   ```bash
   ./build.sh
   ```

2. **Start Services:**
   ```bash
   ./start.sh
   ```

3. **Run Integration Tests:**
   ```bash
   source venv/bin/activate
   cd backend
   python -m pytest src/tests/integration/ -v
   ```

4. **Stop Services:**
   ```bash
   ./stop.sh
   ```

## API Endpoints

- **Health:** `GET /health`
- **Create Quiz:** `POST /api/quiz/`
- **Get Quiz:** `GET /api/quiz/{id}`
- **Generate Questions:** `POST /api/quiz/{id}/questions`
- **Register User:** `POST /api/auth/register`

## Test Dashboard

Visit: http://localhost:8000/docs

## Integration Test Coverage

✅ API endpoint validation  
✅ Database integration  
✅ External service integration  
✅ End-to-end workflows  
✅ Error handling scenarios  

## Environment Setup

Copy `.env.example` to `.env` and configure:
- `DATABASE_URL`
- `GEMINI_API_KEY`
