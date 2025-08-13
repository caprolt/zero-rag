#!/usr/bin/env python3
"""
Test with a query that should definitely match the filtered document.
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_filtered_query():
    """Test with a query that should match the filtered document."""
    
    print("🧪 Testing Filtered Query with Matching Content")
    print("=" * 50)
    
    # Get the document ID from the previous test
    document_id = "29b07c26-271d-4299-a612-4e5d07f6e411"
    
    # Test queries that should definitely match the new document content
    test_queries = [
        "What does the document say about testing?",
        "How does the system store document IDs?",
        "What is the purpose of this test document?",
        "document filtering feature",
        "select specific documents"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: '{query}' (Filtered to document: {document_id})")
        
        query_data = {
            "query": query,
            "document_ids": [document_id],
            "top_k": 5,
            "score_threshold": 0.3
        }
        
        response = requests.post(f"{API_BASE_URL}/query", json=query_data)
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', 'No answer')
            sources = result.get('sources', [])
            
            print(f"   ✅ Query successful!")
            print(f"   Answer: {answer[:200]}...")
            print(f"   Sources found: {len(sources)}")
            
            for j, source in enumerate(sources):
                print(f"     Source {j+1}: {source.get('filename', 'Unknown')} (Score: {source.get('relevance_score', 0):.3f})")
        else:
            print(f"   ❌ Query failed: {response.status_code}")
    
    print("\n" + "=" * 50)
    print("🏁 Filtered query test completed!")

if __name__ == "__main__":
    test_filtered_query()
