#!/usr/bin/env python3
"""
Script to store Colgan Air Flight 3407 crash data with vector embeddings
for similarity search in the AI Aircraft Crash Prevention system.
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from search_utils import store_crash_flight_data

# Colgan Air Flight 3407 crash data
colgan_air_3407 = {
    "flight_id": "CRASH_COLGAN3407",
    "title": "Colgan Air Flight 3407",
    "date": "2009-02-12",
    "location": "Clarence Center, New York, USA",
    "summary": "On February 12, 2009, Colgan Air Flight 3407 (Continental Connection from Newark to Buffalo) stalled on approach and crashed into a house in Clarence Center, New York, killing all 49 people aboard and one person on the ground.",
    "passengers": 45,
    "fatalities": 49,
    "survivors": 0,
    "primary_cause": "Pilot's inappropriate response to an impending stall (pulled back on the controls instead of proper stall recovery), resulting in loss of control.",
    "key_factors": [
        "Crew failed to monitor airspeed, allowing the aircraft to slow to a stall",
        "Violation of sterile cockpit rules (distracting conversation during approach)",
        "Captain's failure to manage the flight and crew effectively",
        "Inadequate airline training/procedures for managing approach and airspeed in icing"
    ],
    "how_ai_copilot_could_help": "An AI copilot could have monitored the aircraft's speed and configuration during approach, alerted the pilots about the impending stall, or even taken control to adjust the nose pitch and increase throttle. By reacting instantly to the stall warning and correcting the flight path (something a human missed due to distraction/fatigue), the AI system might have prevented the stall and crash.",
    "embedding_summary": "Colgan Air Flight 3407, 2009-02-12, Clarence Center, New York, USA. On February 12, 2009, this Newark-to-Buffalo flight entered an aerodynamic stall on approach and crashed into a house in Clarence Center, killing all 49 onboard (and one on the ground). Primary cause: the captain's incorrect response to the stall warning (improper recovery input). Key factors: inadequate airspeed monitoring, breach of sterile cockpit discipline, poor cockpit management by the captain, and insufficient training/procedures for flight in icing conditions."
}

async def main():
    """Store the Colgan Air Flight 3407 crash data with vector embeddings."""
    print("🚨 Storing Colgan Air Flight 3407 crash data...")
    print(f"Flight ID: {colgan_air_3407['flight_id']}")
    print(f"Date: {colgan_air_3407['date']}")
    print(f"Location: {colgan_air_3407['location']}")
    print(f"Fatalities: {colgan_air_3407['fatalities']}")
    print()
    
    try:
        success = await store_crash_flight_data(colgan_air_3407)
        if success:
            print("✅ Colgan Air Flight 3407 crash data stored successfully!")
            print("📊 The data is now available for similarity search in the AI copilot system.")
            print("🔍 Pilots can now get relevant historical context for similar stall scenarios.")
        else:
            print("❌ Failed to store Colgan Air Flight 3407 crash data.")
            return 1
    except Exception as e:
        print(f"❌ Error storing crash data: {e}")
        return 1
    
    print("\n🎯 Key AI Copilot Benefits for Similar Scenarios:")
    print("• Monitor airspeed during approach phases")
    print("• Alert pilots to impending stall conditions")
    print("• Provide immediate stall recovery guidance")
    print("• Enforce sterile cockpit discipline reminders")
    print("• Cross-check multiple sensor inputs for airspeed validation")
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 