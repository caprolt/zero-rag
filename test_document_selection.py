#!/usr/bin/env python3
"""
Test script for document selection functionality.
"""

import requests
import json
from typing import List, Dict, Any

# API configuration
API_BASE_URL = "http://localhost:8000"

def test_document_listing():
    """Test that we can list available documents."""
    try:
        response = requests.get(f"{API_BASE_URL}/documents/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print("✅ Document listing works")
            print(f"Found {len(data.get('documents', []))} documents")
            for doc in data.get('documents', []):
                print(f"  - {doc.get('filename', 'Unknown')} (ID: {doc.get('document_id', 'N/A')})")
            return data.get('documents', [])
        else:
            print(f"❌ Document listing failed: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Document listing error: {e}")
        return []

def test_query_with_document_filtering(documents: List[Dict[str, Any]]):
    """Test querying with document filtering."""
    if not documents:
        print("⚠️ No documents available for testing")
        return
    
    # Test query without document filtering
    print("\n🔍 Testing query without document filtering...")
    try:
        response = requests.post(
            f"{API_BASE_URL}/query/",
            json={"query": "What documents are available?"},
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Query without filtering works")
            print(f"Answer: {data.get('answer', 'No answer')[:100]}...")
        else:
            print(f"❌ Query without filtering failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Query without filtering error: {e}")
    
    # Test query with document filtering
    if len(documents) >= 1:
        print(f"\n🔍 Testing query with document filtering (using first document)...")
        try:
            first_doc_id = documents[0].get('document_id')
            response = requests.post(
                f"{API_BASE_URL}/query/",
                json={
                    "query": "What documents are available?",
                    "document_ids": [first_doc_id]
                },
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                print("✅ Query with document filtering works")
                print(f"Answer: {data.get('answer', 'No answer')[:100]}...")
            else:
                print(f"❌ Query with document filtering failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Query with document filtering error: {e}")

def main():
    """Main test function."""
    print("🧪 Testing Document Selection Functionality")
    print("=" * 50)
    
    # Test document listing
    documents = test_document_listing()
    
    # Test query with document filtering
    test_query_with_document_filtering(documents)
    
    print("\n✅ Document selection testing completed!")

if __name__ == "__main__":
    main()
