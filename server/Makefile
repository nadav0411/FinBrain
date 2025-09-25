# Makefile for FinBrain

# Default ENV
ENV ?= development

# Run Flask app locally (for development use only)
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
	@echo "Showing logs from the backend container..."
	docker compose logs -f backend

# Remove all Docker containers, volumes, and images
clean:
	@echo "Removing all containers, volumes and images..."
	docker system prune -af --volumes

# Show running containers
all-containers:
	@echo "Listing all containers..."
	docker compose ps 

# Remove all containers, volumes and images
clean-all:
	@echo "Removing all containers, volumes and images..."
	docker compose down --volumes --remove-orphans

# Rebuild Docker Compose
rebuild:
	@echo "Rebuilding Docker Compose..."
	docker compose build --no-cache


# Only start the containers
only-up:
	@echo "Starting Docker Compose..."
	docker compose up



# Help
help:
	@echo "Available commands:"
	@echo "  make run            - Run Flask app (locally)"
	@echo "  make test           - Run unit tests"
	@echo "  make up             - Start Docker Compose (build included)"
	@echo "  make down           - Stop Docker Compose"
	@echo "  make logs           - Tail logs from backend"
	@echo "  make clean          - Remove all Docker resources"
	@echo "  make clean-all      - Remove all containers, volumes and images"
	@echo "  make all-containers - Show running containers"
	@echo "  make rebuild        - Rebuild Docker Compose"
	@echo "  make only-up        - Only start the containers"


# Copy all files from the source directory to the destination directory -> linux terminal
# rsync -av --progress /mnt/c/Users/DELL/OneDrive/Documents/FinBrain/ ~/FinBrain/ 