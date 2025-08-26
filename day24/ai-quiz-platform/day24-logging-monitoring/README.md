# AI Quiz Platform - Logging and Monitoring Service

A comprehensive AI-powered quiz platform with advanced logging, monitoring, and analytics capabilities.

## 🚀 Features

- **AI-Powered Quiz Generation**: Uses Google Gemini AI to create dynamic quizzes
- **Real-time Logging**: Comprehensive logging with structured data and multiple output formats
- **Performance Monitoring**: Built-in metrics collection and monitoring
- **Modern Web Interface**: React-based frontend with Ant Design components
- **RESTful API**: FastAPI backend with automatic documentation
- **Docker Support**: Containerized deployment with docker-compose
- **Testing Suite**: Comprehensive test coverage with pytest

## 🏗️ Architecture

```
├── backend/           # FastAPI Python backend
│   ├── app/          # Main application logic
│   ├── config/       # Configuration management
│   ├── middleware/   # Custom middleware
│   ├── services/     # Business logic services
│   └── utils/        # Utility functions
├── frontend/         # React TypeScript frontend
├── docs/            # Documentation
├── tests/           # Test suite
└── docker/          # Docker configuration
```

## 🛠️ Prerequisites

- Python 3.8+
- Node.js 16+
- Docker & Docker Compose (optional)
- Google Gemini API key

## 📦 Installation

### Quick Start (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd day24-logging-monitoring
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

3. **Start all services**
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

### Manual Setup

1. **Backend Setup**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload
   ```

2. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm start
   ```

## 🚀 Usage

### Starting Services

- **Start all services**: `./start.sh`
- **Stop all services**: `./stop.sh`
- **Demo mode**: `./demo.sh`

### Access Points

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **API Documentation**: http://localhost:8080/docs
- **Metrics Dashboard**: http://localhost:8000

### API Endpoints

- `GET /health` - Health check
- `POST /quiz/generate` - Generate new quiz
- `GET /quiz/{quiz_id}` - Get quiz details
- `POST /quiz/{quiz_id}/submit` - Submit quiz answers
- `GET /metrics` - Get performance metrics
- `GET /logs` - Get application logs

## 🐳 Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🧪 Testing

```bash
# Run all tests
cd backend
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_quiz_service.py
```

## 📊 Monitoring & Logging

### Log Levels
- `DEBUG`: Detailed debugging information
- `INFO`: General information about program execution
- `WARNING`: Warning messages for potentially problematic situations
- `ERROR`: Error messages for serious problems
- `CRITICAL`: Critical error messages that may prevent the program from running

### Metrics Collected
- Request/response times
- Error rates
- Quiz generation success rates
- API endpoint usage statistics
- System resource utilization

## 🔧 Configuration

Key configuration options in `.env`:

```bash
LOG_LEVEL=INFO                    # Logging verbosity
ENVIRONMENT=development           # Environment (dev/staging/prod)
GEMINI_API_KEY=your_key_here     # Google Gemini API key
ELASTICSEARCH_HOST=localhost:9200 # Elasticsearch host
REDIS_HOST=localhost             # Redis host
METRICS_PORT=8000                # Metrics server port
```

## 📝 Development

### Code Style
- **Python**: Follow PEP 8, use Black for formatting
- **TypeScript**: Use ESLint and Prettier
- **Tests**: Maintain >90% code coverage

### Adding New Features
1. Create feature branch
2. Implement feature with tests
3. Update documentation
4. Submit pull request

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation in the `docs/` folder
- Review the API documentation at `/docs`

## 🔄 Changelog

### v1.0.0
- Initial release with AI quiz generation
- Comprehensive logging and monitoring
- Modern web interface
- Docker deployment support
- Complete test suite
