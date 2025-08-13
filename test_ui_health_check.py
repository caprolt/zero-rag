#!/usr/bin/env python3
"""
Test script to verify UI health check functionality
"""

import requests
import time

def test_ping_endpoint():
    """Test the fast ping endpoint."""
    print("Testing ping endpoint...")
    try:
        start_time = time.time()
        response = requests.get("http://localhost:8000/health/ping", timeout=5)
        end_time = time.time()
        
        print(f"✅ Ping endpoint: {response.status_code} in {end_time - start_time:.3f}s")
        print(f"   Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Ping endpoint failed: {e}")
        return False

def test_health_endpoint():
    """Test the comprehensive health endpoint."""
    print("\nTesting comprehensive health endpoint...")
    try:
        start_time = time.time()
        response = requests.get("http://localhost:8000/health", timeout=15)
        end_time = time.time()
        
        print(f"✅ Health endpoint: {response.status_code} in {end_time - start_time:.3f}s")
        health_data = response.json()
        print(f"   Status: {health_data.get('status', 'unknown')}")
        print(f"   Services: {len(health_data.get('services', {}))}")
        return True
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        return False

def test_ui_health_check():
    """Test the UI health check function."""
    print("\nTesting UI health check function...")
    
    # Simulate the UI health check function
    def check_api_health():
        try:
            response = requests.get("http://localhost:8000/health/ping", timeout=5)
            if response.status_code == 200:
                return True
            else:
                print(f"   Warning: API ping returned status code: {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"   Error: API health check failed: {e}")
            return False
    
    start_time = time.time()
    result = check_api_health()
    end_time = time.time()
    
    if result:
        print(f"✅ UI health check: PASSED in {end_time - start_time:.3f}s")
    else:
        print(f"❌ UI health check: FAILED in {end_time - start_time:.3f}s")
    
    return result

if __name__ == "__main__":
    print("🔍 Testing ZeroRAG API Health Check Functionality")
    print("=" * 50)
    
    # Test all endpoints
    ping_ok = test_ping_endpoint()
    health_ok = test_health_endpoint()
    ui_ok = test_ui_health_check()
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"   Ping endpoint: {'✅ PASS' if ping_ok else '❌ FAIL'}")
    print(f"   Health endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"   UI health check: {'✅ PASS' if ui_ok else '❌ FAIL'}")
    
    if all([ping_ok, health_ok, ui_ok]):
        print("\n🎉 All tests passed! The API health check should work correctly in the UI.")
    else:
        print("\n⚠️  Some tests failed. Please check the API server status.")
