from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

MONGO_URI = os.environ.get('MONGO_URI')
ATLAS_VECTOR_SEARCH_INDEX_NAME = os.environ.get('ATLAS_VECTOR_SEARCH_INDEX_NAME')
MISTRAL_API_KEY = os.environ.get('MISTRAL_API_KEY')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')

# Validate environment variables
if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set")
if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY environment variable is not set")

# MongoDB connection with timeout and retry configuration
try:
    client = MongoClient(
        MONGO_URI,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=10000,
        retryWrites=True,
        maxPoolSize=50,
        minPoolSize=10
    )
    # Validate connection
    client.admin.command('ping')
    logger.info("Successfully connected to MongoDB Atlas")
except (ServerSelectionTimeoutError, ConnectionFailure) as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    raise RuntimeError(f"MongoDB connection failed: {e}")

db = client['ResumeCollection']
resume_collection = db['ResumeCollection']