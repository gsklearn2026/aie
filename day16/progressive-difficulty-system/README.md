# Progressive Difficulty System

A comprehensive system for managing and adapting difficulty levels in educational or gaming applications using AI-driven analytics.

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (recommended) OR
- **Python 3.8+** and **Node.js 16+** (for local development)
- **Redis** (for caching and session management)

### Using the Scripts

The project includes three convenient scripts for managing the entire system:

#### 1. Start the System
```bash
./start.sh
```

This script will:
- Detect if Docker is available and ask your preference
- Start all services (Redis, Backend, Frontend)
- Wait for services to be ready
- Display service URLs

**Options:**
- **Docker mode**: Uses Docker Compose to orchestrate all services
- **Local mode**: Runs services directly on your machine

#### 2. Stop the System
```bash
./stop.sh
```

This script will:
- Stop all running services
- Clean up processes and ports
- Remove temporary files
- Handle both Docker and local services

#### 3. Check System Status
```bash
./status.sh
```

This script will:
- Show the status of all services
- Display which ports are in use
- Check if processes are running
- Provide service URLs

## 📁 Project Structure

```
progressive-difficulty-system/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API endpoints
│   │   ├── models/         # Data models
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utilities
│   ├── config/             # Configuration
│   ├── tests/              # Backend tests
│   └── requirements.txt    # Python dependencies
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   └── utils/          # Frontend utilities
│   ├── public/             # Static assets
│   └── package.json        # Node.js dependencies
├── docker/                 # Docker configurations
├── docs/                   # Documentation
├── tests/                  # Integration tests
├── start.sh               # Start script
├── stop.sh                # Stop script
├── status.sh              # Status script
└── docker-compose.yml     # Docker orchestration
```

## 🔧 Services

### Backend (FastAPI)
- **Port**: 8000
- **Health Check**: `http://localhost:8000/health`
- **Features**:
  - RESTful API endpoints
  - AI-powered difficulty adjustment
  - Performance analytics
  - Redis integration for caching
- **Docker**: Multi-stage build with security hardening

### Frontend (React)
- **Port**: 3000
- **URL**: `http://localhost:3000`
- **Features**:
  - Interactive difficulty simulator
  - Real-time performance metrics
  - Modern UI with Tailwind CSS
  - Responsive design
- **Docker**: Nginx-based production build with gzip compression

### Redis
- **Port**: 6379
- **Purpose**: Caching and session management
- **Features**:
  - Performance data caching
  - User session storage
  - Real-time analytics
- **Docker**: Alpine-based lightweight image

### Redis
- **Port**: 6379
- **Purpose**: Caching and session management
- **Features**:
  - Performance data caching
  - User session storage
  - Real-time analytics

## 🛠️ Development

### Local Development Setup

1. **Install Dependencies**
   ```bash
   # Backend
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

2. **Start Services**
   ```bash
   # Start Redis (macOS with Homebrew)
   brew services start redis
   
   # Start Backend
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   
   # Start Frontend (in another terminal)
   cd frontend
   npm start
   ```

### Docker Development

#### Production Mode (Optimized)
1. **Build and Start**
   ```bash
   docker-compose up --build
   ```

2. **View Logs**
   ```bash
   docker-compose logs -f [service_name]
   ```

3. **Stop Services**
   ```bash
   docker-compose down
   ```

#### Development Mode (Hot Reloading)
1. **Build and Start**
   ```bash
   docker-compose -f docker-compose.dev.yml up --build
   ```

2. **View Logs**
   ```bash
   docker-compose -f docker-compose.dev.yml logs -f [service_name]
   ```

3. **Stop Services**
   ```bash
   docker-compose -f docker-compose.dev.yml down
   ```

#### Docker Optimization Commands
```bash
# Check image sizes
make docker-size

# Clean up Docker resources
make docker-clean

# Optimize images
make docker-optimize

# Build without cache
make docker-build
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
./tests/run_integration_tests.sh
```

## 📊 API Documentation

Once the backend is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🔍 Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Check what's using the port
   lsof -i :8000
   
   # Kill the process
   kill -9 <PID>
   ```

2. **Docker Issues**
   ```bash
   # Clean up Docker resources
   docker system prune -a
   
   # Restart Docker
   # (Restart Docker Desktop on macOS/Windows)
   ```

3. **Redis Connection Issues**
   ```bash
   # Check if Redis is running
   redis-cli ping
   
   # Start Redis manually
   brew services start redis  # macOS
   sudo systemctl start redis  # Linux
   ```

### Script Troubleshooting

- **Permission Denied**: Make sure scripts are executable
  ```bash
  chmod +x start.sh stop.sh status.sh
  ```

- **Script Not Found**: Ensure you're in the project root directory
  ```bash
  pwd  # Should show the project root
  ls -la *.sh  # Should show the scripts
  ```

## 📝 Environment Variables

Create a `.env` file in the project root for local development:

```env
# Backend
REDIS_HOST=localhost
REDIS_PORT=6379
DATABASE_URL=postgresql://user:password@localhost/dbname

# Frontend
REACT_APP_API_URL=http://localhost:8000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section above
- Review the API documentation
- Open an issue on GitHub 