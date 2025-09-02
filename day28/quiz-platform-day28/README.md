# Day 28: AI Quiz Platform - Data Export Service

A high-performance data export service that handles multiple formats (CSV, JSON, XML, PDF, Excel) with AI-powered insights and async processing.

## Features

- 🚀 **Multi-format exports**: CSV, JSON, XML, PDF, Excel
- 🧠 **AI-powered insights**: Integrated with Gemini AI for performance analysis  
- ⚡ **Async processing**: Background job processing with Celery
- 📊 **Real-time progress**: Live progress tracking and status updates
- 🗜️ **Compression**: Automatic file compression to reduce bandwidth
- 📈 **Dashboard**: React-based management dashboard
- 🔄 **Resumable**: Support for large dataset exports
- 🎯 **Filtering**: Advanced filtering and date range selection

## Quick Start

1. **Start services**:
   ```bash
   ./start.sh
   ```

2. **Access the application**:
   - Frontend Dashboard: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

3. **Stop services**:
   ```bash
   ./stop.sh
   ```

## Architecture

The export service consists of:

- **FastAPI Backend**: RESTful API with async job processing
- **React Frontend**: Interactive dashboard for export management
- **Celery Workers**: Background processing for large exports
- **Redis**: Job queue and caching
- **PostgreSQL**: Data storage and export job tracking

## Testing

Run backend tests:
```bash
cd backend
pytest tests/ -v
```

Run frontend tests:
```bash
cd frontend
npm test
```

## Docker Deployment

Build and run with Docker:
```bash
docker-compose up --build
```

## Configuration

Set environment variables in `backend/.env`:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string  
- `GEMINI_API_KEY`: Google Gemini API key for AI insights

## Export Formats

- **CSV**: Compressed CSV with optimized column ordering
- **JSON**: Structured JSON with metadata and compression
- **XML**: Well-formed XML with proper schema
- **PDF**: Executive reports with charts and summaries
- **Excel**: Multi-sheet workbooks with formatting
