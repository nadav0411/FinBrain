# FinBrain Project - Dockerfile - MIT License (c) 2025 Nadav Eshed


# The Dockerfile (used by the backend service) is like a recipe for building the backend image


# 1. Use a small official Python image (A Python image is a ready-to-use mini 
# Linux system that already has Python installed, so you don't need to install Python yourself)
# This will be the base of our container (like the starting point)
FROM python:3.10-slim

# 2. Install system packages that allow secure HTTPS and SSL connections.
# - "ca-certificates" adds trusted SSL certificates (needed for MongoDB Atlas & HTTPS)
# - "curl" is a simple tool to test internet connections if needed
# - "update-ca-certificates" refreshes the certificate list in the container
# - "rm -rf /var/lib/apt/lists/*" cleans up temporary files to keep the image small
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates curl && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# 3. Set the working directory inside the container to /app
# This means: "All the next commands will run inside the /app folder"
WORKDIR /app

# 4. Copy everything from my local folder (current project) into the /app folder inside the container
COPY . /app

# 5. Add the src directory to Python path so imports work correctly
ENV PYTHONPATH=/app/src

# 6. Install all the Python packages from requirements.txt
# --no-cache-dir means: "Don't save installation files we don't need"
RUN pip install --no-cache-dir -r requirements.txt

# 7. Set the environment variable to production
ENV ENV=production

# 8. Tell Docker that we plan to use port 5000 (Flask runs on this port by default)
# (Render will automatically map this port to an available port on the server)
EXPOSE 5000

# 9. Run the app with Gunicorn – a production WSGI HTTP server for Python web applications.
# "Gunicorn" stands for Green Unicorn – a lightweight, multi-worker web server for WSGI apps.
# WSGI (Web Server Gateway Interface) is a standard interface between Python web frameworks (like Flask) and web servers.
#
# Flask’s built-in server (app.run) is only meant for development – it's single-threaded, lacks robustness and scalability,
# and should never be used in production environments.
#
# Gunicorn is designed for production: it manages multiple worker processes,
# handles concurrent requests efficiently, and provides better error isolation and load handling.
#
# sh -c                  → Run the following command in a shell, so we can use environment variables like $PORT
# gunicorn               → Start the web server
# -w 1                   → Use only 1 worker process to handle requests
# --timeout 120          → Allow up to 120 seconds for a request before it’s considered stuck and killed
# --preload              → Load the app once before starting workers – this reduces memory usage and speeds things up
# -b 0.0.0.0:${PORT}     → Listen on all network interfaces (0.0.0.0) and use the port given by the hosting service (Render)
# src.app:app            → This tells Gunicorn where to find your Flask app:
CMD ["sh", "-c", "gunicorn -w 1 --timeout 120 --preload -b 0.0.0.0:${PORT:-5000} src.app:app"]




# An image is a ready-made package that includes everything your app needs.
# It has Python, your code, and required libraries – all prepared to run.

# Image = the recipe (does not run)
# Container = the running instance made from that image



# Docker Compose manages multiple containers together.
# Each service can either:
# - use "build: ." to build a custom image using its own Dockerfile (like the backend), or
# - use "image: name" to pull a prebuilt image from Docker Hub (like MongoDB or Redis).
# This lets us define and run full multi-container apps with one command.


