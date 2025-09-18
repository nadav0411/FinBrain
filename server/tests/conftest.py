# conftest.py


import os


# Ensure tests use the test database
os.environ.setdefault('ENV', 'test')


