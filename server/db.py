# db.py

from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os


# Loads the .env file so I can get the MongoDB URI and connect MongoDB (test or production)
if os.getenv('ENV') == "test":
    load_dotenv(".env.test")
else:
    load_dotenv()

# Gets the MongoDB URI from the .env file
mongo_uri = os.getenv('MONGO_URI')

# Creates a connection to MongoDB Atlas
client = MongoClient(mongo_uri, server_api=ServerApi('1'))
# Picks the database called "FinBrain" from my MongoDB cluster
db = client['FinBrain']
# Picks a clolection called "users" from the "FinBrain" database - This is where I will store the registered users
users_collection = db['users']
# Picks a clolection called "expenses" from the "FinBrain" database - This is where I will store the expenses
expenses_collection = db['expenses']

# Ensure unique index on users.email to prevent duplicates
try:
    users_collection.create_index('email', unique=True)
except Exception as e:
    print(f"Warning: could not ensure unique index on users.email: {e}")

# pings MongoDB to test the connection
try:
    client.admin.command('ping')
    print("Connected to MongoDB")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
