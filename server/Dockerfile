# FinBrain Project - Dockerfile - MIT License (c) 2025 Nadav Eshed


# The Dockerfile (used by the backend service) is like a recipe for building the backend image


# 1. Use a small official Python image (A Python image is a ready-to-use mini 
# Linux system that already has Python installed, so you don't need to install Python yourself)
# This will be the base of our container (like the starting point)
FROM python:3.10-slim

# 2. Set the working directory inside the container to /app
# This means: "All the next commands will run inside the /app folder"
WORKDIR /app

# 3. Copy everything from my local folder (current project) into the /app folder inside the container
COPY . /app

# 4. Install all the Python packages from requirements.txt
# --no-cache-dir means: "Don't save installation files we don't need"
RUN pip install --no-cache-dir -r requirements.txt

# 5. Set the environment variable to production
ENV ENV=production

# 6. Tell Docker that we plan to use port 5000 (Flask runs on this port by default)
EXPOSE 5000

#7. Run the app with Gunicorn – a production WSGI HTTP server for Python web applications.
# "Gunicorn" stands for Green Unicorn – a lightweight, multi-worker web server for WSGI apps.
# WSGI (Web Server Gateway Interface) is a standard interface between Python web frameworks (like Flask) and web servers.
#
# Flask’s built-in server (app.run) is only meant for development – it's single-threaded, lacks robustness and scalability,
# and should never be used in production environments.
#
# Gunicorn is designed for production: it manages multiple worker processes,
# handles concurrent requests efficiently, and provides better error isolation and load handling.
#
# -w 4             = run with 4 worker processes (parallel request handling)
# -b 0.0.0.0:5000  = bind to all network interfaces inside the Docker container on port 5000
# app:app          = run the "app" instance from "app.py" (format: filename:Flask_instance)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.app:app"]




# An image is a ready-made package that includes everything your app needs.
# It has Python, your code, and required libraries – all prepared to run.

# Image = the recipe (does not run)
# Container = the running instance made from that image



# Docker Compose manages multiple containers together.
# Each service can either:
# - use "build: ." to build a custom image using its own Dockerfile (like the backend), or
# - use "image: name" to pull a prebuilt image from Docker Hub (like MongoDB or Redis).
# This lets us define and run full multi-container apps with one command.


