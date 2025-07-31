# Progressive Quiz Platform - Local Development Setup

This guide will help you set up and run the Progressive Quiz Platform locally without Docker.

## Prerequisites

Before starting, make sure you have the following installed:

- **Python 3.8+**
- **Node.js 16+** and npm
- **PostgreSQL** (with psql command line tool)
- **Redis**

### Installing Prerequisites

#### macOS (using Homebrew)
```bash
# Install Python (if not already installed)
brew install python

# Install Node.js
brew install node

# Install PostgreSQL
brew install postgresql

# Install Redis
brew install redis
```

#### Ubuntu/Debian
```bash
# Install Python
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# Install Redis
sudo apt install redis-server
```

## Database Setup

1. **Start PostgreSQL service:**
   ```bash
   # macOS
   brew services start postgresql
   
   # Ubuntu/Debian
   sudo systemctl start postgresql
   ```

2. **Create database and user:**
   ```bash
   # Connect to PostgreSQL as superuser
   sudo -u postgres psql
   
   # Create database and user
   CREATE DATABASE quiz_db;
   CREATE USER quiz_user WITH PASSWORD 'quiz_pass';
   GRANT ALL PRIVILEGES ON DATABASE quiz_db TO quiz_user;
   \q
   ```

3. **Start Redis:**
   ```bash
   # macOS
   brew services start redis
   
   # Ubuntu/Debian
   sudo systemctl start redis-server
   ```

## Environment Configuration

Create a `.env` file in the `backend` directory with the following content:

```bash
# Database Configuration
DATABASE_URL=postgresql://quiz_user:quiz_pass@localhost:5432/quiz_db

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Application Settings
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# CORS Settings
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```

## Running the Application

### Quick Start
Use the provided scripts:

```bash
# Start the application
./start.sh

# Stop the application
./stop.sh
```

### Manual Start (Alternative)

If you prefer to start services manually:

1. **Backend Setup:**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Frontend Setup:**
   ```bash
   cd frontend
   npm install
   ```

3. **Start Services:**
   ```bash
   # Terminal 1 - Backend
   cd backend
   source venv/bin/activate
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   
   # Terminal 2 - Frontend
   cd frontend
   npm start
   ```

## Accessing the Application

Once started, you can access:

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs

## Troubleshooting

### Common Issues

1. **Port already in use:**
   - Check if PostgreSQL is running on port 5432
   - Check if Redis is running on port 6379
   - Kill any existing processes on ports 3000 or 8000

2. **Database connection errors:**
   - Ensure PostgreSQL is running
   - Verify database credentials in `.env` file
   - Check if database and user exist

3. **Redis connection errors:**
   - Ensure Redis is running
   - Check Redis configuration

4. **Permission errors:**
   - Make sure scripts are executable: `chmod +x start.sh stop.sh`
   - Check file permissions for database access

### Useful Commands

```bash
# Check if PostgreSQL is running
pg_isready -h localhost -p 5432

# Check if Redis is running
redis-cli ping

# View running processes
ps aux | grep -E "(uvicorn|node|postgres|redis)"

# Kill processes by port
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

## Development

### Backend Development
- The backend uses FastAPI with automatic reload
- API documentation is available at `/docs`
- Models are in `backend/app/models/`
- API routes are in `backend/app/api/`

### Frontend Development
- React application with hot reload
- Components are in `frontend/src/components/`
- Services are in `frontend/src/services/`

## Stopping the Application

Use the stop script:
```bash
./stop.sh
```

This will:
- Stop the backend server
- Stop the frontend server
- Stop PostgreSQL and Redis (if started by the script)
- Clean up process ID files 