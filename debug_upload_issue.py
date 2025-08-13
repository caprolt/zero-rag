#!/usr/bin/env python3
"""
Debug script to identify document upload issues.
"""

import sys
import os
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_service_initialization():
    """Test service initialization step by step."""
    print("🔍 Testing service initialization...")
    
    try:
        # Test 1: Configuration
        print("1. Testing configuration...")
        from config import get_config
        config = get_config()
        print(f"✅ Configuration loaded: {config.database.qdrant_host}:{config.database.qdrant_port}")
        
        # Test 2: Vector Store
        print("2. Testing vector store initialization...")
        from services.vector_store import VectorStoreService
        vector_store = VectorStoreService()
        print(f"✅ Vector store initialized: {vector_store.is_connected}")
        
        # Test 3: Document Processor
        print("3. Testing document processor...")
        from services.document_processor import DocumentProcessor
        doc_processor = DocumentProcessor()
        print("✅ Document processor initialized")
        
        # Test 4: Service Factory
        print("4. Testing service factory...")
        from services.service_factory import ServiceFactory
        factory = ServiceFactory()
        print("✅ Service factory initialized")
        
        # Test 5: Test document processing
        print("5. Testing document processing...")
        test_file = Path("test_upload_final.txt")
        if test_file.exists():
            result = factory.document_processor.process_file(test_file)
            print(f"✅ Document processing successful: {len(result.get('chunks', []))} chunks")
            
            # Test 6: Test vector store insertion
            print("6. Testing vector store insertion...")
            if result.get('chunks'):
                # Add embeddings first
                from models.embeddings import EmbeddingService
                embedding_service = EmbeddingService()
                texts = [chunk.text for chunk in result['chunks']]
                embeddings = embedding_service.encode(texts)
                
                # Update chunks with embeddings
                for i, chunk in enumerate(result['chunks']):
                    if i < len(embeddings):
                        chunk.vector = embeddings[i].tolist()
                
                # Insert into vector store
                insert_result = factory.vector_store.insert_documents_batch(result['chunks'])
                print(f"✅ Vector store insertion: {insert_result}")
            else:
                print("❌ No chunks to insert")
        else:
            print("❌ Test file not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_qdrant_connection():
    """Test Qdrant connection directly."""
    print("\n🔍 Testing Qdrant connection...")
    
    try:
        from qdrant_client import QdrantClient
        
        client = QdrantClient(host="localhost", port=6333)
        collections = client.get_collections()
        print(f"✅ Qdrant connected: {len(collections.collections)} collections")
        
        for collection in collections.collections:
            print(f"   - {collection.name}")
            
        return True
        
    except Exception as e:
        print(f"❌ Qdrant connection failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting ZeroRAG upload issue debug...")
    print("=" * 50)
    
    # Test Qdrant connection first
    qdrant_ok = test_qdrant_connection()
    
    if qdrant_ok:
        # Test service initialization
        services_ok = test_service_initialization()
        
        if services_ok:
            print("\n🎉 All tests passed! The issue might be in the API layer.")
        else:
            print("\n❌ Service initialization failed.")
    else:
        print("\n❌ Qdrant connection failed. Please check if Qdrant is running.")
    
    print("=" * 50)
