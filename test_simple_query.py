#!/usr/bin/env python3
"""
Simple test to verify basic RAG functionality.
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_simple_query():
    """Test simple query functionality."""
    
    print("🧪 Testing Simple Query")
    print("=" * 50)
    
    # Simple query that should match the test document
    query_data = {
        "query": "test document",
        "top_k": 5,
        "score_threshold": 0.1  # Very low threshold
    }
    
    print(f"Query: 'test document'")
    
    try:
        response = requests.post(f"{API_BASE_URL}/query", json=query_data)
        if response.status_code == 200:
            result = response.json()
            answer = result.get('answer', 'No answer')
            sources = result.get('sources', [])
            
            print(f"✅ Query successful!")
            print(f"Answer: {answer}")
            print(f"Sources found: {len(sources)}")
            
            for i, source in enumerate(sources):
                print(f"  Source {i+1}: {source.get('filename', 'Unknown')} (Score: {source.get('relevance_score', 0):.3f})")
                print(f"    Preview: {source.get('content_preview', 'No preview')[:100]}...")
        else:
            print(f"❌ Query failed: {response.status_code}")
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Simple query test completed!")

if __name__ == "__main__":
    test_simple_query()
