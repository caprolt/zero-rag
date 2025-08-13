#!/usr/bin/env python3
"""
Test script to verify document filtering functionality.
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_document_filtering():
    """Test document filtering functionality."""
    
    print("🧪 Testing Document Filtering Functionality")
    print("=" * 50)
    
    # Step 1: Check available documents
    print("\n1. Checking available documents...")
    try:
        response = requests.get(f"{API_BASE_URL}/documents")
        if response.status_code == 200:
            documents = response.json().get("documents", [])
            print(f"   Found {len(documents)} documents")
            
            if documents:
                # Show first few documents
                for i, doc in enumerate(documents[:3]):
                    print(f"   {i+1}. {doc.get('filename', 'Unknown')} (ID: {doc.get('document_id', 'N/A')})")
                
                # Test filtering with first document
                first_doc_id = documents[0].get('document_id')
                if first_doc_id:
                    print(f"\n2. Testing query with document filtering (ID: {first_doc_id})...")
                    
                    # Test query with document filtering
                    query_data = {
                        "query": "What is this document about?",
                        "document_ids": [first_doc_id],
                        "top_k": 5,
                        "score_threshold": 0.5
                    }
                    
                    response = requests.post(f"{API_BASE_URL}/query", json=query_data)
                    if response.status_code == 200:
                        result = response.json()
                        print(f"   ✅ Query successful!")
                        print(f"   Answer: {result.get('answer', 'No answer')[:200]}...")
                        print(f"   Sources: {len(result.get('sources', []))} sources found")
                        
                        # Show sources
                        for i, source in enumerate(result.get('sources', [])[:2]):
                            print(f"   Source {i+1}: {source.get('filename', 'Unknown')} (Score: {source.get('relevance_score', 0):.3f})")
                    else:
                        print(f"   ❌ Query failed: {response.status_code}")
                        print(f"   Error: {response.text}")
                else:
                    print("   ⚠️ No document ID found for testing")
            else:
                print("   ℹ️ No documents available for testing")
        else:
            print(f"   ❌ Failed to get documents: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 3: Test query without filtering (should work)
    print(f"\n3. Testing query without document filtering...")
    try:
        query_data = {
            "query": "What documents are available?",
            "top_k": 5,
            "score_threshold": 0.5
        }
        
        response = requests.post(f"{API_BASE_URL}/query", json=query_data)
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Query successful!")
            print(f"   Answer: {result.get('answer', 'No answer')[:200]}...")
            print(f"   Sources: {len(result.get('sources', []))} sources found")
        else:
            print(f"   ❌ Query failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Document filtering test completed!")

if __name__ == "__main__":
    test_document_filtering()
