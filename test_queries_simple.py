#!/usr/bin/env python3
"""
Simple test script to demonstrate proper querying of the ZeroRAG system.
This shows how to ask specific questions that will return relevant results.
"""

import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

def test_query(query, score_threshold=0.1):
    """Test a query and return the response."""
    try:
        data = {
            "query": query,
            "top_k": 5,
            "score_threshold": score_threshold
        }
        
        response = requests.post(
            f"{API_BASE_URL}/query/",
            json=data,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"HTTP {response.status_code}: {response.text}"}
            
    except Exception as e:
        return {"error": str(e)}

def main():
    """Test various queries to demonstrate the system."""
    
    print("🤖 ZeroRAG Query Testing (Simple)")
    print("=" * 50)
    
    # Test queries that should work
    test_queries = [
        "What is the model serving readme about?",
        "Tell me about the test documents",
        "What does the security resume contain?",
        "What is document filtering?",
        "What are the features of the model serving system?",
        "What is Tanner Cline's background?",
        "What does the test upload document say?",
        "What is the purpose of the test documents?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n🔍 Test {i}: {query}")
        print("-" * 40)
        
        result = test_query(query)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✅ Answer: {result.get('answer', 'No answer')}")
            
            sources = result.get('sources', [])
            if sources:
                print(f"📚 Sources ({len(sources)} found):")
                for j, source in enumerate(sources, 1):
                    print(f"   {j}. {source.get('filename', 'Unknown')} (Score: {source.get('relevance_score', 0):.3f})")
            else:
                print("📚 No sources found")
        
        time.sleep(1)  # Brief pause between queries
    
    print("\n" + "=" * 50)
    print("💡 Tips for better queries:")
    print("• Ask specific questions about content")
    print("• Use keywords that appear in the documents")
    print("• Avoid generic phrases like 'describe this document'")
    print("• Try asking about specific topics or features mentioned in the documents")
    print("\n🔧 To restart the API server:")
    print("• Use: python -c \"import uvicorn; from src.api.main import app; uvicorn.run(app, host='0.0.0.0', port=8000)\"")
    print("• Or: python start_app.py")
    print("• Wait 30-40 seconds for full startup")

if __name__ == "__main__":
    main()
