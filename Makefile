# Variables

# Default target - shows help when just 'make' is run
.DEFAULT_GOAL := help

# PHONY targets (commands that don't produce files)
.PHONY: help build run down dev-be dev-fe build-fe install-be install-fe install test-be lint-be lint-fe format-be clean docker-build docker-build-be docker-build-fe docker-up docker-down docker-restart docker-logs docker-clean debug-be debug-fe

## help: Show this help message
help:
	@echo "Available commands:"
	@echo ""
	@echo "Development:"
	@echo "  make build        - Docker compose build of: backend, frontend"
	@echo "  make run          - Docker compose run: backend, frontend, database"
	@echo ""
	@echo "Dependencies:"
	@echo ""
	@echo "Testing & Quality:"
	@echo "  make test         - Run backend tests (pytest)"
	@echo "  make lint 		   - Lint backend code (ruff check)"
	@echo "  make format       - Format backend code (ruff format)"
	@echo ""
	@echo "Docker:"
	@echo "  make log-be          - Shows the backend logs"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean        - Remove build artifacts and caches"
	@echo "  make help         - Show this help message"

build:
	docker compose -f docker-compose.yml build

run:
	docker compose -f docker-compose.yml up -d

down:
	docker compose -f docker-compose.yml down

## dev-be: Run backend development server
dev-be:
	cd $(BACKEND_DIR) && uv run uvicorn app:app --reload --host 0.0.0.0 --port 8000

## dev-fe: Run frontend development server
dev-fe:
	cd $(FRONTEND_DIR) && npm run dev

## build-fe: Build frontend for production
build-fe:
	cd $(FRONTEND_DIR) && npm run build

## install: Install all dependencies
install: install-be install-fe
	@echo "✓ All dependencies installed"

## install-be: Install backend dependencies
install-be:
	cd $(BACKEND_DIR) && uv sync
	@echo "✓ Backend dependencies installed"

## install-fe: Install frontend dependencies
install-fe:
	cd $(FRONTEND_DIR) && npm install
	@echo "✓ Frontend dependencies installed"

## test-be: Run backend tests
test-be:
	cd $(BACKEND_DIR) && uv run pytest

## lint-be: Lint backend code
lint-be:
	ruff check $(BACKEND_DIR)

## format-be: Format backend code
format-be:
	ruff format $(BACKEND_DIR)

## lint-fe: Lint frontend code
lint-fe:
	cd $(FRONTEND_DIR) && npm run lint

## clean: Remove build artifacts and caches
clean:
	@echo "Cleaning build artifacts..."
	rm -rf $(FRONTEND_DIR).next
	rm -rf $(FRONTEND_DIR)out
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Cleaned"

log-be:
	@echo "Checking the backend logs in follow mode"
	docker logs -f cv-backend

## docker-build: Build all Docker images
docker-build:
	@echo "Building all Docker images..."
	docker compose -f docker-compose.yml build
	@echo "✓ All images built"

## docker-build-be: Build backend Docker image only
docker-build-be:
	@echo "Building backend Docker image..."
	docker compose -f docker-compose.yml build backend
	@echo "✓ Backend image built"

## docker-build-fe: Build frontend Docker image only
docker-build-fe:
	@echo "Building frontend Docker image..."
	docker compose -f docker-compose.yml build frontend
	@echo "✓ Frontend image built"

## docker-up: Start all services with docker-compose
docker-up:
	@echo "Starting all services..."
	docker compose -f docker-compose.yml up -d
	@echo "✓ Services started"
	@echo ""
	@echo "Services running at:"
	@echo "  Frontend: http://localhost:3000"
	@echo "  Backend:  http://localhost:8000"
	@echo "  Attu (Milvus UI): http://localhost:8080"
	@echo "  Redis:    localhost:6379"

## docker-down: Stop all services
docker-down:
	@echo "Stopping all services..."
	docker compose -f docker-compose.yml down
	@echo "✓ Services stopped"

## docker-restart: Restart all services
docker-restart:
	@echo "Restarting all services..."
	docker compose -f docker-compose.yml restart
	@echo "✓ Services restarted"

## docker-logs: View logs from all services
docker-logs:
	docker compose -f docker-compose.yml logs -f

## docker-clean: Stop services and remove volumes
docker-clean:
	@echo "Stopping services and removing volumes..."
	docker compose -f docker-compose.yml down -v
	@echo "✓ Services stopped and volumes removed"

## debug-be: Open bash shell in backend container
debug-be:
	@echo "Opening bash shell in cv-backend container..."
	docker exec -it cv-backend bash

## debug-fe: Open bash shell in frontend container
debug-fe:
	@echo "Opening bash shell in cv-frontend container..."
	docker exec -it cv-frontend bash
