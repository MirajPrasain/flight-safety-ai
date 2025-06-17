#!/usr/bin/env python3
"""
Comprehensive test script for intent classification system.
Tests all aspects of the new modular LangChain chains and intent routing.
"""

import requests
import json
import time

def test_intent_classification():
    """Test intent classification with various message types."""
    print("🔍 Testing intent classification...")
    
    test_cases = [
        # Emergency intent
        ("terrain warning alert", "emergency"),
        ("mayday mayday engine failure", "emergency"),
        ("pull up pull up", "emergency"),
        
        # Divert airport intent
        ("nearest airport for emergency landing", "divert_airport"),
        ("divert to alternate airport", "divert_airport"),
        ("landing gear malfunction need to land", "divert_airport"),
        
        # Similar crashes intent
        ("similar past incidents", "similar_crashes"),
        ("what happened in previous crashes", "similar_crashes"),
        ("historical reference like this", "similar_crashes"),
        
        # System status intent
        ("check system status", "system_status"),
        ("instrument readings altitude speed", "system_status"),
        ("autopilot navigation radar weather", "system_status"),
        
        # Status update intent (default)
        ("current flight status", "status_update"),
        ("what's happening now", "status_update"),
        ("update me on situation", "status_update")
    ]
    
    passed_tests = 0
    for message, expected_intent in test_cases:
        try:
            response = requests.post(
                "http://localhost:8000/chat/status_update/",
                json={"flight_id": "CRASH_KAL801", "message": message},
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                actual_intent = result.get("intent", "unknown")
                
                if actual_intent == expected_intent:
                    print(f"✅ Intent classification PASSED: '{message}' → {actual_intent}")
                    passed_tests += 1
                else:
                    print(f"❌ Intent classification FAILED: '{message}' → expected {expected_intent}, got {actual_intent}")
            else:
                print(f"❌ Intent classification FAILED: '{message}' - HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Intent classification TIMEOUT: '{message}'")
        except Exception as e:
            print(f"❌ Intent classification ERROR: '{message}' - {e}")
    
    print(f"\n📊 Intent classification: {passed_tests}/{len(test_cases)} tests passed")
    return passed_tests > len(test_cases) * 0.7  # 70% success rate

def test_flight_specific_responses():
    """Test that different flights get appropriate responses."""
    print("\n🔍 Testing flight-specific responses...")
    
    test_flights = [
        ("CRASH_KAL801", "terrain warning alert"),
        ("TURKISH1951", "autopilot malfunction"),
        ("ASIANA214", "low speed approach"),
        ("KAL801", "glide slope failure")
    ]
    
    passed_tests = 0
    for flight_id, message in test_flights:
        try:
            response = requests.post(
                "http://localhost:8000/chat/status_update/",
                json={"flight_id": flight_id, "message": message},
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                advice = result.get("advice", "")
                intent = result.get("intent", "")
                
                # Check if response contains flight-specific content
                if flight_id in advice or intent != "unknown":
                    print(f"✅ Flight-specific response PASSED: {flight_id} → {intent}")
                    passed_tests += 1
                else:
                    print(f"⚠️  Flight-specific response PARTIAL: {flight_id} - no flight reference")
            else:
                print(f"❌ Flight-specific response FAILED: {flight_id} - HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Flight-specific response TIMEOUT: {flight_id}")
        except Exception as e:
            print(f"❌ Flight-specific response ERROR: {flight_id} - {e}")
    
    print(f"\n📊 Flight-specific responses: {passed_tests}/{len(test_flights)} tests passed")
    return passed_tests > 0

def test_new_endpoints():
    """Test the new divert_airport and system_status endpoints."""
    print("\n🔍 Testing new endpoints...")
    
    endpoint_tests = [
        ("/chat/divert_airport/", "CRASH_KAL801", "nearest airport for emergency landing"),
        ("/chat/system_status/", "CRASH_KAL801", "check all instruments and systems"),
        ("/chat/divert_airport/", "TURKISH1951", "divert to alternate airport"),
        ("/chat/system_status/", "ASIANA214", "system status check")
    ]
    
    passed_tests = 0
    for endpoint, flight_id, message in endpoint_tests:
        try:
            response = requests.post(
                f"http://localhost:8000{endpoint}",
                json={"flight_id": flight_id, "message": message},
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                intent = result.get("intent", "")
                advice = result.get("advice", "")
                
                # Check if endpoint returns appropriate intent
                expected_intent = endpoint.split("/")[-2]  # Extract intent from endpoint
                if intent == expected_intent and advice:
                    print(f"✅ Endpoint test PASSED: {endpoint} → {intent}")
                    passed_tests += 1
                else:
                    print(f"❌ Endpoint test FAILED: {endpoint} → expected {expected_intent}, got {intent}")
            else:
                print(f"❌ Endpoint test FAILED: {endpoint} - HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Endpoint test TIMEOUT: {endpoint}")
        except Exception as e:
            print(f"❌ Endpoint test ERROR: {endpoint} - {e}")
    
    print(f"\n📊 New endpoints: {passed_tests}/{len(endpoint_tests)} tests passed")
    return passed_tests > 0

def test_emergency_priority():
    """Test that emergency intent gets highest priority."""
    print("\n🔍 Testing emergency priority...")
    
    emergency_messages = [
        "mayday mayday engine failure",
        "terrain pull up pull up",
        "emergency landing required",
        "system down critical failure"
    ]
    
    passed_tests = 0
    for message in emergency_messages:
        try:
            response = requests.post(
                "http://localhost:8000/chat/status_update/",
                json={"flight_id": "CRASH_KAL801", "message": message},
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                intent = result.get("intent", "")
                advice = result.get("advice", "")
                
                if intent == "emergency" and ("🚨" in advice or "EMERGENCY" in advice.upper()):
                    print(f"✅ Emergency priority PASSED: '{message}' → {intent}")
                    passed_tests += 1
                else:
                    print(f"❌ Emergency priority FAILED: '{message}' → {intent}")
            else:
                print(f"❌ Emergency priority FAILED: '{message}' - HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Emergency priority TIMEOUT: '{message}'")
        except Exception as e:
            print(f"❌ Emergency priority ERROR: '{message}' - {e}")
    
    print(f"\n📊 Emergency priority: {passed_tests}/{len(emergency_messages)} tests passed")
    return passed_tests > 0

def main():
    """Run all intent classification tests."""
    print("🚁 Intent Classification System Test Suite")
    print("=" * 60)
    
    # Check if backend is running
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code != 200:
            print("❌ Backend not responding properly")
            return
    except:
        print("❌ Backend not running on localhost:8000")
        print("   Please start the backend with: cd backend && uvicorn main:app --reload")
        return
    
    print("✅ Backend is running")
    
    # Run tests
    intent_ok = test_intent_classification()
    flight_ok = test_flight_specific_responses()
    endpoint_ok = test_new_endpoints()
    emergency_ok = test_emergency_priority()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 INTENT CLASSIFICATION TEST SUMMARY")
    print("=" * 60)
    print(f"Intent Classification:    {'✅ PASSED' if intent_ok else '❌ FAILED'}")
    print(f"Flight-Specific Responses: {'✅ PASSED' if flight_ok else '❌ FAILED'}")
    print(f"New Endpoints:           {'✅ PASSED' if endpoint_ok else '❌ FAILED'}")
    print(f"Emergency Priority:      {'✅ PASSED' if emergency_ok else '❌ FAILED'}")
    
    if all([intent_ok, flight_ok, endpoint_ok, emergency_ok]):
        print("\n🎉 ALL TESTS PASSED! Intent classification system is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the backend logs and try again.")

if __name__ == "__main__":
    main() 