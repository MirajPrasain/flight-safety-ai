# backend/insert_kal801.py
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from models import FlightData
from pymongo.errors import PyMongoError
from config import settings

# Define the KAL801 flight data
kal801_flight = {
    "flight_id": "CRASH_KAL801",
    "aircraft_type": "Boeing 747-300",
    "pilot_id": "KAL_CPT_001",
    "location": {
        "latitude": 13.484,
        "longitude": 144.801,
        "altitude_ft": 400
    },
    "speed": {
        "airspeed_knots": 140,
        "vertical_speed_fpm": -1500
    },
    "engine": {
        "engine_1_rpm": 88,
        "engine_2_rpm": 88
    },
    "aircraft_systems": {
        "landing_gear_status": "DOWN",
        "flap_setting": "FLAPS_30",
        "autopilot_engaged": True,
        "warnings": [
            "TERRAIN_PULL_UP",
            "GLIDE_SLOPE_WARNING",
            "SINK_RATE"
        ]
    },
    "environment": {
        "wind_speed_knots": 10,
        "wind_direction_deg": 210,
        "temperature_c": 27,
        "visibility_miles": 3,
        "precipitation": "MODERATE_RAIN",
        "terrain_proximity_ft": 120
    },
    "pilot_actions": {
        "throttle_percent": 35,
        "pitch_deg": -3,
        "roll_deg": 0,
        "yaw_deg": 0
    },
    "timestamp": datetime.fromisoformat("2025-06-12T21:30:00")
}

print("Loaded MONGO_URI:", settings.MONGO_URI)
print("Loaded DB_NAME:", settings.DB_NAME)

async def insert_kal801():
    """
    Insert KAL801 crash data into the crash_flights collection.
    Uses your existing MongoDB Atlas configuration from .env file.
    """
    try:
        # Connect to MongoDB using your existing configuration
        client = AsyncIOMotorClient(settings.MONGO_URI)
        db = client[settings.DB_NAME]
        collection = db["crash_flights"]
        
        print(f"🔗 Connected to MongoDB Atlas database: {settings.DB_NAME}")
        
        # Validate with Pydantic model
        flight_data = FlightData(**kal801_flight)
        flight_data_dict = flight_data.model_dump()

        # Ensure timestamp is stored as datetime object for MongoDB
        if isinstance(flight_data_dict.get("timestamp"), str):
            flight_data_dict["timestamp"] = datetime.fromisoformat(
                flight_data_dict["timestamp"].replace('Z', '+00:00')
            )

        # Insert into the DB
        result = await collection.insert_one(flight_data_dict)
        print(f"✅ Inserted KAL801 with ID: {result.inserted_id}")
        
        # Close the connection
        client.close()
        
        return result.inserted_id
        
    except PyMongoError as e:
        print(f"❌ Database error: {e}")
        print("💡 Check your MongoDB Atlas connection string in .env file")
        raise
    
    except Exception as e:
        print(f"❌ Error inserting KAL801 data: {e}")
        raise

if __name__ == "__main__":
    print("🚀 Starting KAL801 crash data insertion...")
    print(f"📋 Using database: {settings.DB_NAME}")
    asyncio.run(insert_kal801()) 