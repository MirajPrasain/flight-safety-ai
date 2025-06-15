#!/usr/bin/env python3
"""
Script to store Air France Flight 447 crash data with vector embeddings
for similarity search in the AI Aircraft Crash Prevention system.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from search_utils import store_crash_flight_data

# Air France Flight 447 crash data
air_france_447 = {
    "flight_id": "CRASH_AF447",
    "title": "Air France Flight 447",
    "date": "2009-06-01",
    "location": "Atlantic Ocean (off Brazil's northeast coast)",
    "summary": "On June 1, 2009, Air France Flight 447 from Rio de Janeiro to Paris crashed into the Atlantic Ocean after an aerodynamic stall triggered by unreliable airspeed readings and improper pilot response, killing all 228 people on board.",
    "passengers": 216,
    "fatalities": 228,
    "survivors": 0,
    "primary_cause": "Aerodynamic stall due to pilot error after ice crystals blocked the pitot tubes, leading to unreliable airspeed and improper control inputs.",
    "key_factors": [
        "Pitot tubes iced over, causing unreliable airspeed and autopilot disconnect",
        "Destabilized flight path due to inappropriate pilot control inputs",
        "Crew failed to perform proper procedure for unreliable airspeed",
        "Pilots did not recognize the stall and failed to recover"
    ],
    "how_ai_copilot_could_help": "An AI copilot could have identified the frozen pitot tube issue and provided correct airspeed using other data, keeping autopilot engaged or taking corrective action to maintain proper pitch and thrust, thereby preventing the high-altitude stall.",
    "embedding_summary": "Air France Flight 447, 2009-06-01, Atlantic Ocean off Brazil's northeast coast. On 1 June 2009, Air France Flight 447 en route from Rio de Janeiro to Paris crashed into the Atlantic Ocean after entering an aerodynamic stall triggered by iced pitot tubes and pilot mismanagement, killing all 228 onboard. Primary cause: an unrecovered stall due to pilot error following unreliable airspeed indications. Key factors: pitot tube icing (loss of airspeed data), inappropriate crew inputs, failure to follow stall procedure, and lack of timely stall recovery."
}

async def main():
    """Store the Air France Flight 447 crash data with vector embeddings."""
    print("🚨 Storing Air France Flight 447 crash data...")
    print(f"Flight ID: {air_france_447['flight_id']}")
    print(f"Date: {air_france_447['date']}")
    print(f"Location: {air_france_447['location']}")
    print(f"Fatalities: {air_france_447['fatalities']}")
    print()
    
    try:
        success = await store_crash_flight_data(air_france_447)
        if success:
            print("✅ Air France Flight 447 crash data stored successfully!")
            print("📊 The data is now available for similarity search in the AI copilot system.")
            print("🔍 Pilots can now get relevant historical context for similar pitot tube and stall scenarios.")
        else:
            print("❌ Failed to store Air France Flight 447 crash data.")
            return 1
    except Exception as e:
        print(f"❌ Error storing crash data: {e}")
        return 1
    
    print("\n🎯 Key AI Copilot Benefits for Similar Scenarios:")
    print("• Detect pitot tube icing and unreliable airspeed indications")
    print("• Provide alternative airspeed calculations using other sensors")
    print("• Maintain proper pitch and thrust during unreliable airspeed conditions")
    print("• Alert pilots to impending stall conditions at high altitude")
    print("• Guide proper stall recovery procedures")
    print("• Keep autopilot engaged when possible or provide manual guidance")
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 