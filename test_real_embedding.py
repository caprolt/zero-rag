#!/usr/bin/env python3
"""
Test with real embeddings from the embedding service.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.service_factory import ServiceFactory

def test_real_embedding():
    """Test with real embeddings."""
    
    print("🔍 Testing with Real Embeddings")
    print("=" * 50)
    
    try:
        # Get service factory
        service_factory = ServiceFactory()
        vector_store = service_factory.get_vector_store()
        embedding_service = service_factory.get_embedding_service()
        
        if not vector_store:
            print("❌ Vector store not available")
            return
        
        if not embedding_service:
            print("❌ Embedding service not available")
            return
        
        print(f"✅ Services available")
        
        # Test with real embedding
        print(f"\n1. Testing with real embedding...")
        try:
            # Create a real embedding for a query that should match our document
            query = "document filtering"
            query_embedding = embedding_service.encode(query)
            
            print(f"   Query: '{query}'")
            print(f"   Embedding length: {len(query_embedding)}")
            
            results = vector_store.search_similar(
                query_vector=query_embedding,
                top_k=10,
                score_threshold=0.1
            )
            
            print(f"   Results found: {len(results)}")
            for i, result in enumerate(results[:3]):
                print(f"   Result {i+1}: {result.source_file} (Score: {result.score:.3f})")
                print(f"     Text preview: {result.text[:100]}...")
                print(f"     Metadata: {result.metadata}")
        except Exception as e:
            print(f"   ❌ Search failed: {e}")
        
        # Test with document filtering
        print(f"\n2. Testing with document filtering...")
        try:
            document_id = "29b07c26-271d-4299-a612-4e5d07f6e411"
            
            results = vector_store.search_similar(
                query_vector=query_embedding,
                top_k=10,
                score_threshold=0.1,
                filters={"document_ids": [document_id]}
            )
            
            print(f"   Results found: {len(results)}")
            for i, result in enumerate(results[:3]):
                print(f"   Result {i+1}: {result.source_file} (Score: {result.score:.3f})")
                print(f"     Text preview: {result.text[:100]}...")
                print(f"     Metadata: {result.metadata}")
        except Exception as e:
            print(f"   ❌ Filtered search failed: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Real embedding test completed!")

if __name__ == "__main__":
    test_real_embedding()
