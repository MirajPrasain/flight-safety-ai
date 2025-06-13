# backend/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings


# These lines use dot notation to access the configuration values:
# settings.MONGO_URI gets the MongoDB connection string from environment variables
# settings.DB_NAME gets the database name from environment variables

# Initialize the asynchronous MongoDB client
client = AsyncIOMotorClient(settings.MONGO_URI) 
# Access the database
db = client[settings.DB_NAME]


# Access the flight_data collection
flight_data_collection = db["flight_data"]

collection = db["crash_flights"] 
#  Think of this like a SQL table — here you're using "crash_flights" for storing fatal historical incidents.

def get_database():
    return db





# So yes, those two lines are completely dependent on the settings instance from config.py - they're accessing the configuration data that Pydantic automatically loaded from your environment variables or .env file.

# Import Phase: Python imports the settings instance from config.py
# Settings Loading: The settings object automatically reads from the .env file
# Value Access: settings.MONGO_URI and settings.DB_NAME return the actual values

# settings is an instance of Settings class
# MONGO_URI and DB_NAME are attributes of that instance
# Python uses dot notation to access object attributes