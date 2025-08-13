#!/usr/bin/env python3
"""
Test script to verify ZeroRAG API server functionality

This script tests the API server startup and basic functionality.
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

def test_api_server():
    """Test the API server startup and basic functionality."""
    print("🧪 Testing ZeroRAG API Server...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("src/api/main.py").exists():
        print("❌ Error: src/api/main.py not found. Please run this script from the project root.")
        return False
    
    # Start API server
    print("🚀 Starting API server...")
    try:
        api_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "src.api.main:app", 
            "--host", "localhost", 
            "--port", "8000"
        ], cwd=Path.cwd(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(5)
        
        # Test health endpoint
        print("🔍 Testing health endpoint...")
        try:
            response = requests.get("http://localhost:8000/health/ping", timeout=10)
            if response.status_code == 200:
                print("✅ Health endpoint working!")
            else:
                print(f"❌ Health endpoint returned status {response.status_code}")
                return False
        except requests.RequestException as e:
            print(f"❌ Health endpoint failed: {e}")
            return False
        
        # Test main health endpoint
        print("🔍 Testing main health endpoint...")
        try:
            response = requests.get("http://localhost:8000/health", timeout=10)
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Main health endpoint working! Status: {health_data.get('status', 'unknown')}")
            else:
                print(f"❌ Main health endpoint returned status {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ Main health endpoint failed: {e}")
        
        # Test root endpoint
        print("🔍 Testing root endpoint...")
        try:
            response = requests.get("http://localhost:8000/", timeout=10)
            if response.status_code == 200:
                root_data = response.json()
                print(f"✅ Root endpoint working! API: {root_data.get('name', 'unknown')}")
            else:
                print(f"❌ Root endpoint returned status {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ Root endpoint failed: {e}")
        
        # Test file validation endpoint
        print("🔍 Testing file validation endpoint...")
        try:
            test_data = {
                "filename": "test.txt",
                "file_size": 1024,
                "content_type": "text/plain"
            }
            response = requests.post("http://localhost:8000/documents/validate", json=test_data, timeout=10)
            if response.status_code == 200:
                validation_data = response.json()
                print(f"✅ File validation endpoint working! Valid: {validation_data.get('is_valid', False)}")
            else:
                print(f"❌ File validation endpoint returned status {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ File validation endpoint failed: {e}")
        
        # Stop the server
        print("🛑 Stopping API server...")
        api_process.terminate()
        api_process.wait(timeout=10)
        
        print("=" * 50)
        print("✅ API server test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_api_server()
    sys.exit(0 if success else 1)
