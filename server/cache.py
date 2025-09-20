# cache.py


import os
import redis
from dotenv import load_dotenv
import logging


# Create a logger for this module
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Get the Redis URL from environment or default to localhost
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Connect to Redis (decode_responses=True means we get strings instead of bytes)
try:
    r = redis.from_url(REDIS_URL, decode_responses=True)
    # Test the connection
    r.ping()
    logger.info("Connected to Redis", extra={"redis_url": REDIS_URL})
except Exception as e:
    logger.error("Failed to connect to Redis", extra={"redis_url": REDIS_URL, "error": str(e)})
    raise
