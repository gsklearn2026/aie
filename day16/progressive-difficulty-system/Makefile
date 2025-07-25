# Progressive Difficulty System - Makefile
# Provides convenient commands for development

.PHONY: help start stop status clean install test build docker-build docker-up docker-down logs

# Default target
help:
	@echo "Progressive Difficulty System - Available Commands:"
	@echo ""
	@echo "  make start        - Start all services (Docker or local)"
	@echo "  make stop         - Stop all services"
	@echo "  make status       - Check status of all services"
	@echo "  make clean        - Clean up temporary files and containers"
	@echo "  make install      - Install dependencies for local development"
	@echo "  make test         - Run all tests"
	@echo "  make build        - Build frontend for production"
	@echo "  make docker-build - Build Docker images"
	@echo "  make docker-up    - Start services with Docker Compose"
	@echo "  make docker-down  - Stop Docker services"
	@echo "  make logs         - Show Docker service logs"
	@echo "  make help         - Show this help message"

# Start all services
start:
	@echo "Starting Progressive Difficulty System..."
	@./start.sh

# Stop all services
stop:
	@echo "Stopping Progressive Difficulty System..."
	@./stop.sh

# Check status
status:
	@./status.sh

# Clean up
clean:
	@echo "Cleaning up..."
	@rm -f .backend.pid .frontend.pid
	@rm -f .temp_*
	@docker system prune -f 2>/dev/null || true
	@echo "Cleanup completed"

# Install dependencies for local development
install:
	@echo "Installing dependencies..."
	@echo "Installing backend dependencies..."
	@cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	@cd frontend && npm install
	@echo "Dependencies installed successfully"

# Run tests
test:
	@echo "Running tests..."
	@echo "Running backend tests..."
	@cd backend && source venv/bin/activate && pytest -v
	@echo "Running frontend tests..."
	@cd frontend && npm test -- --watchAll=false

# Build frontend for production
build:
	@echo "Building frontend for production..."
	@cd frontend && npm run build
	@echo "Frontend build completed"

# Docker commands
docker-build:
	@echo "Building optimized Docker images..."
	@docker-compose build --no-cache

docker-build-dev:
	@echo "Building development Docker images..."
	@docker-compose -f docker-compose.dev.yml build --no-cache

docker-up:
	@echo "Starting production Docker services..."
	@docker-compose up -d

docker-up-dev:
	@echo "Starting development Docker services..."
	@docker-compose -f docker-compose.dev.yml up -d

docker-down:
	@echo "Stopping Docker services..."
	@docker-compose down

docker-down-dev:
	@echo "Stopping development Docker services..."
	@docker-compose -f docker-compose.dev.yml down

docker-clean:
	@echo "Cleaning up Docker resources..."
	@docker system prune -f
	@docker volume prune -f

docker-optimize:
	@echo "Optimizing Docker images..."
	@docker image prune -f
	@docker builder prune -f

docker-size:
	@echo "Docker image sizes:"
	@docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep progressive-difficulty-system

# Show logs
logs:
	@echo "Showing Docker service logs..."
	@docker-compose logs -f

# Development shortcuts
dev-backend:
	@echo "Starting backend in development mode..."
	@cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "Starting frontend in development mode..."
	@cd frontend && npm start

# Database commands
db-migrate:
	@echo "Running database migrations..."
	@cd backend && source venv/bin/activate && alembic upgrade head

db-rollback:
	@echo "Rolling back database migration..."
	@cd backend && source venv/bin/activate && alembic downgrade -1

# Linting and formatting
lint-backend:
	@echo "Linting backend code..."
	@cd backend && source venv/bin/activate && flake8 app/ tests/ --max-line-length=88

lint-frontend:
	@echo "Linting frontend code..."
	@cd frontend && npm run lint

format-backend:
	@echo "Formatting backend code..."
	@cd backend && source venv/bin/activate && black app/ tests/

format-frontend:
	@echo "Formatting frontend code..."
	@cd frontend && npm run format

# Security checks
security-check:
	@echo "Running security checks..."
	@cd backend && source venv/bin/activate && safety check
	@cd frontend && npm audit

# Performance monitoring
monitor:
	@echo "Starting performance monitoring..."
	@docker-compose logs -f backend | grep -E "(ERROR|WARNING|CRITICAL)"

# Backup and restore
backup:
	@echo "Creating backup..."
	@docker-compose exec redis redis-cli BGSAVE
	@echo "Backup completed"

restore:
	@echo "Restoring from backup..."
	@docker-compose exec redis redis-cli FLUSHALL
	@echo "Restore completed" 