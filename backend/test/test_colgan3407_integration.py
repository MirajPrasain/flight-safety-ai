#!/usr/bin/env python3
"""
Test script to verify Colgan Air Flight 3407 crash data integration
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

# Test data for Colgan Air Flight 3407 scenario
test_flight_data = {
    "flight_id": "CRASH_COLGAN3407",
    "aircraft_type": "Bombardier DHC-8-402",
    "timestamp": "2009-02-12T22:17:00Z",
    "location": {
        "altitude_ft": 2300,
        "latitude": 42.9406,
        "longitude": -78.7367
    },
    "speed": {
        "airspeed_knots": 130,  # Low approach speed
        "vertical_speed_fpm": -700
    },
    "engine": {
        "engine_1_rpm": 85,
        "engine_2_rpm": 85
    },
    "aircraft_systems": {
        "landing_gear_status": "Extended",
        "flap_setting": "Full",
        "autopilot_engaged": False,
        "warnings": ["Stall Warning", "Low Airspeed"]
    },
    "environment": {
        "wind_speed_knots": 15,
        "wind_direction_deg": 270,
        "temperature_c": -2,
        "visibility_miles": 2,
        "precipitation": "Light Snow",
        "terrain_proximity_ft": 500
    },
    "pilot_actions": {
        "throttle_percent": 60,
        "pitch_deg": -2,
        "roll_deg": 0,
        "yaw_deg": 0
    }
}

async def test_colgan3407_integration():
    """Test the Colgan Air Flight 3407 crash data integration."""
    print("🧪 Testing Colgan Air Flight 3407 Integration")
    print("=" * 50)
    
    # Test 1: Similar crash search
    print("\n1️⃣ Testing Similar Crash Search...")
    try:
        results = await search_similar_flights(
            query_summary="stall on approach due to low airspeed and improper recovery",
            top_k=3
        )
        
        print(f"✅ Found {len(results)} similar crashes")
        for i, result in enumerate(results, 1):
            print(f"   {i}. {result.get('title', 'Unknown')} - {result.get('date', 'Unknown')}")
            if result.get('flight_id') == 'CRASH_COLGAN3407':
                print(f"      🎯 Colgan Air Flight 3407 found in results!")
        
    except Exception as e:
        print(f"❌ Error in similar crash search: {e}")
    
    # Test 2: AI Copilot Chat Response
    print("\n2️⃣ Testing AI Copilot Chat Response...")
    try:
        response = requests.post(
            "http://localhost:8000/chat/status_update/",
            json={
                "flight_id": "CRASH_COLGAN3407",
                "message": "Airspeed is getting low on approach, stall warning just activated"
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
                "anomaly_description": "Airspeed below minimum approach speed with stall warning active"
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
    print("🎯 Colgan Air Flight 3407 Integration Test Complete!")
    print("\n📊 Key Features Tested:")
    print("   • Similar crash search functionality")
    print("   • AI copilot chat responses")
    print("   • Emergency advisor chain")
    print("   • Risk explanation capabilities")
    print("\n🚨 Historical Context:")
    print("   • Stall prevention during approach")
    print("   • Airspeed monitoring critical")
    print("   • Sterile cockpit enforcement")
    print("   • Proper stall recovery procedures")

if __name__ == "__main__":
    asyncio.run(test_colgan3407_integration()) 