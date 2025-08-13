#!/usr/bin/env python3
"""
Test with the correct document ID from the documents list.
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_correct_id():
    """Test with the correct document ID."""
    
    print("🧪 Testing with Correct Document ID")
    print("=" * 50)
    
    # Get the correct document ID from the documents list
    response = requests.get(f"{API_BASE_URL}/documents")
    if response.status_code == 200:
        documents = response.json().get("documents", [])
        
        # Find the document that contains our test content
        target_doc = None
        for doc in documents:
            if "test_new_document.txt" in doc.get("filename", ""):
                target_doc = doc
                break
        
        if target_doc:
            document_id = target_doc.get("document_id")
            filename = target_doc.get("filename")
            print(f"Found target document: {filename}")
            print(f"Document ID: {document_id}")
            
            # Test query with the correct document ID
            print(f"\nTesting query with correct document ID...")
            query_data = {
                "query": "document filtering",
                "document_ids": [document_id],
                "top_k": 5,
                "score_threshold": 0.3
            }
            
            response = requests.post(f"{API_BASE_URL}/query", json=query_data)
            if response.status_code == 200:
                result = response.json()
                answer = result.get('answer', 'No answer')
                sources = result.get('sources', [])
                
                print(f"✅ Query successful!")
                print(f"Answer: {answer[:200]}...")
                print(f"Sources found: {len(sources)}")
                
                for i, source in enumerate(sources):
                    print(f"  Source {i+1}: {source.get('filename', 'Unknown')} (Score: {source.get('relevance_score', 0):.3f})")
                    print(f"    Preview: {source.get('content_preview', 'No preview')[:100]}...")
            else:
                print(f"❌ Query failed: {response.status_code}")
                print(f"Error: {response.text}")
        else:
            print("❌ Target document not found")
    else:
        print(f"❌ Failed to get documents: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_correct_id()
