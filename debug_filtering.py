#!/usr/bin/env python3
"""
Debug script to understand the filtering issue.
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def debug_filtering():
    """Debug the filtering issue."""
    
    print("🔍 Debugging Document Filtering")
    print("=" * 50)
    
    document_id = "29b07c26-271d-4299-a612-4e5d07f6e411"
    
    # Test 1: Search without any filtering
    print("1. Testing search without filtering...")
    query_data = {
        "query": "document filtering",
        "top_k": 10,
        "score_threshold": 0.1
    }
    
    response = requests.post(f"{API_BASE_URL}/query", json=query_data)
    if response.status_code == 200:
        result = response.json()
        sources = result.get('sources', [])
        print(f"   Sources found: {len(sources)}")
        
        for i, source in enumerate(sources):
            print(f"   Source {i+1}: {source.get('filename', 'Unknown')} (Score: {source.get('relevance_score', 0):.3f})")
            print(f"     Preview: {source.get('content_preview', 'No preview')[:100]}...")
    else:
        print(f"   ❌ Query failed: {response.status_code}")
    
    # Test 2: Search with document filtering
    print(f"\n2. Testing search with document filtering (ID: {document_id})...")
    query_data = {
        "query": "document filtering",
        "document_ids": [document_id],
        "top_k": 10,
        "score_threshold": 0.1
    }
    
    response = requests.post(f"{API_BASE_URL}/query", json=query_data)
    if response.status_code == 200:
        result = response.json()
        sources = result.get('sources', [])
        print(f"   Sources found: {len(sources)}")
        
        for i, source in enumerate(sources):
            print(f"   Source {i+1}: {source.get('filename', 'Unknown')} (Score: {source.get('relevance_score', 0):.3f})")
            print(f"     Preview: {source.get('content_preview', 'No preview')[:100]}...")
    else:
        print(f"   ❌ Query failed: {response.status_code}")
    
    # Test 3: Check if the document ID exists in the documents list
    print(f"\n3. Checking if document ID exists in documents list...")
    response = requests.get(f"{API_BASE_URL}/documents")
    if response.status_code == 200:
        documents = response.json().get("documents", [])
        found = False
        for doc in documents:
            if doc.get("document_id") == document_id:
                print(f"   ✅ Found document: {doc.get('filename', 'Unknown')} (ID: {doc.get('document_id')})")
                found = True
                break
        
        if not found:
            print(f"   ❌ Document ID {document_id} not found in documents list")
            print(f"   Available document IDs:")
            for doc in documents:
                print(f"     - {doc.get('document_id', 'No ID')} ({doc.get('filename', 'Unknown')})")
    else:
        print(f"   ❌ Failed to get documents: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🏁 Debugging completed!")

if __name__ == "__main__":
    debug_filtering()
