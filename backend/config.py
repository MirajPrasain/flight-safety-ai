# backend/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

# 1. Class-Based Configuration, 2. Pydantic Settings Pattern
class Settings(BaseSettings): #Inheritance - Settings inherits from BaseSettings 
    # Class Attributes - Define configuration fields as class variables
    MONGO_URI: str  #Type Annotations - str defines expected data types for validation
    DB_NAME: str

    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")
# Configuration Dictionary - Uses SettingsConfigDict to specify behavior
# Environment File Loading - Automatically reads from .env file
# Extra Field Handling - extra="ignore" prevents errors from unexpected environment variables

settings = Settings()
#Singleton Pattern - Module-Level Instance - Creates a single, reusable configuration object
