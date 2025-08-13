#!/usr/bin/env python3
"""
Test vector store search directly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.service_factory import ServiceFactory
import numpy as np

def test_vector_search():
    """Test vector store search directly."""
    
    print("🔍 Testing Vector Store Search Directly")
    print("=" * 50)
    
    try:
        # Get service factory
        service_factory = ServiceFactory()
        vector_store = service_factory.get_vector_store()
        
        if not vector_store:
            print("❌ Vector store not available")
            return
        
        print(f"✅ Vector store available")
        print(f"   Status: {vector_store._check_health()}")
        
        # Test search without filters
        print(f"\n1. Testing search without filters...")
        try:
            # Create a simple test embedding
            test_embedding = [0.1] * 384  # Assuming 384-dimensional embeddings
            
            results = vector_store.search_similar(
                query_vector=test_embedding,
                top_k=10,
                score_threshold=0.1
            )
            
            print(f"   Results found: {len(results)}")
            for i, result in enumerate(results[:3]):
                print(f"   Result {i+1}: {result.source_file} (Score: {result.score:.3f})")
                print(f"     Metadata: {result.metadata}")
        except Exception as e:
            print(f"   ❌ Search failed: {e}")
        
        # Test search with document filtering
        print(f"\n2. Testing search with document filtering...")
        try:
            document_id = "29b07c26-271d-4299-a612-4e5d07f6e411"
            
            results = vector_store.search_similar(
                query_vector=test_embedding,
                top_k=10,
                score_threshold=0.1,
                filters={"document_ids": [document_id]}
            )
            
            print(f"   Results found: {len(results)}")
            for i, result in enumerate(results[:3]):
                print(f"   Result {i+1}: {result.source_file} (Score: {result.score:.3f})")
                print(f"     Metadata: {result.metadata}")
        except Exception as e:
            print(f"   ❌ Filtered search failed: {e}")
        
        # Test list documents
        print(f"\n3. Testing list documents...")
        try:
            documents = vector_store.list_documents(limit=10)
            print(f"   Documents found: {len(documents)}")
            for i, doc in enumerate(documents[:3]):
                print(f"   Document {i+1}: {doc.get('source_file', 'Unknown')}")
                print(f"     Metadata: {doc.get('metadata', {})}")
        except Exception as e:
            print(f"   ❌ List documents failed: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Vector store test completed!")

if __name__ == "__main__":
    test_vector_search()
