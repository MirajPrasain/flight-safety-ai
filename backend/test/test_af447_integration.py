#!/usr/bin/env python3
"""
Test script to verify Air France Flight 447 crash data integration
with the AI Aircraft Crash Prevention system.
"""

import asyncio
import sys
import os
import requests
import json

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from search_utils import search_similar_flights

# Test data for Air France Flight 447 scenario
test_flight_data = {
    "flight_id": "CRASH_AF447",
    "aircraft_type": "Airbus A330-203",
    "timestamp": "2009-06-01T02:10:00Z",
    "location": {
        "altitude_ft": 35000,
        "latitude": -3.0,
        "longitude": -30.0
    },
    "speed": {
        "airspeed_knots": 275,  # Unreliable due to pitot tube icing
        "vertical_speed_fpm": -1000
    },
    "engine": {
        "engine_1_rpm": 95,
        "engine_2_rpm": 95
    },
    "aircraft_systems": {
        "landing_gear_status": "Retracted",
        "flap_setting": "0",
        "autopilot_engaged": False,  # Disconnected due to unreliable airspeed
        "warnings": ["Unreliable Airspeed", "Autopilot Disconnect", "Stall Warning"]
    },
    "environment": {
        "wind_speed_knots": 25,
        "wind_direction_deg": 270,
        "temperature_c": -50,
        "visibility_miles": 10,
        "precipitation": "Heavy Rain",
        "terrain_proximity_ft": 35000
    },
    "pilot_actions": {
        "throttle_percent": 85,
        "pitch_deg": 15,  # Incorrect pitch input
        "roll_deg": 0,
        "yaw_deg": 0
    }
}

async def test_af447_integration():
    """Test the Air France Flight 447 crash data integration."""
    print("🧪 Testing Air France Flight 447 Integration")
    print("=" * 50)
    
    # Test 1: Similar crash search
    print("\n1️⃣ Testing Similar Crash Search...")
    try:
        results = await search_similar_flights(
            query_summary="high altitude stall due to unreliable airspeed from pitot tube icing",
            top_k=3
        )
        
        print(f"✅ Found {len(results)} similar crashes")
        for i, result in enumerate(results, 1):
            print(f"   {i}. {result.get('title', 'Unknown')} - {result.get('date', 'Unknown')}")
            if result.get('flight_id') == 'CRASH_AF447':
                print(f"      🎯 Air France Flight 447 found in results!")
        
    except Exception as e:
        print(f"❌ Error in similar crash search: {e}")
    
    # Test 2: AI Copilot Chat Response
    print("\n2️⃣ Testing AI Copilot Chat Response...")
    try:
        response = requests.post(
            "http://localhost:8000/chat/status_update/",
            json={
                "flight_id": "CRASH_AF447",
                "message": "Pitot tubes are iced over, airspeed unreliable, autopilot just disconnected"
            },
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ AI Copilot Response Received:")
            print(f"   Intent: {data.get('intent', 'Unknown')}")
            print(f"   Advice: {data.get('advice', 'No advice')[:200]}...")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend server not running. Please start the backend first.")
    except Exception as e:
        print(f"❌ Error in AI copilot test: {e}")
    
    # Test 3: Emergency Advisor Chain
    print("\n3️⃣ Testing Emergency Advisor Chain...")
    try:
        response = requests.post(
            "http://localhost:8000/advise_pilot/",
            json=test_flight_data,
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Emergency Advisor Response:")
            print(f"   Advice: {data.get('advice', 'No advice')[:200]}...")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend server not running. Please start the backend first.")
    except Exception as e:
        print(f"❌ Error in emergency advisor test: {e}")
    
    # Test 4: Risk Explanation
    print("\n4️⃣ Testing Risk Explanation...")
    try:
        response = requests.post(
            "http://localhost:8000/explain_risk/",
            json={
                "flight_data": test_flight_data,
                "anomaly_description": "Pitot tubes iced over causing unreliable airspeed and autopilot disconnect at high altitude"
            },
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Risk Explanation Response:")
            print(f"   Explanation: {data.get('explanation', 'No explanation')[:200]}...")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Backend server not running. Please start the backend first.")
    except Exception as e:
        print(f"❌ Error in risk explanation test: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Air France Flight 447 Integration Test Complete!")
    print("\n📊 Key Features Tested:")
    print("   • Similar crash search functionality")
    print("   • AI copilot chat responses")
    print("   • Emergency advisor chain")
    print("   • Risk explanation capabilities")
    print("\n🚨 Historical Context:")
    print("   • Pitot tube icing detection")
    print("   • Unreliable airspeed procedures")
    print("   • High-altitude stall prevention")
    print("   • Alternative airspeed calculations")
    print("   • Autopilot management during sensor failures")

if __name__ == "__main__":
    asyncio.run(test_af447_integration()) 