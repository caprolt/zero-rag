#!/usr/bin/env python3
"""
Test script with specific queries that should match document content.
"""

import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_specific_queries():
    """Test with specific queries that should match document content."""
    
    print("🧪 Testing Specific Queries")
    print("=" * 50)
    
    # Get available documents
    try:
        response = requests.get(f"{API_BASE_URL}/documents")
        if response.status_code == 200:
            documents = response.json().get("documents", [])
            print(f"Found {len(documents)} documents")
            
            if documents:
                first_doc_id = documents[0].get('document_id')
                first_doc_name = documents[0].get('filename', 'Unknown')
                
                print(f"\nTesting with document: {first_doc_name} (ID: {first_doc_id})")
                
                # Test queries that should match the test document content
                test_queries = [
                    "What is ZeroRAG?",
                    "What file formats does the system support?",
                    "How does the chunking algorithm work?",
                    "What are the capabilities of the document processor?",
                    "test document"
                ]
                
                for i, query in enumerate(test_queries, 1):
                    print(f"\n{i}. Query: '{query}'")
                    
                    # Test without filtering
                    query_data = {
                        "query": query,
                        "top_k": 5,
                        "score_threshold": 0.3  # Lower threshold for testing
                    }
                    
                    response = requests.post(f"{API_BASE_URL}/query", json=query_data)
                    if response.status_code == 200:
                        result = response.json()
                        answer = result.get('answer', 'No answer')
                        sources = result.get('sources', [])
                        
                        print(f"   Answer: {answer[:150]}...")
                        print(f"   Sources: {len(sources)} found")
                        
                        if sources:
                            for j, source in enumerate(sources[:2]):
                                print(f"   Source {j+1}: {source.get('filename', 'Unknown')} (Score: {source.get('relevance_score', 0):.3f})")
                        else:
                            print("   ⚠️ No sources found")
                    else:
                        print(f"   ❌ Query failed: {response.status_code}")
                
                # Test with document filtering
                print(f"\n6. Testing with document filtering...")
                query_data = {
                    "query": "What is ZeroRAG?",
                    "document_ids": [first_doc_id],
                    "top_k": 5,
                    "score_threshold": 0.3
                }
                
                response = requests.post(f"{API_BASE_URL}/query", json=query_data)
                if response.status_code == 200:
                    result = response.json()
                    answer = result.get('answer', 'No answer')
                    sources = result.get('sources', [])
                    
                    print(f"   Answer: {answer[:150]}...")
                    print(f"   Sources: {len(sources)} found")
                    
                    if sources:
                        for j, source in enumerate(sources[:2]):
                            print(f"   Source {j+1}: {source.get('filename', 'Unknown')} (Score: {source.get('relevance_score', 0):.3f})")
                    else:
                        print("   ⚠️ No sources found")
                else:
                    print(f"   ❌ Query failed: {response.status_code}")
            else:
                print("No documents available")
        else:
            print(f"Failed to get documents: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Specific query test completed!")

if __name__ == "__main__":
    test_specific_queries()
