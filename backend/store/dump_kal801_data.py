#!/usr/bin/env python3
"""
Comprehensive data dump script for Korean Air Flight 801.
Shows all data sources, storage locations, and usage in the AI Aircraft Crash Prevention system.
"""

import requests
import json
import sys

def print_section(title):
    """Print a formatted section header."""
    print("\n" + "="*80)
    print(f"📋 {title}")
    print("="*80)

def print_subsection(title):
    """Print a formatted subsection header."""
    print(f"\n🔹 {title}")
    print("-" * 60)

# 1. ORIGINAL SOURCE DATA (from store_kal801_data.py)
print_section("ORIGINAL KOREAN AIR FLIGHT 801 SOURCE DATA")

original_data = {
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

print("📄 Source File: store_kal801_data.py")
print("📄 Data Structure:")
print(json.dumps(original_data, indent=2))

# 2. MONGODB STORAGE DATA
print_section("MONGODB STORAGE DATA")

try:
    # Query the stored data via API
    response = requests.get("http://localhost:8000/similar_crashes/?query=Korean%20Air%20Flight%20801&top_k=1")
    if response.status_code == 200:
        results = response.json()["results"]
        if results:
            kal801_result = results[0]
            print("📊 Database Collection: flight_vectors")
            print("📊 Stored Document Structure:")
            print(f"   Flight ID: {kal801_result['flight_id']}")
            print(f"   Summary: {kal801_result['summary']}")
            print(f"   Similarity Score: {kal801_result['similarity']:.4f}")
            
            # Additional fields that would be in MongoDB (not returned by API)
            print("\n📊 Additional MongoDB Fields:")
            print("   - title: Korean Air Flight 801")
            print("   - date: 1997-08-06")
            print("   - location: Guam")
            print("   - passengers: 254")
            print("   - fatalities: 229")
            print("   - survivors: 25")
            print("   - primary_cause: Pilot error and navigational aid failure")
            print("   - key_factors: [array of 4 factors]")
            print("   - how_ai_copilot_could_help: [AI assistance description]")
            print("   - vector: [384-dimensional embedding vector]")
            print("   - embedding_summary: [concatenated text for embedding]")
        else:
            print("❌ No Korean Air Flight 801 data found in database")
    else:
        print(f"❌ Failed to query database: HTTP {response.status_code}")
except Exception as e:
    print(f"❌ Error querying database: {e}")

# 3. FRONTEND DISPLAY DATA
print_section("FRONTEND DISPLAY DATA")

frontend_data = {
    'CRASH_KAL801': {
        'title': 'Korean Air Flight 801 (Historical Crash)',
        'date': 'August 6, 1997',
        'location': 'Guam International Airport',
        'description': 'Controlled flight into terrain - 229 fatalities, 25 survivors',
        'status': 'Critical - Historical Reference'
    }
}

print("📄 Source File: frontend/src/pages/ChatPage.jsx")
print("📄 Flight Selection Dropdown Data:")
print(json.dumps(frontend_data, indent=2))

# 4. AI PROMPT INTEGRATION
print_section("AI PROMPT INTEGRATION")

print("📄 Source Files:")
print("   - backend/router_utils.py (intent classification)")
print("   - backend/langchain_utils.py (flight-specific prompts)")

print_subsection("Emergency Chain Integration")
emergency_prompt = """
## Flight-Specific Emergency Context:
- **KAL801/CRASH_KAL801**: Terrain proximity, glide slope failure, Guam approach

## Emergency Response Format:
🚨 **CRITICAL EMERGENCY** 🚨
**IMMEDIATE ACTION REQUIRED:**
[Specific action in CAPS]

**EMERGENCY PROCEDURES:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**CONTACT ATC IMMEDIATELY**
"""
print(emergency_prompt)

print_subsection("Status Update Chain Integration")
status_prompt = """
## Flight-Specific Emergency Context:
- **CRASH_KAL801**: Korean Air Flight 801 (1997) - Controlled flight into terrain on Guam approach due to descent below minimum safe altitude, non-functional glideslope, and poor crew resource management. 229 fatalities, 25 survivors.

## Historical Crash Reference - KAL801:
- **Date**: August 6, 1997
- **Location**: Guam International Airport
- **Primary Cause**: Pilot error and navigational aid failure
- **Key Factors**: Non-precision approach with out-of-service glideslope, descent below minimum safe altitude, captain fatigue, pilot misinterpretation of navigation signals
- **AI Copilot Solution**: Detect descent below safe altitude, issue immediate terrain pull-up alert, prompt for missed approach when glideslope signal weak/absent, enforce crew cross-checks
"""
print(status_prompt)

# 5. FALLBACK MESSAGES
print_section("FALLBACK MESSAGES")

fallback_messages = {
    "CRASH_KAL801": "🚨 HISTORICAL KAL801 REFERENCE 🚨\nThis flight pattern matches Korean Air Flight 801 (1997 Guam crash). Immediate terrain pull-up required. Verify glideslope status and initiate missed approach procedures."
}

print("📄 Source File: backend/router_utils.py")
print("📄 Fallback Message:")
print(json.dumps(fallback_messages, indent=2))

# 6. API ENDPOINTS
print_section("API ENDPOINTS")

endpoints = [
    {
        "endpoint": "POST /store_crash_data/",
        "description": "Stores Korean Air Flight 801 data with vector embeddings",
        "data_source": "store_kal801_data.py"
    },
    {
        "endpoint": "GET /similar_crashes/?query=Korean%20Air%20Flight%20801",
        "description": "Finds Korean Air Flight 801 in similarity search",
        "data_source": "MongoDB flight_vectors collection"
    },
    {
        "endpoint": "POST /chat/status_update/",
        "description": "AI copilot chat with intent classification",
        "data_source": "router_utils.py + langchain_utils.py"
    },
    {
        "endpoint": "POST /chat/divert_airport/",
        "description": "Airport diversion recommendations for KAL801",
        "data_source": "router_utils.py divert_airport chain"
    },
    {
        "endpoint": "POST /chat/system_status/",
        "description": "System status checks for KAL801",
        "data_source": "router_utils.py system_status chain"
    }
]

for endpoint in endpoints:
    print(f"🔗 {endpoint['endpoint']}")
    print(f"   Description: {endpoint['description']}")
    print(f"   Data Source: {endpoint['data_source']}")
    print()

# 7. TESTING DATA
print_section("TESTING DATA")

print("📄 Test Files:")
print("   - test_kal801_integration.py (comprehensive integration tests)")
print("   - test_intent_classification.py (intent classification tests)")

print_subsection("Sample Test Cases")
test_cases = [
    "terrain warning alert",
    "glideslope failure", 
    "descent below minimum altitude",
    "similar past incidents",
    "nearest airport for emergency landing"
]

for i, test_case in enumerate(test_cases, 1):
    print(f"   {i}. '{test_case}'")

# 8. DATA FLOW SUMMARY
print_section("DATA FLOW SUMMARY")

flow_steps = [
    "1. Original data defined in store_kal801_data.py",
    "2. Data sent to /store_crash_data/ endpoint",
    "3. store_crash_flight_data() function processes data",
    "4. Sentence transformer creates 384-dim vector embedding",
    "5. Complete document stored in MongoDB flight_vectors collection",
    "6. Frontend displays flight in dropdown via ChatPage.jsx",
    "7. AI prompts reference KAL801 in router_utils.py",
    "8. Intent classification routes to appropriate chains",
    "9. Similarity search finds KAL801 via vector embeddings",
    "10. Fallback messages provide emergency responses"
]

for step in flow_steps:
    print(f"   {step}")

print_section("COMPLETE DATA DUMP FINISHED")
print("✅ All Korean Air Flight 801 data sources and storage locations documented")
print("📁 Files containing KAL801 data:")
print("   - store_kal801_data.py (source data)")
print("   - backend/search_utils.py (storage function)")
print("   - backend/router_utils.py (AI prompts & fallbacks)")
print("   - backend/langchain_utils.py (flight-specific context)")
print("   - frontend/src/pages/ChatPage.jsx (UI display)")
print("   - MongoDB flight_vectors collection (database storage)") 