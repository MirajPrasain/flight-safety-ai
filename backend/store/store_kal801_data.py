#!/usr/bin/env python3
"""
Script to store Korean Air Flight 801 crash data in the AI Aircraft Crash Prevention system.
"""

import requests
import json

# Korean Air Flight 801 crash data
kal801_data = {
    "flight_id": "CRASH_KAL801",
    "title": "Korean Air Flight 801",
    "date": "1997-08-06",
    "location": "Guam",
    "summary": "Controlled flight into terrain on approach to Guam due to descent below minimum safe altitude, non‑functional glideslope, and poor crew resource management.",
    "passengers": 254,
    "fatalities": 229,
    "survivors": 25,
    "primary_cause": "Pilot error and navigational aid failure",
    "key_factors": [
        "Non‑precision approach with out‑of‑service glideslope",
        "Descent below minimum safe altitude",
        "Captain fatigue and inadequate crew communication",
        "Pilot misinterpretation of navigation signals"
    ],
    "how_ai_copilot_could_help": "Detects descent below safe altitude and issues immediate terrain pull‑up alert; prompts for missed approach when glideslope signal weak or absent; enforces cross‑checks among crew."
}

def store_crash_data():
    """Store the Korean Air Flight 801 crash data via API endpoint."""
    try:
        # API endpoint
        url = "http://localhost:8000/store_crash_data/"
        
        # Send POST request
        response = requests.post(url, json=kal801_data)
        
        if response.status_code == 200:
            print("✅ Korean Air Flight 801 crash data stored successfully!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Failed to store crash data. Status: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the FastAPI backend is running on localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🚁 Storing Korean Air Flight 801 crash data...")
    store_crash_data() 