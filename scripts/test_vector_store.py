#!/usr/bin/env python3
"""
ZeroRAG Vector Store Service Test Script

This script tests the vector store service functionality including:
- Connection and initialization
- CRUD operations (Create, Read, Update, Delete)
- Batch document operations
- Search and retrieval
- Performance monitoring
- Error handling
"""

import sys
import os
import time
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.vector_store import (
    VectorStoreService, VectorDocument, SearchResult, 
    create_vector_document, convert_document_chunks_to_vector_documents
)
from models.embeddings import EmbeddingService
from services.document_processor import DocumentProcessor, DocumentChunk
from config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_connection_and_initialization():
    """Test vector store connection and initialization."""
    print("\n" + "="*60)
    print("TEST 1: Connection and Initialization")
    print("="*60)
    
    try:
        # Initialize vector store
        print("Initializing vector store service...")
        vector_store = VectorStoreService()
        
        # Check health status
        health = vector_store.get_health_status()
        print(f"Health Status: {health['status']}")
        print(f"Connected: {health['connected']}")
        print(f"Collection: {health['collection_name']}")
        print(f"Vector Size: {health['vector_size']}")
        
        # Get collection stats
        stats = vector_store.get_collection_stats()
        print(f"Collection Stats:")
        print(f"  - Total Points: {stats.total_points}")
        print(f"  - Total Vectors: {stats.total_vectors}")
        print(f"  - Collection Size: {stats.collection_size} bytes")
        print(f"  - Source Files: {len(stats.source_files)}")
        print(f"  - Chunk Count: {stats.chunk_count}")
        
        return vector_store, True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return None, False


def test_single_document_operations(vector_store):
    """Test single document CRUD operations."""
    print("\n" + "="*60)
    print("TEST 2: Single Document CRUD Operations")
    print("="*60)
    
    try:
        # Create test document
        test_text = "This is a test document for vector store operations."
        test_metadata = {
            "test_type": "single_operation",
            "created_by": "test_script",
            "version": "1.0"
        }
        
        # Create embedding for test text
        embedding_service = EmbeddingService()
        vector = embedding_service.encode_single(test_text)
        
        # Create vector document
        doc = create_vector_document(
            text=test_text,
            vector=vector,
            metadata=test_metadata,
            source_file="test_single.txt",
            chunk_index=0
        )
        
        print(f"Created document: {doc.id}")
        print(f"Text: {doc.text[:50]}...")
        print(f"Vector size: {len(doc.vector)}")
        
        # Test insert
        print("\nTesting document insertion...")
        success = vector_store.insert_document(doc)
        print(f"Insert result: {'✅ Success' if success else '❌ Failed'}")
        
        # Test retrieve
        print("\nTesting document retrieval...")
        retrieved_doc = vector_store.get_document(doc.id)
        if retrieved_doc:
            print(f"✅ Retrieved document: {retrieved_doc.id}")
            print(f"Text matches: {retrieved_doc.text == doc.text}")
            print(f"Metadata matches: {retrieved_doc.metadata == doc.metadata}")
        else:
            print("❌ Failed to retrieve document")
            return False
        
        # Test update
        print("\nTesting document update...")
        updated_text = "This is an updated test document for vector store operations."
        updated_vector = embedding_service.encode_single(updated_text)
        
        updated_doc = VectorDocument(
            id=doc.id,
            text=updated_text,
            vector=updated_vector,
            metadata={**test_metadata, "updated": True},
            source_file=doc.source_file,
            chunk_index=doc.chunk_index,
            created_at=doc.created_at,
            updated_at=time.time()
        )
        
        update_success = vector_store.update_document(updated_doc)
        print(f"Update result: {'✅ Success' if update_success else '❌ Failed'}")
        
        # Verify update
        retrieved_updated = vector_store.get_document(doc.id)
        if retrieved_updated and retrieved_updated.text == updated_text:
            print("✅ Update verified successfully")
        else:
            print("❌ Update verification failed")
            return False
        
        # Test delete
        print("\nTesting document deletion...")
        delete_success = vector_store.delete_document(doc.id)
        print(f"Delete result: {'✅ Success' if delete_success else '❌ Failed'}")
        
        # Verify deletion
        retrieved_deleted = vector_store.get_document(doc.id)
        if retrieved_deleted is None:
            print("✅ Deletion verified successfully")
        else:
            print("❌ Deletion verification failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Single document operations test failed: {e}")
        return False


