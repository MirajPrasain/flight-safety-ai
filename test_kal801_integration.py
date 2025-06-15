#!/usr/bin/env python3
"""
Comprehensive test script for Korean Air Flight 801 integration.
Tests all aspects of the CRASH_KAL801 flight data integration.
"""

import requests
import json
import time

def test_crash_data_storage():
    """Test if the crash data is properly stored."""
    print("🔍 Testing crash data storage...")
    
    try:
        response = requests.get("http://localhost:8000/similar_crashes/?query=Korean%20Air%20Flight%20801&top_k=1")
        if response.status_code == 200:
            results = response.json()["results"]
            if results and results[0]["flight_id"] == "CRASH_KAL801":
                print("✅ Crash data storage test PASSED")
                print(f"   Found: {results[0]['flight_id']} - Similarity: {results[0]['similarity']:.3f}")
                return True
            else:
                print("❌ Crash data storage test FAILED - Data not found")
                return False
        else:
            print(f"❌ Crash data storage test FAILED - HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Crash data storage test FAILED - Error: {e}")
        return False

def test_chat_functionality():
    """Test chat functionality with CRASH_KAL801."""
    print("\n🔍 Testing chat functionality...")
    
    test_messages = [
        "terrain warning alert",
        "glideslope failure", 
        "descent below minimum altitude",
        "crew communication issues"
    ]
    
    passed_tests = 0
    for message in test_messages:
        try:
            response = requests.post(
                "http://localhost:8000/chat/status_update/",
                json={"flight_id": "CRASH_KAL801", "message": message},
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                if "advice" in result and "CRASH_KAL801" in result["advice"]:
                    print(f"✅ Chat test PASSED for: '{message}'")
                    passed_tests += 1
                else:
                    print(f"⚠️  Chat test PARTIAL for: '{message}' - No CRASH_KAL801 reference")
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
        "terrain proximity descent below glide slope",
        "Korean Air Guam crash 1997",
        "non-functional glideslope approach",
        "crew resource management failure"
    ]
    
    passed_tests = 0
    for query in test_queries:
        try:
            response = requests.get(f"http://localhost:8000/similar_crashes/?query={query}&top_k=3")
            if response.status_code == 200:
                results = response.json()["results"]
                kal801_found = any(r["flight_id"] == "CRASH_KAL801" for r in results)
                if kal801_found:
                    kal801_result = next(r for r in results if r["flight_id"] == "CRASH_KAL801")
                    print(f"✅ Similarity search PASSED for: '{query}'")
                    print(f"   CRASH_KAL801 similarity: {kal801_result['similarity']:.3f}")
                    passed_tests += 1
                else:
                    print(f"⚠️  Similarity search PARTIAL for: '{query}' - CRASH_KAL801 not in top 3")
            else:
                print(f"❌ Similarity search FAILED for: '{query}' - HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Similarity search FAILED for: '{query}' - Error: {e}")
    
    print(f"\n📊 Similarity search: {passed_tests}/{len(test_queries)} tests passed")
    return passed_tests > 0

def main():
    """Run all integration tests."""
    print("🚁 Korean Air Flight 801 Integration Test Suite")
    print("=" * 50)
    
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
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 INTEGRATION TEST SUMMARY")
    print("=" * 50)
    print(f"Crash Data Storage: {'✅ PASSED' if storage_ok else '❌ FAILED'}")
    print(f"Chat Functionality:  {'✅ PASSED' if chat_ok else '❌ FAILED'}")
    print(f"Similarity Search:   {'✅ PASSED' if search_ok else '❌ FAILED'}")
    
    if all([storage_ok, chat_ok, search_ok]):
        print("\n🎉 ALL TESTS PASSED! Korean Air Flight 801 integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please check the backend logs and try again.")

if __name__ == "__main__":
    main() 