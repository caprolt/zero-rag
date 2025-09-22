#!/usr/bin/env python3
"""
Inspect documents in the vector database to debug the "Unknown" filename issue.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.services.service_factory import get_service_factory
from src.config import get_config

def inspect_vector_documents():
    """Inspect documents stored in the vector database."""
    print("🔍 Inspecting vector database documents...")
    
    # Initialize services
    config = get_config()
    service_factory = get_service_factory()
    vector_store = service_factory.get_vector_store()
    
    if not vector_store:
        print("❌ Vector store not available")
        return
    
    # Get some sample documents
    try:
        from qdrant_client.http.models import Filter, FieldCondition, MatchValue
        
        # Search for documents with the specific document_id
        target_doc_id = "303f9420-0ceb-4920-bcd7-2ee8576d00fd"
        
        print(f"📋 Searching for documents with document_id: {target_doc_id}")
        
        # Create filter for the specific document
        filter_condition = Filter(
            must=[
                FieldCondition(
                    key="metadata.document_id",
                    match=MatchValue(value=target_doc_id)
                )
            ]
        )
        
        # Retrieve documents
        search_results = vector_store.client.scroll(
            collection_name=vector_store.collection_name,
            scroll_filter=filter_condition,
            limit=10,
            with_payload=True
        )[0]  # Get the points, not the next_page_offset
        
        print(f"📦 Found {len(search_results)} document chunks")
        
        for i, result in enumerate(search_results):
            print(f"\n--- Document Chunk {i+1} ---")
            print(f"ID: {result.id}")
            print(f"Payload keys: {list(result.payload.keys()) if result.payload else 'None'}")
            
            if result.payload:
                print(f"source_file: '{result.payload.get('source_file', 'NOT FOUND')}'")
                print(f"chunk_index: {result.payload.get('chunk_index', 'NOT FOUND')}")
                print(f"text (first 100 chars): {result.payload.get('text', 'NOT FOUND')[:100]}...")
                
                metadata = result.payload.get('metadata', {})
                print(f"metadata keys: {list(metadata.keys()) if metadata else 'None'}")
                if metadata:
                    print(f"metadata.document_id: {metadata.get('document_id', 'NOT FOUND')}")
                    print(f"metadata.filename: {metadata.get('filename', 'NOT FOUND')}")
                    print(f"metadata.source_file: {metadata.get('source_file', 'NOT FOUND')}")
        
        # Also try a general search to see what's in the database
        print(f"\n📊 General database inspection...")
        all_results = vector_store.client.scroll(
            collection_name=vector_store.collection_name,
            limit=5,
            with_payload=True
        )[0]
        
        print(f"📦 Total sample documents: {len(all_results)}")
        
        for i, result in enumerate(all_results):
            print(f"\n--- Sample Document {i+1} ---")
            print(f"ID: {result.id}")
            
            if result.payload:
                print(f"source_file: '{result.payload.get('source_file', 'NOT FOUND')}'")
                metadata = result.payload.get('metadata', {})
                if metadata:
                    print(f"metadata.document_id: {metadata.get('document_id', 'NOT FOUND')}")
                    print(f"metadata.filename: {metadata.get('filename', 'NOT FOUND')}")
                
    except Exception as e:
        print(f"❌ Error inspecting documents: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    inspect_vector_documents()