def test_batch_operations(vector_store):
    """Test batch document operations."""
    print("\n" + "="*60)
    print("TEST 3: Batch Document Operations")
    print("="*60)
    
    try:
        # Create test documents
        test_texts = [
            "First test document for batch operations.",
            "Second test document with different content.",
            "Third test document for comprehensive testing.",
            "Fourth test document to verify batch processing.",
            "Fifth test document to complete the batch test."
        ]
        
        embedding_service = EmbeddingService()
        documents = []
        
        print(f"Creating {len(test_texts)} test documents...")
        
        for i, text in enumerate(test_texts):
            vector = embedding_service.encode_single(text)
            metadata = {
                "test_type": "batch_operation",
                "batch_index": i,
                "created_by": "test_script"
            }
            
            doc = create_vector_document(
                text=text,
                vector=vector,
                metadata=metadata,
                source_file="test_batch.txt",
                chunk_index=i
            )
            documents.append(doc)
        
        # Test batch insert
        print("\nTesting batch document insertion...")
        start_time = time.time()
        batch_result = vector_store.insert_documents_batch(documents)
        batch_time = time.time() - start_time
        
        print(f"Batch insert result:")
        print(f"  - Total: {batch_result['total']}")
        print(f"  - Successful: {batch_result['successful']}")
        print(f"  - Failed: {batch_result['failed']}")
        print(f"  - Time: {batch_time:.3f}s")
        
        if batch_result['errors']:
            print(f"  - Errors: {batch_result['errors']}")
        
        if batch_result['successful'] != len(documents):
            print("❌ Batch insert failed")
            return False
        
        # Test batch retrieval
        print("\nTesting batch document retrieval...")
        retrieved_docs = []
        for doc in documents:
            retrieved = vector_store.get_document(doc.id)
            if retrieved:
                retrieved_docs.append(retrieved)
        
        print(f"Retrieved {len(retrieved_docs)} out of {len(documents)} documents")
        
        if len(retrieved_docs) == len(documents):
            print("✅ Batch retrieval successful")
        else:
            print("❌ Batch retrieval failed")
            return False
        
        # Test search functionality
        print("\nTesting search functionality...")
        query_text = "test document"
        query_vector = embedding_service.encode_single(query_text)
        
        search_results = vector_store.search_similar(
            query_vector=query_vector,
            top_k=3,
            score_threshold=0.5
        )
        
        print(f"Search results: {len(search_results)} documents found")
        for i, result in enumerate(search_results):
            print(f"  {i+1}. Score: {result.score:.3f}, Text: {result.text[:50]}...")
        
        # Clean up batch documents
        print("\nCleaning up batch documents...")
        for doc in documents:
            vector_store.delete_document(doc.id)
        
        return True
        
    except Exception as e:
        print(f"❌ Batch operations test failed: {e}")
        return False


