# FinBrain Project - conftest.py - MIT License (c) 2025 Nadav Eshed


import os
import sys
from pathlib import Path


# Add the server directory to Python path for imports
# This is needed so that when pytest runs our tests, Python can find and import our modules
# like 'app', 'db', 'cache', etc. from the server directory
server_dir = Path(__file__).parent
if str(server_dir) not in sys.path:
    # Insert the server directory at the beginning of Python's module search path
    # This tells Python: "when looking for modules, check the server directory first"
    sys.path.insert(0, str(server_dir))


# Ensure tests use the test database
# This sets an environment variable that tells our application to run in "test mode"
# When ENV=test, the application will:
# - Use mongomock (fake in-memory database) instead of real MongoDB
# - Use test-specific cache keys in Redis to avoid mixing with production data
# - Enable test-only features like cache clearing functions
os.environ['ENV'] = 'test'
