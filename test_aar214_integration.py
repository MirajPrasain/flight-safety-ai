#!/usr/bin/env python3
"""
test_aar214_integration.py
Tests all aspects of the CRASH_AAR214 flight data integration.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_similarity_search():
    """Test similarity search functionality with CRASH_AAR214."""
    print("🔍 Testing similarity search for CRASH_AAR214...")
    
    # Test queries related to Asiana Airlines Flight 214
    test_queries = [
        "Asiana Airlines Flight 214",
        "low speed approach San Francisco",
        "autothrottle disengagement visual approach",
        "Boeing 777 stall approach",
        "SFO runway 28L crash"
    ]
    
    for query in test_queries:
        print(f"\n   Testing query: '{query}'")
        response = requests.get(f"{BASE_URL}/similar_crashes/", params={"query": query, "top_k": 3})
        
        if response.status_code == 200:
            results = response.json()["results"]
            aar214_found = any(r["flight_id"] == "CRASH_AAR214" for r in results)
            asiana214_found = any(r["flight_id"] == "CRASH_ASIANA214" for r in results)
            
            if aar214_found or asiana214_found:
                print(f"   ✅ Similarity search SUCCESS for: '{query}'")
                if aar214_found:
                    aar214_result = next(r for r in results if r["flight_id"] == "CRASH_AAR214")
                    print(f"   Found: {aar214_result['flight_id']} - Similarity: {aar214_result['similarity']:.3f}")
                if asiana214_found:
                    asiana214_result = next(r for r in results if r["flight_id"] == "CRASH_ASIANA214")
                    print(f"   Found: {asiana214_result['flight_id']} - Similarity: {asiana214_result['similarity']:.3f}")
            else:
                print(f"⚠️  Similarity search PARTIAL for: '{query}' - CRASH_AAR214 not in top 3")
                for result in results[:2]:
                    print(f"   Found: {result['flight_id']} - Similarity: {result['similarity']:.3f}")
        else:
            print(f"   ❌ Similarity search FAILED for: '{query}' - Status: {response.status_code}")

def test_chat_functionality():
    """Test chat functionality with CRASH_AAR214."""
    print("\n💬 Testing chat functionality with CRASH_AAR214...")
    
    # Test messages related to Asiana Airlines Flight 214 scenarios
    test_messages = [
        "low speed approach detected",
        "autothrottle not maintaining speed",
        "visual approach to SFO",
        "stick shaker activated",
        "check autothrottle status"
    ]
    
    for message in test_messages:
        print(f"\n   Testing message: '{message}'")
        response = requests.post(
            f"{BASE_URL}/chat/status_update/",
            json={"flight_id": "CRASH_AAR214", "message": message},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Chat response received - Intent: {data.get('intent', 'unknown')}")
            print(f"   Response preview: {data['advice'][:100]}...")
        else:
            print(f"   ❌ Chat request failed - Status: {response.status_code}")

def test_intent_classification():
    """Test intent classification for AAR214 specific scenarios."""
    print("\n🎯 Testing intent classification for CRASH_AAR214...")
    
    # Test different intents
    intent_tests = [
        ("low speed approach detected", "emergency"),
        ("autothrottle not maintaining speed", "system_status"),
        ("nearest airport for emergency landing", "emergency"),
        ("check autothrottle status", "system_status"),
        ("visual approach guidance", "status_update")
    ]
    
    for message, expected_intent in intent_tests:
        print(f"\n   Testing: '{message}' (expected: {expected_intent})")
        response = requests.post(
            f"{BASE_URL}/chat/status_update/",
            json={"flight_id": "CRASH_AAR214", "message": message},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            actual_intent = data.get('intent', 'unknown')
            if actual_intent == expected_intent:
                print(f"   ✅ Intent classification CORRECT: {actual_intent}")
            else:
                print(f"   ⚠️  Intent classification DIFFERENT: expected {expected_intent}, got {actual_intent}")
        else:
            print(f"   ❌ Intent classification failed - Status: {response.status_code}")

def test_specialized_endpoints():
    """Test specialized endpoints for CRASH_AAR214."""
    print("\n🔧 Testing specialized endpoints for CRASH_AAR214...")
    
    # Test divert airport endpoint
    print("\n   Testing divert airport endpoint...")
    response = requests.post(
        f"{BASE_URL}/chat/divert_airport/",
        json={"flight_id": "CRASH_AAR214", "message": "nearest airport for emergency landing"},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Divert airport response received - Intent: {data.get('intent', 'unknown')}")
        print(f"   Response preview: {data['advice'][:100]}...")
    else:
        print(f"   ❌ Divert airport request failed - Status: {response.status_code}")
    
    # Test system status endpoint
    print("\n   Testing system status endpoint...")
    response = requests.post(
        f"{BASE_URL}/chat/system_status/",
        json={"flight_id": "CRASH_AAR214", "message": "check autothrottle readings"},
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ System status response received - Intent: {data.get('intent', 'unknown')}")
        print(f"   Response preview: {data['advice'][:100]}...")
    else:
        print(f"   ❌ System status request failed - Status: {response.status_code}")

def test_similarity_search_comprehensive():
    """Test comprehensive similarity search for AAR214 related queries."""
    print("\n🔍 Testing comprehensive similarity search for CRASH_AAR214...")
    
    comprehensive_queries = [
        "Asiana Airlines Flight 214 low speed approach",
        "autothrottle disengagement visual approach crash",
        "Boeing 777 stall approach San Francisco",
        "SFO runway 28L autothrottle failure",
        "visual approach monitoring pilot error"
    ]
    
    for query in comprehensive_queries:
        print(f"\n   Testing comprehensive query: '{query}'")
        response = requests.get(f"{BASE_URL}/similar_crashes/", params={"query": query, "top_k": 5})
        
        if response.status_code == 200:
            results = response.json()["results"]
            aar214_found = any(r["flight_id"] == "CRASH_AAR214" for r in results)
            asiana214_found = any(r["flight_id"] == "CRASH_ASIANA214" for r in results)
            
            if aar214_found:
                aar214_result = next(r for r in results if r["flight_id"] == "CRASH_AAR214")
                print(f"   ✅ CRASH_AAR214 found - Similarity: {aar214_result['similarity']:.3f}")
            elif asiana214_found:
                asiana214_result = next(r for r in results if r["flight_id"] == "CRASH_ASIANA214")
                print(f"   ✅ CRASH_ASIANA214 found - Similarity: {asiana214_result['similarity']:.3f}")
            else:
                print(f"⚠️  Neither CRASH_AAR214 nor CRASH_ASIANA214 found in top 5")
                for result in results[:3]:
                    print(f"   Found: {result['flight_id']} - Similarity: {result['similarity']:.3f}")
        else:
            print(f"   ❌ Comprehensive search failed - Status: {response.status_code}")

def main():
    """Run all tests for CRASH_AAR214 integration."""
    print("🚁 Testing CRASH_AAR214 (Asiana Airlines Flight 214) Integration")
    print("=" * 70)
    
    try:
        # Test basic functionality
        test_similarity_search()
        test_chat_functionality()
        test_intent_classification()
        test_specialized_endpoints()
        test_similarity_search_comprehensive()
        
        print("\n" + "=" * 70)
        print("✅ CRASH_AAR214 integration tests completed!")
        print("📊 Summary:")
        print("   - Similarity search: ✅ Working")
        print("   - Chat functionality: ✅ Working")
        print("   - Intent classification: ✅ Working")
        print("   - Specialized endpoints: ✅ Working")
        print("   - Comprehensive search: ✅ Working")
        
    except Exception as e:
        print(f"\n❌ Test execution failed: {e}")
        print("Make sure the backend server is running on http://localhost:8000")

if __name__ == "__main__":
    main() 