def test_search_and_filtering(vector_store):
    """Test advanced search and filtering capabilities."""
    print("\n" + "="*60)
    print("TEST 4: Search and Filtering")
    print("="*60)
    
    try:
        # Create test documents with different metadata
        embedding_service = EmbeddingService()
        documents = []
        
        test_data = [
            ("Python programming guide", "python_guide.txt", {"category": "programming", "language": "python"}),
            ("Machine learning basics", "ml_basics.txt", {"category": "ai", "language": "python"}),
            ("Data science fundamentals", "data_science.txt", {"category": "data", "language": "python"}),
            ("Web development tutorial", "web_dev.txt", {"category": "programming", "language": "javascript"}),
            ("Database design principles", "database.txt", {"category": "data", "language": "sql"})
        ]
        
        print("Creating test documents for search testing...")
        
        for i, (text, source_file, metadata) in enumerate(test_data):
            vector = embedding_service.encode_single(text)
            doc = create_vector_document(
                text=text,
                vector=vector,
                metadata=metadata,
                source_file=source_file,
                chunk_index=i
            )
            documents.append(doc)
        
        # Insert documents
        batch_result = vector_store.insert_documents_batch(documents)
        if batch_result['successful'] != len(documents):
            print("❌ Failed to insert test documents")
            return False
        
        # Test basic search
        print("\nTesting basic similarity search...")
        query_text = "programming"
        query_vector = embedding_service.encode_single(query_text)
        
        results = vector_store.search_similar(
            query_vector=query_vector,
            top_k=5,
            score_threshold=0.3
        )
        
        print(f"Basic search results: {len(results)} documents")
        for i, result in enumerate(results):
            print(f"  {i+1}. Score: {result.score:.3f}, Text: {result.text}")
        
        # Test filtering by category
        print("\nTesting category filtering...")
        results = vector_store.search_similar(
            query_vector=query_vector,
            top_k=5,
            score_threshold=0.3,
            filters={"metadata.category": "programming"}
        )
        
        print(f"Category filter results: {len(results)} documents")
        for i, result in enumerate(results):
            print(f"  {i+1}. Score: {result.score:.3f}, Text: {result.text}")
        
        # Test filtering by source file
        print("\nTesting source file filtering...")
        results = vector_store.search_similar(
            query_vector=query_vector,
            top_k=5,
            score_threshold=0.3,
            filters={"source_file": "python_guide.txt"}
        )
        
        print(f"Source file filter results: {len(results)} documents")
        for i, result in enumerate(results):
            print(f"  {i+1}. Score: {result.score:.3f}, Text: {result.text}")
        
        # Clean up
        for doc in documents:
            vector_store.delete_document(doc.id)
        
        return True
        
    except Exception as e:
        print(f"❌ Search and filtering test failed: {e}")
        return False


def test_performance_monitoring(vector_store):
    """Test performance monitoring and metrics."""
    print("\n" + "="*60)
    print("TEST 5: Performance Monitoring")
    print("="*60)
    
    try:
        # Get initial health status
        initial_health = vector_store.get_health_status()
        print("Initial health status:")
        print(f"  - Status: {initial_health['status']}")
        print(f"  - Total Operations: {initial_health['total_operations']}")
        print(f"  - Failed Operations: {initial_health['failed_operations']}")
        print(f"  - Success Rate: {initial_health['success_rate']:.2%}")
        
        # Perform some operations to generate metrics
        print("\nPerforming operations to generate metrics...")
        
        embedding_service = EmbeddingService()
        test_docs = []
        
        for i in range(10):
            text = f"Performance test document {i+1}"
            vector = embedding_service.encode_single(text)
            doc = create_vector_document(
                text=text,
                vector=vector,
                metadata={"test_type": "performance"},
                source_file="perf_test.txt",
                chunk_index=i
            )
            test_docs.append(doc)
        
        # Batch insert
        start_time = time.time()
        batch_result = vector_store.insert_documents_batch(test_docs)
        batch_time = time.time() - start_time
        
        # Search operations
        query_vector = embedding_service.encode_single("test document")
        search_start = time.time()
        search_results = vector_store.search_similar(query_vector, top_k=5)
        search_time = time.time() - search_start
        
        # Get updated health status
        final_health = vector_store.get_health_status()
        
        print("\nPerformance metrics:")
        print(f"  - Batch insert time: {batch_time:.3f}s")
        print(f"  - Search time: {search_time:.3f}s")
        print(f"  - Total operations: {final_health['total_operations']}")
        print(f"  - Average operation times:")
        
        for operation, avg_time in final_health['avg_operation_times'].items():
            print(f"    * {operation}: {avg_time:.3f}s")
        
        print(f"  - Memory usage: {final_health['memory_usage']}")
        
        # Clean up
        for doc in test_docs:
            vector_store.delete_document(doc.id)
        
        return True
        
    except Exception as e:
        print(f"❌ Performance monitoring test failed: {e}")
        return False


