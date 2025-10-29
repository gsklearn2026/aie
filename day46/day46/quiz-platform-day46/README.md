# Day 46: Quiz Taking Interface

Interactive quiz taking system with AI-powered questions and real-time session management.

## Features

- 🤖 AI-generated questions using Gemini
- ⏱️ Real-time timer and progress tracking
- 📊 Intelligent result analysis
- 🎯 Interactive question presentation
- 💾 Auto-save functionality
- 📱 Responsive design

## Quick Start

```bash
# Build and start
./build.sh

# Start services
./start.sh

# Stop services
./stop.sh

# Run demo
./build.sh demo
```

## URLs

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## Architecture

- **Frontend**: React with state management
- **Backend**: FastAPI with Gemini AI
- **Database**: In-memory (Redis in production)
- **AI**: Google Gemini Pro

## Testing

```bash
./build.sh test
```
