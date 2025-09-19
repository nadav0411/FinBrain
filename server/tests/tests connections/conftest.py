# conftest.py


import os
import sys
from pathlib import Path

# Add the server directory to Python path for imports
server_dir = Path(__file__).parent.parent
if str(server_dir) not in sys.path:
    sys.path.insert(0, str(server_dir))

# Ensure tests use the test database
os.environ.setdefault('ENV', 'test')


