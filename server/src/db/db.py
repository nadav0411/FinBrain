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
    logger.info("Detected test environment - loading configs/.env.test")
    # Load the .env.test file
    load_dotenv('configs/.env.test')
else:
    logger.info("Detected dev/prod environment - loading configs/.env.development")
    # Load the default .env file
    load_dotenv('configs/.env.development')

# Get the environment from the environment variable (if not set, default to development)
env = os.getenv('ENV', 'development')

# Get the DB name from environment
db_name = os.getenv('DB_NAME', 'FinBrain')

# Get the Redis URL from environment
raw_redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
# If it's a file path (e.g. from AWS Secrets Store), read the secret from the file
if raw_redis_url and os.path.isfile(raw_redis_url):
    try:
        with open(raw_redis_url, 'r') as f:
            redis_url = f.read().strip()
    except Exception as e:
        raise RuntimeError(f"Failed to read REDIS_URL from file: {raw_redis_url}") from e
else:
    redis_url = raw_redis_url

# Get the MongoDB URI from environment
raw_mongo_uri = os.getenv('MONGO_URI')
# If it's a file path (e.g. from AWS Secrets Store), read the secret from the file
if raw_mongo_uri and os.path.isfile(raw_mongo_uri):
    try:
        with open(raw_mongo_uri, 'r') as f:
            mongo_uri = f.read().strip()
    except Exception as e:
        raise RuntimeError(f"Failed to read MONGO_URI from file: {raw_mongo_uri}") from e
else:
    mongo_uri = raw_mongo_uri


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
    # Create a mock user_feedback collection
    user_feedback_collection = db['user_feedback']

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
        client = MongoClient(
        mongo_uri,
        server_api=ServerApi('1'),
        tls=True,
        tlsAllowInvalidCertificates=False,
        connectTimeoutMS=20000,
        socketTimeoutMS=20000,
        retryWrites=True
        )
        # Create a real database
        db = client[db_name]
        # Create a real users collection
        users_collection = db['users']
        # Create a real expenses collection
        expenses_collection = db['expenses']
        # Create a real user_feedback collection
        user_feedback_collection = db['user_feedback']

        # Create a unique index on the users collection
        users_collection.create_index('email', unique=True)
        logger.info("Created unique index on users.email")

        # Ping the MongoDB server
        client.admin.command('ping')
        logger.info(f"Connected to MongoDB | URI={mongo_uri} | DB={db.name} | ENV={env}")
    except Exception as e:
        logger.error(f"Error connecting to MongoDB | {e}")
        raise e
