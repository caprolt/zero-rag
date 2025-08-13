#!/usr/bin/env python3
"""
Test script to upload a document through the API.
"""

import requests
import time

API_BASE_URL = "http://localhost:8000"

def test_document_upload():
    """Test document upload through the API."""
    print("🔍 Testing document upload through API...")
    print(f"API URL: {API_BASE_URL}")
    print("=" * 50)
    
    # Create a test file
    test_content = "This is a test document for upload testing. It contains some sample text to verify that the upload functionality is working correctly."
    
    # Test upload
    print("1. Testing document upload...")
    try:
        files = {"file": ("test_upload.txt", test_content, "text/plain")}
        response = requests.post(f"{API_BASE_URL}/documents/upload", files=files, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Document upload successful!")
            print(f"   Document ID: {result.get('document_id', 'N/A')}")
            print(f"   Filename: {result.get('filename', 'N/A')}")
            print(f"   Chunks created: {result.get('chunks_created', 'N/A')}")
            print(f"   Status: {result.get('status', 'N/A')}")
            return True
        else:
            print(f"❌ Document upload failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.RequestException as e:
        print(f"❌ Document upload failed: {e}")
        return False

def test_health_ping():
    """Test health ping."""
    print("2. Testing health ping...")
    try:
        response = requests.get(f"{API_BASE_URL}/health/ping", timeout=5)
        if response.status_code == 200:
            print("✅ Health ping successful!")
            return True
        else:
            print(f"❌ Health ping failed with status: {response.status_code}")
            return False
    except requests.RequestException as e:
        print(f"❌ Health ping failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting document upload test...")
    print("=" * 50)
    
    # Test health ping first
    health_ok = test_health_ping()
    
    if health_ok:
        # Test document upload
        upload_ok = test_document_upload()
        
        if upload_ok:
            print("\n🎉 Document upload test completed successfully!")
        else:
            print("\n❌ Document upload test failed.")
    else:
        print("\n❌ API is not responding. Please check if the API server is running.")
    
    print("=" * 50)
