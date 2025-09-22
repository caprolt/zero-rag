#!/usr/bin/env python3
"""
Test the API query endpoint to check if the fix works.
"""

import requests
import json

def test_query():
    """Test the query endpoint."""
    url = "http://localhost:8000/query/"
    
    payload = {
        "query": "describe one of the cheat sheet items",
        "document_ids": ["303f9420-0ceb-4920-bcd7-2ee8576d00fd"]
    }
    
    try:
        print("🚀 Testing query endpoint...")
        print(f"📤 Sending query: {payload['query']}")
        print(f"📋 Document filter: {payload['document_ids']}")
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Query successful!")
            print(f"📝 Answer: {result.get('answer', 'No answer')[:200]}...")
            print(f"🕐 Response time: {result.get('response_time', 'Unknown')} seconds")
            
            sources = result.get('sources', [])
            print(f"📚 Sources found: {len(sources)}")
            
            for i, source in enumerate(sources):
                print(f"  Source {i+1}:")
                print(f"    Filename: {source.get('filename', 'Unknown')}")
                print(f"    Relevance: {source.get('relevance_score', 0.0)}")
                print(f"    Chunk: {source.get('chunk_index', 0)}")
                print(f"    Preview: {source.get('content_preview', 'No preview')[:100]}...")
        else:
            print(f"❌ Query failed with status {response.status_code}")
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing query: {e}")

if __name__ == "__main__":
    test_query()