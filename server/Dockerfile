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

# 5. Tell Docker that we plan to use port 5000 (Flask runs on this port by default)
EXPOSE 5000

# 6. When the container starts, run this command to start the Flask server
CMD ["python", "app.py"]


# An image is a ready-made package that includes everything your app needs.
# It has Python, your code, and required libraries – all prepared to run.

# Image = the recipe (does not run)
# Container = the running instance made from that image

