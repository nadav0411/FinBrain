# db.py

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os
import logging


# Create a logger for this module
logger = logging.getLogger(__name__)

# Check if we're running in CI (GitHub Actions) first (that use mongomock)
is_ci = os.getenv('GITHUB_ACTIONS') == 'true'

# Only load .env file if not in CI
if not is_ci:
    # Loads the .env file so we can get the MongoDB URI
    if os.getenv('ENV') == 'test':
        load_dotenv('.env.test')
    else:
        load_dotenv()

# Gets the MongoDB URI from the .env file
mongo_uri = os.getenv('MONGO_URI')

# Use in-memory database only when no MongoDB URI is available (probably in CI -> GitHub Actions)
if not mongo_uri:
    logger.info("No MongoDB URI found, using in-memory database for testing")
    from pymongo import MongoClient
    from mongomock import MongoClient as MockMongoClient
    
    # Use mongomock for testing
    client = MockMongoClient()
    db = client['FinBrainTest']
    users_collection = db['users']
    expenses_collection = db['expenses']
    
    # Create unique index for email
    users_collection.create_index('email', unique=True)
    
    logger.info("Connected to in-memory MongoDB (mongomock)")

else:
    # Creates a connection to MongoDB Atlas
    client = MongoClient(mongo_uri, server_api=ServerApi('1'))
    
    # Use an isolated DB name in tests to protect real data
    db = client['FinBrainTest'] if os.getenv('ENV') == 'test' else client['FinBrain']
    
    # Collections
    users_collection = db['users']
    expenses_collection = db['expenses']
    
    # Ensure unique index on users.email to prevent duplicates
    try:
        users_collection.create_index('email', unique=True)
        logger.info("Created unique index on users.email")
    except Exception as e:
        logger.warning("Could not ensure unique index on users.email", extra={"error": str(e)})
    
    # Ping MongoDB to test the connection
    try:
        client.admin.command('ping')
        logger.info("Connected to MongoDB", extra={"database": db.name})
    except Exception as e:
        logger.error("Error connecting to MongoDB", extra={"error": str(e)})
