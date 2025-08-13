#!/usr/bin/env python3
"""
Test script to verify that file uploads no longer include UUID prefixes in filenames.
"""

import requests
import time
import os
from pathlib import Path

# Configuration
API_BASE_URL = "http://localhost:8000"
TEST_FILENAME = "test_no_uuid_upload.txt"
TEST_CONTENT = "This is a test file to verify that uploads no longer include UUID prefixes in filenames."

def create_test_file():
    """Create a test file for upload."""
    with open(TEST_FILENAME, "w") as f:
        f.write(TEST_CONTENT)
    print(f"Created test file: {TEST_FILENAME}")

def cleanup_test_file():
    """Clean up the test file."""
    if os.path.exists(TEST_FILENAME):
        os.remove(TEST_FILENAME)
        print(f"Cleaned up test file: {TEST_FILENAME}")

def check_api_health():
    """Check if the API is running."""
    try:
        response = requests.get(f"{API_BASE_URL}/health/ping", timeout=5)
        return response.status_code == 200
    except:
        return False

def upload_file():
    """Upload the test file and return the response."""
    with open(TEST_FILENAME, "rb") as f:
        files = {"file": (TEST_FILENAME, f, "text/plain")}
        response = requests.post(f"{API_BASE_URL}/documents/upload", files=files, timeout=60)
        return response.json()

def check_uploaded_file():
    """Check if the uploaded file exists without UUID prefix."""
    upload_dir = Path("data/uploads")
    
    # Look for files that start with our test filename (no UUID prefix)
    matching_files = list(upload_dir.glob(f"{TEST_FILENAME}*"))
    
    if matching_files:
        print(f"Found uploaded file(s): {[f.name for f in matching_files]}")
        
        # Check if any file has no UUID prefix (should be exactly our filename)
        for file_path in matching_files:
            if file_path.name == TEST_FILENAME:
                print("✅ SUCCESS: File uploaded without UUID prefix!")
                return True
            elif file_path.name.startswith(TEST_FILENAME + "_"):
                print(f"✅ SUCCESS: File uploaded with number suffix (conflict resolution): {file_path.name}")
                return True
        
        print("❌ FAILURE: All uploaded files still have UUID prefixes")
        return False
    else:
        print("❌ FAILURE: No uploaded files found")
        return False

def main():
    """Main test function."""
    print("🧪 Testing file upload without UUID prefix...")
    
    # Check API health
    if not check_api_health():
        print("❌ API is not running. Please start the API server first.")
        return False
    
    print("✅ API is running")
    
    # Create test file
    create_test_file()
    
    try:
        # Upload file
        print("📤 Uploading test file...")
        upload_result = upload_file()
        
        if "error" in upload_result:
            print(f"❌ Upload failed: {upload_result['error']}")
            return False
        
        print(f"✅ Upload successful. Document ID: {upload_result.get('document_id')}")
        
        # Wait a moment for processing
        print("⏳ Waiting for file processing...")
        time.sleep(2)
        
        # Check if file was uploaded without UUID prefix
        success = check_uploaded_file()
        
        return success
        
    finally:
        # Clean up test file
        cleanup_test_file()

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 Test PASSED: Files are now uploaded without UUID prefixes!")
    else:
        print("\n💥 Test FAILED: Files still have UUID prefixes or upload failed.")
