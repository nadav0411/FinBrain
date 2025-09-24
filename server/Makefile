# Makefile for FinBrain

# Default ENV
ENV ?= development

# Run Flask app locally (for dev use only)
run:
	@echo "Running Flask app locally in $(ENV) mode..."
	ENV=$(ENV) python app.py

# Run tests with pytest
test:
	@echo "Running tests..."
	ENV=test pytest -v tests/

# Build and run Docker containers
up:
	@echo "Starting Docker Compose in $(ENV) mode..."
	docker compose --env-file .env.docker up --build

# Stop and remove all containers
down:
	@echo "Stopping Docker Compose..."
	docker compose down

# View logs from the backend container
logs:
	docker compose logs -f backend

# Remove all Docker containers, volumes, and images (⚠️ dangerous)
clean:
	@echo "Removing all containers, volumes and images..."
	docker system prune -af --volumes

# Lint the code using flake8 (optional)
lint:
	flake8 . --exclude=venv,.venv,__pycache__

# Help
help:
	@echo "Available commands:"
	@echo "  make run       - Run Flask app (locally)"
	@echo "  make test      - Run unit tests"
	@echo "  make up        - Start Docker Compose (build included)"
	@echo "  make down      - Stop Docker Compose"
	@echo "  make logs      - Tail logs from backend"
	@echo "  make clean     - Remove all Docker resources (danger!)"
	@echo "  make lint      - Run flake8 linter"
