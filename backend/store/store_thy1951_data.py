#!/usr/bin/env python3
"""
Script to store Turkish Airlines Flight 1951 crash data in the AI Aircraft Crash Prevention system.
"""

import requests
import json

# Turkish Airlines Flight 1951 crash data
thy1951_data = {
    "flight_id": "CRASH_THY1951",
    "title": "Turkish Airlines Flight 1951",
    "date": "2009-02-25",
    "location": "Near Amsterdam Schiphol Airport, Amsterdam, Netherlands",
    "summary": "Investigators concluded that a faulty altimeter and pilot error led to Turkish Airlines Flight 1951 crashing on approach to Amsterdam Schiphol Airport.",
    "passengers": 128,
    "fatalities": 9,
    "survivors": 126,
    "primary_cause": "A faulty radio altimeter reading triggered the autothrottle to cut engine power to idle, and the crew failed to notice in time to recover, resulting in an aerodynamic stall on approach.",
    "key_factors": [
        "Faulty left radio altimeter gave an incorrect low altitude indication",
        "Autothrottle reduced thrust to idle based on the false altitude data",
        "High pilot workload and inattention to airspeed (glide slope intercept from above) delayed the crew's response",
        "Pilots did not execute proper stall recovery after the stick-shaker (stall warning) activated"
    ],
    "how_ai_copilot_could_help": "An AI-powered co-pilot could cross-check multiple sensor inputs (such as dual altimeters) to detect anomalies and prevent automated systems from relying on a single faulty reading. It would also monitor airspeed and flight path, alerting the crew to an impending stall or even taking corrective action (like adding thrust or initiating a go-around) if the pilots fail to respond in time, thereby helping to avoid or mitigate this kind of accident.",
    "embedding_summary": "Turkish Airlines Flight 1951, 2009-02-25, near Amsterdam Schiphol Airport, Amsterdam, Netherlands – stalled and crashed on approach due to a faulty radio altimeter and pilot error. Primary cause: the faulty altimeter triggered idle engine thrust and the crew reacted too late to prevent a stall. Key factors: faulty altimeter; autothrottle cut power; crew not monitoring airspeed; high workload and improper stall recovery."
}

def store_crash_data():
    """Store the Turkish Airlines Flight 1951 crash data via API endpoint."""
    try:
        # API endpoint
        url = "http://localhost:8000/store_crash_data/"
        
        # Send POST request
        response = requests.post(url, json=thy1951_data)
        
        if response.status_code == 200:
            print("✅ Turkish Airlines Flight 1951 crash data stored successfully!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Failed to store crash data. Status: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error: Make sure the FastAPI backend is running on localhost:8000")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("🚁 Storing Turkish Airlines Flight 1951 crash data...")
    store_crash_data() 