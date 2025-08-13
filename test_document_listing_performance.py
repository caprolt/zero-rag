#!/usr/bin/env python3
"""
Test script to measure document listing performance and identify bottlenecks.
"""

import time
import requests
import json
from qdrant_client import QdrantClient
from qdrant_client.http.models import ScrollRequest

def test_api_document_listing():
    """Test the API endpoint for document listing performance."""
    print("Testing API document listing performance...")
    
    start_time = time.time()
    try:
        response = requests.get("http://localhost:8000/documents", timeout=10)
        duration = time.time() - start_time
        
        print(f"API Response Status: {response.status_code}")
        print(f"API Response Time: {duration:.3f} seconds")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Total documents: {data.get('total', 0)}")
            print(f"Documents returned: {len(data.get('documents', []))}")
            print(f"Response size: {len(response.content)} bytes")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"API test failed: {e}")

def test_direct_qdrant_scroll():
    """Test direct Qdrant scroll operation performance."""
    print("\nTesting direct Qdrant scroll performance...")
    
    try:
        client = QdrantClient(host="localhost", port=6333)
        
        # Test 1: Get collection info
        start_time = time.time()
        collection_info = client.get_collection("zero_rag_documents")
        duration = time.time() - start_time
        print(f"Collection info time: {duration:.3f} seconds")
        print(f"Points count: {collection_info.points_count}")
        
        # Test 2: Scroll operation
        start_time = time.time()
        scroll_response = client.scroll(
            collection_name="zero_rag_documents",
            limit=100,
            offset=0,
            with_payload=True
        )
        duration = time.time() - start_time
        
        print(f"Scroll operation time: {duration:.3f} seconds")
        print(f"Points returned: {len(scroll_response[0])}")
        
        # Test 3: Scroll with different parameters
        print("\nTesting scroll with different parameters...")
        
        # Test with smaller limit
        start_time = time.time()
        scroll_response = client.scroll(
            collection_name="zero_rag_documents",
            limit=10,
            offset=0,
            with_payload=True
        )
        duration = time.time() - start_time
        print(f"Scroll (limit=10) time: {duration:.3f} seconds")
        
        # Test without payload
        start_time = time.time()
        scroll_response = client.scroll(
            collection_name="zero_rag_documents",
            limit=100,
            offset=0,
            with_payload=False
        )
        duration = time.time() - start_time
        print(f"Scroll (no payload) time: {duration:.3f} seconds")
        
    except Exception as e:
        print(f"Direct Qdrant test failed: {e}")

def test_qdrant_http_api():
    """Test Qdrant HTTP API directly."""
    print("\nTesting Qdrant HTTP API directly...")
    
    try:
        # Test scroll endpoint directly
        start_time = time.time()
        response = requests.post(
            "http://localhost:6333/collections/zero_rag_documents/points/scroll",
            json={
                "limit": 100,
                "offset": 0,
                "with_payload": True
            },
            timeout=10
        )
        duration = time.time() - start_time
        
        print(f"HTTP API scroll time: {duration:.3f} seconds")
        print(f"HTTP API status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Points returned: {len(data.get('result', {}).get('points', []))}")
        
    except Exception as e:
        print(f"HTTP API test failed: {e}")

def test_vector_store_service():
    """Test the vector store service directly."""
    print("\nTesting vector store service directly...")
    
    try:
        from src.services.vector_store import VectorStoreService
        from src.config import get_config
        
        config = get_config()
        vector_store = VectorStoreService(config)
        
        # Test list_documents method
        start_time = time.time()
        documents = vector_store.list_documents(limit=100, offset=0)
        duration = time.time() - start_time
        
        print(f"Vector store list_documents time: {duration:.3f} seconds")
        print(f"Documents returned: {len(documents)}")
        
        # Test health check
        start_time = time.time()
        is_healthy = vector_store._check_health()
        duration = time.time() - start_time
        print(f"Health check time: {duration:.3f} seconds")
        print(f"Health status: {is_healthy}")
        
    except Exception as e:
        print(f"Vector store service test failed: {e}")

if __name__ == "__main__":
    print("=== Document Listing Performance Test ===\n")
    
    # Test 1: API endpoint
    test_api_document_listing()
    
    # Test 2: Direct Qdrant scroll
    test_direct_qdrant_scroll()
    
    # Test 3: Qdrant HTTP API
    test_qdrant_http_api()
    
    # Test 4: Vector store service
    test_vector_store_service()
    
    print("\n=== Performance Test Complete ===")
