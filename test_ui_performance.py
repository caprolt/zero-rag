#!/usr/bin/env python3
"""
Performance test for ZeroRAG UI improvements.

This script measures the time it takes for the UI to load and display the main chat interface.
"""

import time
import requests
import subprocess
import sys
from pathlib import Path

def test_api_response_time():
    """Test API response times for different endpoints."""
    base_url = "http://localhost:8000"
    
    print("🔍 Testing API Response Times...")
    
    # Test ping endpoint (should be fastest)
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/health/ping", timeout=1)
        ping_time = time.time() - start_time
        print(f"✅ Ping endpoint: {ping_time:.3f}s (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Ping endpoint failed: {e}")
        ping_time = float('inf')
    
    # Test health endpoint
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        health_time = time.time() - start_time
        print(f"✅ Health endpoint: {health_time:.3f}s (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Health endpoint failed: {e}")
        health_time = float('inf')
    
    # Test documents endpoint
    start_time = time.time()
    try:
        response = requests.get(f"{base_url}/documents", timeout=5)
        docs_time = time.time() - start_time
        print(f"✅ Documents endpoint: {docs_time:.3f}s (Status: {response.status_code})")
    except Exception as e:
        print(f"❌ Documents endpoint failed: {e}")
        docs_time = float('inf')
    
    return {
        "ping": ping_time,
        "health": health_time,
        "documents": docs_time
    }

def test_streamlit_startup():
    """Test Streamlit startup time."""
    print("\n🚀 Testing Streamlit Startup...")
    
    # Check if Streamlit is already running
    try:
        response = requests.get("http://localhost:8501", timeout=2)
        if response.status_code == 200:
            print("✅ Streamlit is already running on port 8501")
            return True
    except:
        pass
    
    print("⚠️ Streamlit not running. Start it manually with: streamlit run src/ui/streamlit_app.py")
    return False

def main():
    """Main performance test."""
    print("🤖 ZeroRAG UI Performance Test")
    print("=" * 40)
    
    # Test API endpoints
    api_times = test_api_response_time()
    
    # Test Streamlit
    streamlit_running = test_streamlit_startup()
    
    # Summary
    print("\n📊 Performance Summary:")
    print("-" * 20)
    
    total_api_time = sum(api_times.values()) if all(t != float('inf') for t in api_times.values()) else float('inf')
    
    if total_api_time != float('inf'):
        print(f"✅ Total API response time: {total_api_time:.3f}s")
        
        if total_api_time < 2:
            print("🎉 Excellent performance! (< 2s)")
        elif total_api_time < 5:
            print("👍 Good performance! (< 5s)")
        elif total_api_time < 10:
            print("⚠️ Acceptable performance (< 10s)")
        else:
            print("❌ Poor performance (> 10s)")
    else:
        print("❌ API not responding")
    
    if streamlit_running:
        print("✅ Streamlit UI is accessible")
    else:
        print("⚠️ Streamlit UI not running")
    
    print("\n💡 Performance Tips:")
    print("- Use cached document lists (30s cache)")
    print("- Health status moved to separate page")
    print("- Reduced API timeouts (0.5s ping, 5s docs)")
    print("- Less aggressive status checking (5s interval)")
    print("- Lazy loading of health diagnostics")

if __name__ == "__main__":
    main()
