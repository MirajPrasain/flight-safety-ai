#!/usr/bin/env python3
"""
Comprehensive test script for Turkish Airlines Flight 1951 integration.
Tests all aspects of the CRASH_THY1951 flight data integration.
"""

import requests
import json
import time

def test_crash_data_storage():
    """Test if the crash data is properly stored."""
    print("🔍 Testing crash data storage...")
    
    try:
        response = requests.get("http://localhost:8000/similar_crashes/?query=Turkish%20Airlines%20Flight%201951&top_k=5")
        if response.status_code == 200:
            results = response.json()["results"]
            # Check for both possible Turkish Airlines Flight 1951 entries
            thy1951_found = any(r["flight_id"] == "CRASH_THY1951" for r in results)
            turkish1951_found = any(r["flight_id"] == "CRASH_TURKISH1951" for r in results)
            
            if thy1951_found or turkish1951_found:
                print("✅ Crash data storage test PASSED")
                if thy1951_found:
                    thy1951_result = next(r for r in results if r["flight_id"] == "CRASH_THY1951")
                    print(f"   Found: {thy1951_result['flight_id']} - Similarity: {thy1951_result['similarity']:.3f}")
                if turkish1951_found:
                    turkish1951_result = next(r for r in results if r["flight_id"] == "CRASH_TURKISH1951")
                    print(f"   Found: {turkish1951_result['flight_id']} - Similarity: {turkish1951_result['similarity']:.3f}")
                return True
            else:
                print("❌ Crash data storage test FAILED - No Turkish Airlines Flight 1951 data found")
                return False
        else:
            print(f"❌ Crash data storage test FAILED - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Crash data storage test FAILED - Error: {e}")
        return False

def test_chat_functionality():
    """Test chat functionality with CRASH_THY1951."""
    print("\n🔍 Testing chat functionality...")
    
    test_messages = [
        "stall alert autothrottle reduced power",
        "radio altimeter showing incorrect readings", 
        "autothrottle cut engine power to idle",
        "stick shaker activated"
    ]
    
    passed_tests = 0
    for message in test_messages:
        try:
            response = requests.post(
                "http://localhost:8000/chat/status_update/",
                json={"flight_id": "CRASH_THY1951", "message": message},
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                if "advice" in result and "intent" in result:
                    print(f"✅ Chat test PASSED for: '{message}' → {result['intent']}")
                    passed_tests += 1
                else:
                    print(f"⚠️  Chat test PARTIAL for: '{message}' - Missing fields")
            else:
                print(f"❌ Chat test FAILED for: '{message}' - HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"⏰ Chat test TIMEOUT for: '{message}' - AI processing slow")
        except Exception as e:
            print(f"❌ Chat test FAILED for: '{message}' - Error: {e}")
    
    print(f"\n📊 Chat functionality: {passed_tests}/{len(test_messages)} tests passed")
    return passed_tests > 0

def test_similarity_search():
    """Test similarity search with various queries."""
    print("\n🔍 Testing similarity search...")
    
    test_queries = [
        "Turkish Airlines Flight 1951 radio altimeter",
        "faulty altimeter autothrottle stall",
        "Amsterdam Schiphol approach crash",
        "radio altimeter failure pilot error"
    ]
    
    passed_tests = 0
    for query in test_queries:
        try:
            response = requests.get(f"http://localhost:8000/similar_crashes/?query={query}&top_k=3")
            if response.status_code == 200:
                results = response.json()["results"]
                thy1951_found = any(r["flight_id"] == "CRASH_THY1951" for r in results)
                if thy1951_found:
                    thy1951_result = next(r for r in results if r["flight_id"] == "CRASH_THY1951")
                    print(f"✅ Similarity search PASSED for: '{query}'")
                    print(f"   CRASH_THY1951 similarity: {thy1951_result['similarity']:.3f}")
                    passed_tests += 1
                else:
                    print(f"⚠️  Similarity search PARTIAL for: '{query}' - CRASH_THY1951 not in top 3")
            else:
                print(f"❌ Similarity search FAILED for: '{query}' - HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Similarity search FAILED for: '{query}' - Error: {e}")
    
    print(f"\n📊 Similarity search: {passed_tests}/{len(test_queries)} tests passed")
    return passed_tests > 0

def test_intent_classification():
    """Test intent classification for THY1951 specific scenarios."""
    print("\n🔍 Testing intent classification...")
    
    test_cases = [
        ("stall alert autothrottle reduced power", "emergency"),
        ("radio altimeter showing incorrect readings", "system_status"),
        ("nearest airport for emergency landing", "divert_airport"),
        ("check all instruments and systems", "system_status")
    ]
    
    passed_tests = 0
    for message, expected_intent in test_cases:
        try:
            response = requests.post(
                "http://localhost:8000/chat/status_update/",
                json={"flight_id": "CRASH_THY1951", "message": message},
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

def test_new_endpoints():
    """Test the new divert_airport and system_status endpoints."""
    print("\n🔍 Testing new endpoints...")
    
    endpoint_tests = [
        ("/chat/divert_airport/", "CRASH_THY1951", "nearest airport for emergency landing"),
        ("/chat/system_status/", "CRASH_THY1951", "check radio altimeter readings")
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

def main():
    """Run all integration tests."""
    print("🚁 Turkish Airlines Flight 1951 Integration Test Suite")
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
    storage_ok = test_crash_data_storage()
    chat_ok = test_chat_functionality()
    search_ok = test_similarity_search()
    intent_ok = test_intent_classification()
    endpoint_ok = test_new_endpoints()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    print(f"Crash Data Storage:    {'✅ PASSED' if storage_ok else '❌ FAILED'}")
    print(f"Chat Functionality:     {'✅ PASSED' if chat_ok else '❌ FAILED'}")
    print(f"Similarity Search:      {'✅ PASSED' if search_ok else '❌ FAILED'}")
    print(f"Intent Classification:  {'✅ PASSED' if intent_ok else '❌ FAILED'}")
    print(f"New Endpoints:          {'✅ PASSED' if endpoint_ok else '❌ FAILED'}")
    
    if all([storage_ok, chat_ok, search_ok, intent_ok, endpoint_ok]):
        print("\n🎉 ALL TESTS PASSED! Turkish Airlines Flight 1951 integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the backend logs and try again.")

if __name__ == "__main__":
    main() 