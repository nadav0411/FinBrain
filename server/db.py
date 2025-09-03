from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os


# Loads the .env file so I can get the MongoDB URI and connect MongoDB
load_dotenv()
mongo_uri = os.getenv('MONGO_URI')

# Creates a connection to MongoDB Atlas
client = MongoClient(mongo_uri, server_api=ServerApi('1'))
# Picks the database called "FinBrain" from my MongoDB cluster
db = client['FinBrain']
# Picks a clolection called "users" from the "FinBrain" database - This is where I will store the registered users
users_collection = db['users']

# pings MongoDB to test the connection
try:
    client.admin.command('ping')
    print("Connected to MongoDB")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
