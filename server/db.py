# FinBrain Project - db.py - MIT License (c) 2025 Nadav Eshed


from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import logging


# Create a logger for this module
logger = logging.getLogger(__name__)

# Check if the environment is CI (GitHub Actions)
is_ci = os.getenv('GITHUB_ACTIONS') == 'true'
# Get the environment from the environment variable (if not set, default to development)
env = os.getenv('ENV', 'development')


if is_ci:
    logger.info("Detected CI environment (GitHub Actions) - skipping .env loading")
elif env == 'test':
    logger.info("Detected test environment - loading .env.test")
    # Load the .env.test file
    load_dotenv('.env.test')
else:
    logger.info("Detected dev/prod environment - loading default .env")
    # Load the default .env file
    load_dotenv()

# Re-fetch the environment variables after loading .env
env = os.getenv('ENV', 'development')
mongo_uri = os.getenv('MONGO_URI')
db_name = os.getenv('DB_NAME', 'FinBrain')
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')  


# Test mode - use mongomock
if env == 'test' or is_ci:
    try:
        from mongomock import MongoClient as MockMongoClient
    except ImportError:
        raise ImportError("mongomock is required for test environment. Run: pip install mongomock")

    # Create a mock MongoDB client
    client = MockMongoClient()
    # Create a mock database
    db = client['FinBrainTest']
    # Create a mock users collection
    users_collection = db['users']
    # Create a mock expenses collection
    expenses_collection = db['expenses']
    # Create a unique index on the users collection
    users_collection.create_index('email', unique=True)

    logger.info("Connected to in-memory MongoDB (mongomock) | DB=FinBrainTest | ENV=test")
    print(f"[DEBUG] ENV={env} | Using mongomock=True | DB Name={db.name}")


# Production/Development mode - use real MongoDB
else:
    if not mongo_uri:
        raise RuntimeError("MONGO_URI is not defined. Please set it in your environment or .env file.")

    try:
        # Create a real MongoDB client
        client = MongoClient(mongo_uri, server_api=ServerApi('1'))
        # Create a real database
        db = client[db_name]
        # Create a real users collection
        users_collection = db['users']
        # Create a real expenses collection
        expenses_collection = db['expenses']

        # Create a unique index on the users collection
        users_collection.create_index('email', unique=True)
        logger.info("Created unique index on users.email")

        # Ping the MongoDB server
        client.admin.command('ping')
        logger.info(f"Connected to MongoDB | URI={mongo_uri} | DB={db.name} | ENV={env}")
    except Exception as e:
        logger.error(f"Error connecting to MongoDB | {e}")
        raise e
