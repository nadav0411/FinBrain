# FinBrain Project - conftest.py - MIT License (c) 2025 Nadav Eshed


import os
import sys
from pathlib import Path


# Add the current "src" directory (where this file is located) to the Python path
server_src_dir = Path(__file__).parent.resolve()
if str(server_src_dir) not in sys.path:
    sys.path.insert(0, str(server_src_dir))


# Ensure tests use the test database
# This sets an environment variable that tells our application to run in "test mode"
# When ENV=test, the application will:
# - Use mongomock (fake in-memory database) instead of real MongoDB
# - Use test-specific cache keys in Redis to avoid mixing with production data
# - Enable test-only features like cache clearing functions
os.environ['ENV'] = 'test'
