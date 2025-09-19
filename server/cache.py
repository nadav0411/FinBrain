# cache.py


import os
import redis
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Get the Redis URL from environment or default to localhost
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Connect to Redis (decode_responses=True means we get strings instead of bytes)
r = redis.from_url(REDIS_URL, decode_responses=True)
