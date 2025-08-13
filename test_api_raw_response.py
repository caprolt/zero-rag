#!/usr/bin/env python3
"""
Test to see the raw API response.
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_raw_response():
    """Test to see the raw API response."""
    
    print("🔍 Testing Raw API Response")
    print("=" * 50)
    
    # Get the document ID
    response = requests.get(f"{API_BASE_URL}/documents")
    if response.status_code == 200:
        documents = response.json().get("documents", [])
        
        # Find our test document
        target_doc = None
        for doc in documents:
            if "test_new_document.txt" in doc.get("filename", ""):
                target_doc = doc
                break
        
        if target_doc:
            document_id = target_doc.get("document_id")
            print(f"Document ID: {document_id}")
            
            # Test with filtering
            query_data = {
                "query": "document filtering",
                "document_ids": [document_id],
                "top_k": 5,
                "score_threshold": 0.3
            }
            
            response = requests.post(f"{API_BASE_URL}/query", json=query_data)
            if response.status_code == 200:
                result = response.json()
                print(f"Raw response:")
                print(json.dumps(result, indent=2))
            else:
                print(f"❌ Query failed: {response.status_code}")
                print(f"Error: {response.text}")
        else:
            print("❌ Target document not found")
    else:
        print(f"❌ Failed to get documents: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🏁 Raw response test completed!")

if __name__ == "__main__":
    test_raw_response()