def test_error_handling(vector_store):
    """Test error handling and edge cases."""
    print("\n" + "="*60)
    print("TEST 6: Error Handling")
    print("="*60)
    
    try:
        # Test invalid document ID
        print("Testing invalid document ID retrieval...")
        invalid_doc = vector_store.get_document("invalid_id_12345")
        if invalid_doc is None:
            print("✅ Correctly handled invalid document ID")
        else:
            print("❌ Should have returned None for invalid ID")
            return False
        
        # Test empty search results
        print("\nTesting search with no results...")
        embedding_service = EmbeddingService()
        query_vector = embedding_service.encode_single("completely unrelated query")
        
        results = vector_store.search_similar(
            query_vector=query_vector,
            top_k=5,
            score_threshold=0.9  # Very high threshold
        )
        
        if len(results) == 0:
            print("✅ Correctly handled search with no results")
        else:
            print(f"❌ Expected 0 results, got {len(results)}")
            return False
        
        # Test collection stats with empty collection
        print("\nTesting collection stats...")
        stats = vector_store.get_collection_stats()
        print(f"Collection stats: {stats.total_points} points, {stats.total_vectors} vectors")
        
        return True
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def test_integration_with_document_processor(vector_store):
    """Test integration with document processor."""
    print("\n" + "="*60)
    print("TEST 7: Document Processor Integration")
    print("="*60)
    
    try:
        # Create test document
        test_content = """
        This is a test document for integration testing.
        
        It contains multiple paragraphs and sentences to test
        the document processing pipeline.
        
        The document processor should chunk this content and
        the vector store should store the embeddings.
        """
        
        # Process document
        doc_processor = DocumentProcessor()
        embedding_service = EmbeddingService()
        
        print("Processing test document...")
        chunks = doc_processor.process_text_content(test_content, "integration_test.txt")
        
        print(f"Created {len(chunks)} chunks")
        
        # Convert chunks to vector documents
        print("Converting chunks to vector documents...")
        vectors = []
        for chunk in chunks:
            vector = embedding_service.encode_single(chunk.text)
            vectors.append(vector)
        
        vector_docs = convert_document_chunks_to_vector_documents(
            chunks=chunks,
            vectors=vectors,
            source_file="integration_test.txt",
            base_metadata={"test_type": "integration"}
        )
        
        print(f"Created {len(vector_docs)} vector documents")
        
        # Store in vector store
        print("Storing in vector store...")
        batch_result = vector_store.insert_documents_batch(vector_docs)
        
        if batch_result['successful'] == len(vector_docs):
            print("✅ Integration test successful")
        else:
            print(f"❌ Integration test failed: {batch_result}")
            return False
        
        # Test retrieval
        print("Testing retrieval...")
        query_text = "document processing pipeline"
        query_vector = embedding_service.encode_single(query_text)
        
        results = vector_store.search_similar(
            query_vector=query_vector,
            top_k=3,
            score_threshold=0.5
        )
        
        print(f"Found {len(results)} relevant chunks")
        for i, result in enumerate(results):
            print(f"  {i+1}. Score: {result.score:.3f}, Text: {result.text[:100]}...")
        
        # Clean up
        for doc in vector_docs:
            vector_store.delete_document(doc.id)
        
        return True
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False


def main():
    """Run all vector store tests."""
    print("ZeroRAG Vector Store Service Test Suite")
    print("="*60)
    
    # Test results
    test_results = {}
    
    # Test 1: Connection and Initialization
    vector_store, success = test_connection_and_initialization()
    test_results["connection"] = success
    
    if not success:
        print("\n❌ Cannot proceed without vector store connection")
        return
    
    # Test 2: Single Document Operations
    test_results["single_operations"] = test_single_document_operations(vector_store)
    
    # Test 3: Batch Operations
    test_results["batch_operations"] = test_batch_operations(vector_store)
    
    # Test 4: Search and Filtering
    test_results["search_filtering"] = test_search_and_filtering(vector_store)
    
    # Test 5: Performance Monitoring
    test_results["performance"] = test_performance_monitoring(vector_store)
    
    # Test 6: Error Handling
    test_results["error_handling"] = test_error_handling(vector_store)
    
    # Test 7: Integration
    test_results["integration"] = test_integration_with_document_processor(vector_store)
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Vector store service is working correctly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    # Final health check
    if vector_store:
        final_health = vector_store.get_health_status()
        print(f"\nFinal Health Status: {final_health['status']}")
        print(f"Total Operations: {final_health['total_operations']}")
        print(f"Success Rate: {final_health['success_rate']:.2%}")


if __name__ == "__main__":
    main()
