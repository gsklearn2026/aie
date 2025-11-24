# Developer Setup Guide

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose
- Git

## Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourorg/quiz-platform
cd quiz-platform
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 4. Run Application
```bash
# Start all services
docker-compose up -d

# Access API documentation
open http://localhost:8000/api/docs
```

## Development Workflow

### Running Tests
```bash
pytest backend/tests/ -v
```

### Code Quality
```bash
# Linting
flake8 backend/

# Type checking
mypy backend/

# Format code
black backend/
```

### API Development

All endpoints must include:
- Pydantic models for request/response
- Complete docstrings
- Example requests/responses
- Error handling documentation

Example:
```python
@app.post("/api/v1/endpoint")
async def my_endpoint(request: MyRequest) -> MyResponse:
    """
    Endpoint description.
    
    Args:
        request: Request parameters
        
    Returns:
        Response data
        
    Raises:
        HTTPException: Error conditions
    """
    pass
```
