#!/usr/bin/env python3
"""
Test API filtering with a specific query that should match.
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_api_filtering():
    """Test API filtering with specific queries."""
    
    print("🧪 Testing API Document Filtering")
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
            filename = target_doc.get("filename")
            print(f"Target document: {filename}")
            print(f"Document ID: {document_id}")
            
            # Test with a query that should definitely match
            test_queries = [
                "document filtering",
                "test document",
                "verify that document filtering works",
                "select specific documents"
            ]
            
            for i, query in enumerate(test_queries, 1):
                print(f"\n{i}. Testing query: '{query}'")
                
                # Test without filtering
                query_data = {
                    "query": query,
                    "top_k": 5,
                    "score_threshold": 0.3
                }
                
                response = requests.post(f"{API_BASE_URL}/query", json=query_data)
                if response.status_code == 200:
                    result = response.json()
                    sources = result.get('sources', [])
                    print(f"   Without filtering: {len(sources)} sources")
                
                # Test with filtering
                query_data = {
                    "query": query,
                    "document_ids": [document_id],
                    "top_k": 5,
                    "score_threshold": 0.3
                }
                
                response = requests.post(f"{API_BASE_URL}/query", json=query_data)
                if response.status_code == 200:
                    result = response.json()
                    sources = result.get('sources', [])
                    answer = result.get('answer', 'No answer')
                    print(f"   With filtering: {len(sources)} sources")
                    print(f"   Answer preview: {answer[:100]}...")
                    
                    if sources:
                        for j, source in enumerate(sources):
                            print(f"     Source {j+1}: {source.get('filename', 'Unknown')} (Score: {source.get('relevance_score', 0):.3f})")
                else:
                    print(f"   ❌ Query failed: {response.status_code}")
        else:
            print("❌ Target document not found")
    else:
        print(f"❌ Failed to get documents: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🏁 API filtering test completed!")

if __name__ == "__main__":
    test_api_filtering()
