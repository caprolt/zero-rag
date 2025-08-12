#!/usr/bin/env python3
"""
ZeroRAG RAG Pipeline Test Script

This script tests the complete RAG pipeline functionality including:
- Document retrieval and context assembly
- Response generation with different parameters
- Streaming responses
- Error handling and edge cases
- Performance metrics
"""

import sys
import os
import time
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.service_factory import ServiceFactory
from services.rag_pipeline import RAGPipeline, RAGQuery, RAGResponse
from services.document_processor import DocumentProcessor
from services.vector_store import VectorStoreService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_rag_pipeline_initialization():
    """Test RAG pipeline initialization."""
    print("\n" + "="*60)
    print("TEST 1: RAG Pipeline Initialization")
    print("="*60)
    
    try:
        # Initialize service factory
        service_factory = ServiceFactory()
        
        # Get RAG pipeline
        rag_pipeline = service_factory.get_rag_pipeline()
        
        if rag_pipeline:
            print("✅ RAG Pipeline initialized successfully")
            print(f"   - Pipeline status: {rag_pipeline.health_check()['status']}")
            print(f"   - Services healthy: {service_factory.are_all_services_healthy()}")
            return True
        else:
            print("❌ RAG Pipeline initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ RAG Pipeline initialization error: {e}")
        return False


def test_document_ingestion():
    """Test document ingestion for RAG pipeline."""
    print("\n" + "="*60)
    print("TEST 2: Document Ingestion")
    print("="*60)
    
    try:
        service_factory = ServiceFactory()
        document_processor = service_factory.get_document_processor()
        vector_store = service_factory.get_vector_store()
        
        if not document_processor or not vector_store:
            print("❌ Required services not available")
            return False
        
        # Test document path
        test_doc_path = Path(__file__).parent.parent / "data" / "test_documents" / "simple_test.txt"
        
        if not test_doc_path.exists():
            print(f"❌ Test document not found: {test_doc_path}")
            return False
        
        print(f"📄 Processing test document: {test_doc_path.name}")
        
        # Process document
        processed_docs = document_processor.process_file(str(test_doc_path))
        
        if not processed_docs:
            print("❌ Document processing failed")
            return False
        
        print(f"✅ Document processed successfully")
        print(f"   - Chunks created: {len(processed_docs)}")
        
        # Store in vector database
        print("🗄️ Storing documents in vector database...")
        
        for doc in processed_docs:
            vector_store.add_document(doc)
        
        print("✅ Documents stored successfully")
        
        # Check collection stats
        stats = vector_store.get_collection_stats()
        print(f"   - Total documents: {stats.total_points}")
        print(f"   - Source files: {len(stats.source_files)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Document ingestion error: {e}")
        return False


def test_basic_rag_query():
    """Test basic RAG query functionality."""
    print("\n" + "="*60)
    print("TEST 3: Basic RAG Query")
    print("="*60)
    
    try:
        service_factory = ServiceFactory()
        rag_pipeline = service_factory.get_rag_pipeline()
        
        if not rag_pipeline:
            print("❌ RAG Pipeline not available")
            return False
        
        # Test query
        test_query = "What is this document about?"
        print(f"🔍 Query: {test_query}")
        
        # Process query
        start_time = time.time()
        response = rag_pipeline.query(test_query, top_k=3, max_tokens=200)
        query_time = time.time() - start_time
        
        print(f"✅ Query completed in {query_time:.2f}s")
        print(f"📝 Answer: {response.answer}")
        print(f"📊 Response time: {response.response_time:.2f}s")
        print(f"📄 Documents retrieved: {len(response.context.retrieved_documents)}")
        print(f"📏 Context length: {response.context.context_length} characters")
        
        if response.sources:
            print("📚 Sources:")
            for i, source in enumerate(response.sources[:3], 1):
                print(f"   {i}. {source['file']} (score: {source['score']:.3f})")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic RAG query error: {e}")
        return False


