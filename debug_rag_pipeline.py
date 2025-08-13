#!/usr/bin/env python3
"""
Debug the RAG pipeline directly.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from services.service_factory import ServiceFactory
from services.rag_pipeline import RAGQuery

def debug_rag_pipeline():
    """Debug the RAG pipeline directly."""
    
    print("🔍 Debugging RAG Pipeline")
    print("=" * 50)
    
    try:
        # Get service factory
        service_factory = ServiceFactory()
        rag_pipeline = service_factory.rag_pipeline
        
        if not rag_pipeline:
            print("❌ RAG pipeline not available")
            return
        
        print(f"✅ RAG pipeline available")
        
        # Test without filtering
        print(f"\n1. Testing without document filtering...")
        try:
            rag_query = RAGQuery(
                query="document filtering",
                top_k=5,
                score_threshold=0.3
            )
            
            response = rag_pipeline.process_query(rag_query)
            
            print(f"   Answer: {response.answer[:100]}...")
            print(f"   Sources: {len(response.sources)}")
            
            for i, source in enumerate(response.sources[:2]):
                print(f"   Source {i+1}: {source.get('file', 'Unknown')} (Score: {source.get('score', 0):.3f})")
                print(f"     Preview: {source.get('text_preview', 'No preview')[:100]}...")
        except Exception as e:
            print(f"   ❌ Query failed: {e}")
        
        # Test with document filtering
        print(f"\n2. Testing with document filtering...")
        try:
            document_id = "29b07c26-271d-4299-a612-4e5d07f6e411"
            
            rag_query = RAGQuery(
                query="document filtering",
                top_k=5,
                score_threshold=0.3,
                filters={"document_ids": [document_id]}
            )
            
            response = rag_pipeline.process_query(rag_query)
            
            print(f"   Answer: {response.answer[:100]}...")
            print(f"   Sources: {len(response.sources)}")
            
            for i, source in enumerate(response.sources[:2]):
                print(f"   Source {i+1}: {source.get('file', 'Unknown')} (Score: {source.get('score', 0):.3f})")
                print(f"     Preview: {source.get('text_preview', 'No preview')[:100]}...")
        except Exception as e:
            print(f"   ❌ Filtered query failed: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 RAG pipeline debug completed!")

if __name__ == "__main__":
    debug_rag_pipeline()
