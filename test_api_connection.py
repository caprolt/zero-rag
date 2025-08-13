#!/usr/bin/env python3
"""
Test script to verify API connection and document listing functionality.
"""

import requests
import time
import sys

API_BASE_URL = "http://localhost:8000"

def test_api_connection():
    """Test the API connection and document listing."""
    print("🔍 Testing ZeroRAG API connection...")
    print(f"API URL: {API_BASE_URL}")
    print("=" * 50)
    
    # Test 1: Health ping
    print("1. Testing health ping...")
    try:
        response = requests.get(f"{API_BASE_URL}/health/ping", timeout=10)
        if response.status_code == 200:
            print("✅ Health ping successful!")
        else:
            print(f"❌ Health ping failed with status: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Health ping failed: {e}")
        return False
    
    # Test 2: Full health check
    print("\n2. Testing full health check...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ Health check successful!")
            print(f"   Status: {health_data.get('status', 'Unknown')}")
            print(f"   Uptime: {health_data.get('uptime', 0):.1f} seconds")
            
            # Show service status
            services = health_data.get("services", {})
            if services:
                print("   Services:")
                for service, info in services.items():
                    status = info.get("status", "unknown")
                    print(f"     - {service}: {status}")
        else:
            print(f"❌ Health check failed with status: {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ Health check failed: {e}")
    
    # Test 3: Document listing
    print("\n3. Testing document listing...")
    try:
        response = requests.get(f"{API_BASE_URL}/documents", timeout=10)
        if response.status_code == 200:
            documents_data = response.json()
            documents = documents_data.get("documents", [])
            print(f"✅ Document listing successful!")
            print(f"   Total documents: {len(documents)}")
            
            if documents:
                print("   Documents:")
                for doc in documents:
                    filename = doc.get("filename", "Unknown")
                    doc_id = doc.get("document_id", "")
                    chunks = doc.get("chunks_count", 0)
                    print(f"     - {filename} (ID: {doc_id}, Chunks: {chunks})")
            else:
                print("   No documents found")
        else:
            print(f"❌ Document listing failed with status: {response.status_code}")
    except requests.RequestException as e:
        print(f"❌ Document listing failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 API connection test completed!")
    return True

def wait_for_api(max_wait=60):
    """Wait for the API to become available."""
    print(f"⏳ Waiting for API to become available (max {max_wait}s)...")
    print("💡 Note: The API server typically takes 30-45 seconds to start up")
    
    for i in range(max_wait):
        try:
            response = requests.get(f"{API_BASE_URL}/health/ping", timeout=5)
            if response.status_code == 200:
                print(f"✅ API is available after {i+1} seconds!")
                return True
        except:
            pass
        
        if (i + 1) % 10 == 0:
            print(f"⏳ Still waiting... ({i+1}/{max_wait}s)")
        time.sleep(1)
    
    print(f"❌ API did not become available within {max_wait} seconds")
    return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--wait":
        # Wait for API to become available first
        if wait_for_api():
            test_api_connection()
        else:
            print("💡 Try starting the API server with: python start_app.py")
            sys.exit(1)
    else:
        # Test immediately
        test_api_connection()