def test_rag_query_with_parameters():
    """Test RAG query with different parameters."""
    print("\n" + "="*60)
    print("TEST 4: RAG Query with Parameters")
    print("="*60)
    
    try:
        service_factory = ServiceFactory()
        rag_pipeline = service_factory.get_rag_pipeline()
        
        if not rag_pipeline:
            print("❌ RAG Pipeline not available")
            return False
        
        # Test different parameter combinations
        test_cases = [
            {
                "query": "What is the main topic?",
                "top_k": 1,
                "max_tokens": 100,
                "temperature": 0.3,
                "description": "Conservative, short response"
            },
            {
                "query": "Explain in detail",
                "top_k": 5,
                "max_tokens": 500,
                "temperature": 0.8,
                "description": "Creative, detailed response"
            },
            {
                "query": "Summarize the key points",
                "top_k": 3,
                "max_tokens": 300,
                "temperature": 0.5,
                "description": "Balanced response"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n🔍 Test {i}: {test_case['description']}")
            print(f"   Query: {test_case['query']}")
            
            start_time = time.time()
            response = rag_pipeline.query(**test_case)
            query_time = time.time() - start_time
            
            print(f"   ✅ Completed in {query_time:.2f}s")
            print(f"   📝 Answer length: {len(response.answer)} characters")
            print(f"   📄 Documents: {len(response.context.retrieved_documents)}")
            print(f"   🎯 Avg relevance: {response.metadata.get('avg_relevance_score', 0):.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Parameterized RAG query error: {e}")
        return False


def test_streaming_rag_query():
    """Test streaming RAG query functionality."""
    print("\n" + "="*60)
    print("TEST 5: Streaming RAG Query")
    print("="*60)
    
    try:
        service_factory = ServiceFactory()
        rag_pipeline = service_factory.get_rag_pipeline()
        
        if not rag_pipeline:
            print("❌ RAG Pipeline not available")
            return False
        
        # Test streaming query
        test_query = "What are the main points in this document?"
        print(f"🔍 Streaming Query: {test_query}")
        
        print("📝 Streaming response:")
        print("-" * 40)
        
        start_time = time.time()
        response_chunks = []
        
        for chunk in rag_pipeline.query_streaming(test_query, max_tokens=200):
            print(chunk, end="", flush=True)
            response_chunks.append(chunk)
        
        query_time = time.time() - start_time
        full_response = "".join(response_chunks)
        
        print("\n" + "-" * 40)
        print(f"✅ Streaming completed in {query_time:.2f}s")
        print(f"📝 Total response length: {len(full_response)} characters")
        print(f"📦 Number of chunks: {len(response_chunks)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Streaming RAG query error: {e}")
        return False


def test_error_handling():
    """Test error handling in RAG pipeline."""
    print("\n" + "="*60)
    print("TEST 6: Error Handling")
    print("="*60)
    
    try:
        service_factory = ServiceFactory()
        rag_pipeline = service_factory.get_rag_pipeline()
        
        if not rag_pipeline:
            print("❌ RAG Pipeline not available")
            return False
        
        # Test empty query
        print("🔍 Test 1: Empty query")
        response = rag_pipeline.query("")
        print(f"   Response: {response.answer[:100]}...")
        
        # Test very long query
        print("🔍 Test 2: Very long query")
        long_query = "What is this about? " * 100
        response = rag_pipeline.query(long_query, max_tokens=50)
        print(f"   Response: {response.answer[:100]}...")
        
        # Test query with no relevant documents
        print("🔍 Test 3: Query with no relevant documents")
        response = rag_pipeline.query("xyz123 completely unrelated topic", top_k=1)
        print(f"   Response: {response.answer[:100]}...")
        
        print("✅ Error handling tests completed")
        return True
        
    except Exception as e:
        print(f"❌ Error handling test error: {e}")
        return False


def test_performance_metrics():
    """Test performance metrics collection."""
    print("\n" + "="*60)
    print("TEST 7: Performance Metrics")
    print("="*60)
    
    try:
        service_factory = ServiceFactory()
        rag_pipeline = service_factory.get_rag_pipeline()
        
        if not rag_pipeline:
            print("❌ RAG Pipeline not available")
            return False
        
        # Run several queries to build metrics
        test_queries = [
            "What is this about?",
            "Summarize the content",
            "What are the key points?",
            "Explain the main topic",
            "What information is provided?"
        ]
        
        print("🔄 Running performance test queries...")
        
        for i, query in enumerate(test_queries, 1):
            print(f"   Query {i}/{len(test_queries)}: {query}")
            response = rag_pipeline.query(query, max_tokens=100)
            time.sleep(0.1)  # Small delay between queries
        
        # Get metrics
        metrics = rag_pipeline.get_metrics()
        
        print("\n📊 Performance Metrics:")
        print(f"   - Pipeline status: {metrics['pipeline_status']}")
        print(f"   - Uptime: {metrics['uptime_seconds']:.1f}s")
        print(f"   - Total queries: {metrics['metrics']['total_queries']}")
        print(f"   - Success rate: {metrics['metrics']['success_rate']:.2%}")
        print(f"   - Avg response time: {metrics['metrics']['avg_response_time']:.3f}s")
        print(f"   - Avg retrieval time: {metrics['metrics']['avg_retrieval_time']:.3f}s")
        print(f"   - Avg generation time: {metrics['metrics']['avg_generation_time']:.3f}s")
        print(f"   - Avg context length: {metrics['metrics']['avg_context_length']:.0f} chars")
        print(f"   - Avg documents retrieved: {metrics['metrics']['avg_documents_retrieved']:.1f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance metrics error: {e}")
        return False


def test_health_check():
    """Test health check functionality."""
    print("\n" + "="*60)
    print("TEST 8: Health Check")
    print("="*60)
    
    try:
        service_factory = ServiceFactory()
        rag_pipeline = service_factory.get_rag_pipeline()
        
        if not rag_pipeline:
            print("❌ RAG Pipeline not available")
            return False
        
        # Perform health check
        health_status = rag_pipeline.health_check()
        
        print("🏥 Health Check Results:")
        print(f"   - Overall status: {health_status['status']}")
        print(f"   - Services healthy: {health_status['services_healthy']}")
        print(f"   - Test query successful: {health_status['test_query_successful']}")
        
        if health_status['status'] == 'healthy':
            print("✅ RAG Pipeline is healthy")
        else:
            print("⚠️ RAG Pipeline has issues")
            if 'error' in health_status:
                print(f"   Error: {health_status['error']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False


def main():
    """Run all RAG pipeline tests."""
    print("🚀 ZeroRAG RAG Pipeline Test Suite")
    print("="*60)
    
    # Test results tracking
    test_results = []
    
    # Run all tests
    tests = [
        ("Initialization", test_rag_pipeline_initialization),
        ("Document Ingestion", test_document_ingestion),
        ("Basic Query", test_basic_rag_query),
        ("Parameterized Query", test_rag_query_with_parameters),
        ("Streaming Query", test_streaming_rag_query),
        ("Error Handling", test_error_handling),
        ("Performance Metrics", test_performance_metrics),
        ("Health Check", test_health_check)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"❌ Test '{test_name}' failed with exception: {e}")
            test_results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 All tests passed! RAG Pipeline is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
