.PHONY: help setup build start stop logs clean demo test

help:
	@echo "AI Content Agent System - Commands:"
	@echo "  make setup     - Setup development environment"
	@echo "  make build     - Build Docker containers"
	@echo "  make start     - Start all services"
	@echo "  make stop      - Stop all services"
	@echo "  make logs      - View container logs"
	@echo "  make clean     - Remove containers and volumes"
	@echo "  make demo      - Setup demo with sample data"
	@echo "  make test      - Run tests"

setup:
	@echo "Setting up development environment..."
	python -m venv venv
	./venv/bin/pip install -r backend/requirements.txt
	cd frontend && npm install

build:
	@echo "Building Docker containers..."
	docker-compose build

start:
	@echo "Starting services..."
	docker-compose up -d
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
	@echo "Ollama: http://localhost:11434"

stop:
	@echo "Stopping services..."
	docker-compose down

logs:
	@echo "Showing logs..."
	docker-compose logs -f

clean:
	@echo "Cleaning up..."
	docker-compose down -v
	rm -rf backend/uploads/* backend/data/*

demo:
	@echo "Setting up demo..."
	docker-compose up -d
	@sleep 10
	@echo "Pulling Gemma 7B model..."
	docker exec ai-agent-ollama ollama pull gemma:7b
	@sleep 5
	@echo "Creating sample data..."
	curl -X POST http://localhost:8000/api/v1/auth/login \
		-H "Content-Type: application/json" \
		-d '{"username": "admin@demo.com", "password": "demo123"}'
	@echo ""
	@echo "Demo setup complete!"
	@echo "Access:"
	@echo "  Frontend: Coming soon"
	@echo "  Backend API: http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/docs"
	@echo ""
	@echo "Demo credentials:"
	@echo "  Admin: admin@demo.com / demo123"
	@echo "  Reviewer: reviewer@demo.com / demo123"
	@echo "  Client: client@demo.com / demo123"

test:
	@echo "Running tests..."
	cd backend && python -m pytest tests/ -v
