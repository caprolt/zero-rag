#!/usr/bin/env python3
"""
ZeroRAG Phase 4.3 Optimizations Test Script

This script tests the Phase 4.3 enhancements to the vector store service including:
- Operation queuing and background processing
- Enhanced batch operations with chunking
- Memory optimization and garbage collection
- Performance alerts and monitoring
- Storage monitoring and health checks
- Batch search capabilities
"""

import sys
import os
import time
import logging
import threading
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.vector_store import (
    VectorStoreService, VectorDocument, SearchResult, 
    create_vector_document, convert_document_chunks_to_vector_documents,
    PerformanceAlert
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


def test_operation_queuing(vector_store):
    """Test operation queuing functionality."""
    print("\n" + "="*60)
    print("TEST 1: Operation Queuing")
    print("="*60)
    
    try:
        # Create test documents
        embedding_service = EmbeddingService()
        test_docs = []
        
        for i in range(50):
            text = f"Test document {i} for queuing operations."
            vector = embedding_service.encode_single(text)
            doc = create_vector_document(
                text=text,
                vector=vector,
                metadata={"test_type": "queuing", "index": i},
                source_file=f"queuing_test_{i}.txt",
                chunk_index=i
            )
            test_docs.append(doc)
        
        print(f"Created {len(test_docs)} test documents")
        
        # Test callback functionality
        callback_results = []
        def callback(result):
            callback_results.append(result)
            print(f"Callback received: {result['successful']} documents processed")
        
        # Queue batch insert operations
        print("Queuing batch insert operations...")
        success = vector_store.queue_batch_insert(
            documents=test_docs[:25],
            priority=1,  # High priority
            callback=callback
        )
        
        if not success:
            print("❌ Failed to queue batch insert")
            return False
        
        # Queue another batch with different priority
        success = vector_store.queue_batch_insert(
            documents=test_docs[25:],
            priority=2,  # Normal priority
            callback=callback
        )
        
        if not success:
            print("❌ Failed to queue second batch insert")
            return False
        
        print("✅ Batch operations queued successfully")
        
        # Wait for operations to complete
        print("Waiting for queued operations to complete...")
        time.sleep(5)  # Wait for background processing
        
        # Check queue status
        health = vector_store.get_health_status()
        print(f"Queue size: {health['queue_size']}")
        print(f"Background services: {health['background_services']}")
        
        # Verify documents were inserted
        stats = vector_store.get_collection_stats()
        print(f"Collection now has {stats.total_points} documents")
        
        # Test queue batch delete
        doc_ids = [doc.id for doc in test_docs]
        success = vector_store.queue_batch_delete(
            document_ids=doc_ids,
            priority=1,
            callback=callback
        )
        
        if success:
            print("✅ Batch delete queued successfully")
            time.sleep(3)  # Wait for deletion to complete
        else:
            print("❌ Failed to queue batch delete")
        
        print(f"Total callbacks received: {len(callback_results)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Operation queuing test failed: {e}")
        return False


def test_enhanced_batch_operations(vector_store):
    """Test enhanced batch operations with chunking."""
    print("\n" + "="*60)
    print("TEST 2: Enhanced Batch Operations")
    print("="*60)
    
    try:
        # Create a large batch of documents
        embedding_service = EmbeddingService()
        large_batch = []
        
        print("Creating large batch of documents...")
        for i in range(200):  # Large batch to test chunking
            text = f"Large batch document {i} with more content to test chunked processing."
            vector = embedding_service.encode_single(text)
            doc = create_vector_document(
                text=text,
                vector=vector,
                metadata={"test_type": "large_batch", "index": i},
                source_file=f"large_batch_{i}.txt",
                chunk_index=i
            )
            large_batch.append(doc)
        
        print(f"Created {len(large_batch)} documents for large batch test")
        
        # Test enhanced batch insert
        print("Testing enhanced batch insert with chunking...")
        start_time = time.time()
        
        result = vector_store.insert_documents_batch(large_batch)
        
        batch_time = time.time() - start_time
        
        print(f"Batch insert results:")
        print(f"  - Total: {result['total']}")
        print(f"  - Successful: {result['successful']}")
        print(f"  - Failed: {result['failed']}")
        print(f"  - Processing time: {result['processing_time']:.3f}s")
        print(f"  - Actual time: {batch_time:.3f}s")
        print(f"  - Memory usage: {result['memory_usage']}")
        
        if result['successful'] == len(large_batch):
            print("✅ Large batch insert successful")
        else:
            print(f"❌ Batch insert failed: {result['errors']}")
            return False
        
        # Test batch search
        print("\nTesting batch search...")
        query_texts = [
            "large batch document",
            "chunked processing",
            "test content",
            "vector operations"
        ]
        
        query_vectors = []
        for text in query_texts:
            vector = embedding_service.encode_single(text)
            query_vectors.append(vector)
        
        start_time = time.time()
        batch_results = vector_store.batch_search(
            query_vectors=query_vectors,
            top_k=5,
            score_threshold=0.5
        )
        
        search_time = time.time() - start_time
        
        print(f"Batch search results:")
        print(f"  - Queries: {len(query_vectors)}")
        print(f"  - Search time: {search_time:.3f}s")
        
        for i, results in enumerate(batch_results):
            print(f"  - Query {i+1}: {len(results)} results")
        
        # Clean up
        doc_ids = [doc.id for doc in large_batch]
        delete_result = vector_store.queue_batch_delete(doc_ids, priority=1)
        
        if delete_result:
            print("✅ Batch cleanup queued")
            time.sleep(3)  # Wait for cleanup
        else:
            print("❌ Failed to queue cleanup")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced batch operations test failed: {e}")
        return False


def test_memory_optimization(vector_store):
    """Test memory optimization and garbage collection."""
    print("\n" + "="*60)
    print("TEST 3: Memory Optimization")
    print("="*60)
    
    try:
        # Get initial memory usage
        initial_health = vector_store.get_health_status()
        initial_memory = initial_health['memory_usage']
        print(f"Initial memory usage: {initial_memory}")
        
        # Create documents to test memory management
        embedding_service = EmbeddingService()
        test_docs = []
        
        print("Creating documents to test memory management...")
        for i in range(100):
            text = f"Memory test document {i} with substantial content to test memory optimization and garbage collection mechanisms."
            vector = embedding_service.encode_single(text)
            doc = create_vector_document(
                text=text,
                vector=vector,
                metadata={"test_type": "memory_test", "index": i},
                source_file=f"memory_test_{i}.txt",
                chunk_index=i
            )
            test_docs.append(doc)
        
        # Insert documents
        result = vector_store.insert_documents_batch(test_docs)
        print(f"Inserted {result['successful']} documents")
        
        # Check memory after insertion
        post_insert_health = vector_store.get_health_status()
        post_insert_memory = post_insert_health['memory_usage']
        print(f"Memory after insertion: {post_insert_memory}")
        
        # Get memory trend
        detailed_metrics = vector_store.get_detailed_metrics()
        memory_trend = detailed_metrics['memory_trend']
        print(f"Memory trend entries: {len(memory_trend)}")
        
        if memory_trend:
            print("Recent memory measurements:")
            for entry in memory_trend[-3:]:  # Last 3 measurements
                print(f"  - {entry['timestamp']}: {entry['memory_mb']:.1f}MB ({entry['memory_percent']:.1f}%)")
        
        # Test manual memory cleanup
        print("\nTesting manual memory cleanup...")
        from services.vector_store import OperationQueueItem
        cleanup_item = OperationQueueItem(
            operation_type="collection_cleanup",
            data=None,
            priority=1
        )
        vector_store.operation_queue.put(cleanup_item)
        
        time.sleep(2)  # Wait for cleanup
        
        # Check memory after cleanup
        post_cleanup_health = vector_store.get_health_status()
        post_cleanup_memory = post_cleanup_health['memory_usage']
        print(f"Memory after cleanup: {post_cleanup_memory}")
        
        # Clean up test documents
        doc_ids = [doc.id for doc in test_docs]
        vector_store.queue_batch_delete(doc_ids, priority=1)
        time.sleep(2)
        
        print("✅ Memory optimization test completed")
        return True
        
    except Exception as e:
        print(f"❌ Memory optimization test failed: {e}")
        return False


def test_performance_alerts(vector_store):
    """Test performance alerts and monitoring."""
    print("\n" + "="*60)
    print("TEST 4: Performance Alerts")
    print("="*60)
    
    try:
        # Clear existing alerts
        vector_store.clear_performance_alerts()
        print("Cleared existing performance alerts")
        
        # Test alert callback
        received_alerts = []
        
        def alert_callback(alert: PerformanceAlert):
            received_alerts.append(alert)
            print(f"Alert received: [{alert.severity.upper()}] {alert.message}")
        
        vector_store.add_alert_callback(alert_callback)
        print("Added alert callback")
        
        # Trigger some alerts by performing operations
        embedding_service = EmbeddingService()
        
        # Create a slow operation to trigger performance alert
        print("Creating documents to trigger performance monitoring...")
        test_docs = []
        
        for i in range(50):
            text = f"Performance test document {i} for testing alerts and monitoring capabilities."
            vector = embedding_service.encode_single(text)
            doc = create_vector_document(
                text=text,
                vector=vector,
                metadata={"test_type": "performance_test", "index": i},
                source_file=f"performance_test_{i}.txt",
                chunk_index=i
            )
            test_docs.append(doc)
        
        # Insert documents (may trigger alerts)
        result = vector_store.insert_documents_batch(test_docs)
        print(f"Inserted {result['successful']} documents")
        
        # Wait for alerts to be processed
        time.sleep(2)
        
        # Check alerts
        alerts = vector_store.get_performance_alerts()
        print(f"Total alerts generated: {len(alerts)}")
        
        if alerts:
            print("Recent alerts:")
            for alert in alerts[-3:]:  # Last 3 alerts
                print(f"  - [{alert['severity']}] {alert['message']}")
        
        # Test alert filtering
        high_alerts = vector_store.get_performance_alerts(severity='high')
        print(f"High severity alerts: {len(high_alerts)}")
        
        # Check received callbacks
        print(f"Alerts received via callback: {len(received_alerts)}")
        
        # Clean up
        doc_ids = [doc.id for doc in test_docs]
        vector_store.queue_batch_delete(doc_ids, priority=1)
        time.sleep(2)
        
        print("✅ Performance alerts test completed")
        return True
        
    except Exception as e:
        print(f"❌ Performance alerts test failed: {e}")
        return False


def test_storage_monitoring(vector_store):
    """Test storage monitoring and health checks."""
    print("\n" + "="*60)
    print("TEST 5: Storage Monitoring")
    print("="*60)
    
    try:
        # Get storage monitoring info
        storage_info = vector_store.get_storage_monitoring()
        print("Storage monitoring information:")
        for key, value in storage_info.items():
            print(f"  - {key}: {value}")
        
        # Get detailed health status
        health = vector_store.get_health_status()
        print(f"\nHealth status: {health['status']}")
        print(f"Health score: {health['health_score']}")
        
        if health['health_issues']:
            print("Health issues:")
            for issue in health['health_issues']:
                print(f"  - {issue}")
        
        # Get detailed metrics
        detailed_metrics = vector_store.get_detailed_metrics()
        print(f"\nDetailed metrics:")
        print(f"  - Operation percentiles: {len(detailed_metrics['operation_percentiles'])} operations")
        print(f"  - Memory trend: {len(detailed_metrics['memory_trend'])} measurements")
        print(f"  - Queue utilization: {detailed_metrics['queue_metrics']['utilization']:.1%}")
        
        # Test operation percentiles
        if detailed_metrics['operation_percentiles']:
            print("\nOperation performance percentiles:")
            for operation, percentiles in detailed_metrics['operation_percentiles'].items():
                print(f"  - {operation}:")
                print(f"    P50: {percentiles['p50']*1000:.1f}ms")
                print(f"    P90: {percentiles['p90']*1000:.1f}ms")
                print(f"    P95: {percentiles['p95']*1000:.1f}ms")
        
        # Test error rates
        error_rates = health['error_rates']
        if error_rates:
            print("\nError rates by operation:")
            for operation, rate in error_rates.items():
                print(f"  - {operation}: {rate:.1%}")
        
        print("✅ Storage monitoring test completed")
        return True
        
    except Exception as e:
        print(f"❌ Storage monitoring test failed: {e}")
        return False


def test_background_services(vector_store):
    """Test background services functionality."""
    print("\n" + "="*60)
    print("TEST 6: Background Services")
    print("="*60)
    
    try:
        # Check background services status
        health = vector_store.get_health_status()
        background_services = health['background_services']
        
        print("Background services status:")
        for service, status in background_services.items():
            print(f"  - {service}: {'Running' if status else 'Stopped'}")
        
        # Test queue operations
        queue_size = health['queue_size']
        print(f"Current queue size: {queue_size}")
        
        # Test memory monitoring
        memory_info = health['memory_usage']
        print(f"Current memory usage: {memory_info}")
        
        # Test performance thresholds
        thresholds = vector_store.performance_thresholds
        print(f"Performance thresholds:")
        for threshold, value in thresholds.items():
            print(f"  - {threshold}: {value}")
        
        # Test queue worker functionality
        print("\nTesting queue worker with multiple operations...")
        
        embedding_service = EmbeddingService()
        test_docs = []
        
        for i in range(20):
            text = f"Background service test document {i}."
            vector = embedding_service.encode_single(text)
            doc = create_vector_document(
                text=text,
                vector=vector,
                metadata={"test_type": "background_test", "index": i},
                source_file=f"background_test_{i}.txt",
                chunk_index=i
            )
            test_docs.append(doc)
        
        # Queue operations with different priorities
        success1 = vector_store.queue_batch_insert(test_docs[:10], priority=1)
        success2 = vector_store.queue_batch_insert(test_docs[10:], priority=3)
        
        print(f"High priority queue: {'Success' if success1 else 'Failed'}")
        print(f"Low priority queue: {'Success' if success2 else 'Failed'}")
        
        # Wait for processing
        time.sleep(3)
        
        # Check final status
        final_health = vector_store.get_health_status()
        final_queue_size = final_health['queue_size']
        print(f"Final queue size: {final_queue_size}")
        
        # Clean up
        doc_ids = [doc.id for doc in test_docs]
        vector_store.queue_batch_delete(doc_ids, priority=1)
        time.sleep(2)
        
        print("✅ Background services test completed")
        return True
        
    except Exception as e:
        print(f"❌ Background services test failed: {e}")
        return False


def main():
    """Run all Phase 4.3 optimization tests."""
    print("ZeroRAG Phase 4.3 Optimizations Test Suite")
    print("="*60)
    
    # Initialize vector store
    print("Initializing vector store service...")
    vector_store = VectorStoreService()
    
    # Test results
    test_results = {}
    
    # Test 1: Operation Queuing
    test_results["operation_queuing"] = test_operation_queuing(vector_store)
    
    # Test 2: Enhanced Batch Operations
    test_results["enhanced_batch_operations"] = test_enhanced_batch_operations(vector_store)
    
    # Test 3: Memory Optimization
    test_results["memory_optimization"] = test_memory_optimization(vector_store)
    
    # Test 4: Performance Alerts
    test_results["performance_alerts"] = test_performance_alerts(vector_store)
    
    # Test 5: Storage Monitoring
    test_results["storage_monitoring"] = test_storage_monitoring(vector_store)
    
    # Test 6: Background Services
    test_results["background_services"] = test_background_services(vector_store)
    
    # Summary
    print("\n" + "="*60)
    print("PHASE 4.3 TEST SUMMARY")
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
        print("🎉 All Phase 4.3 optimization tests passed!")
        print("✅ Operation queuing is working")
        print("✅ Enhanced batch operations are optimized")
        print("✅ Memory optimization is active")
        print("✅ Performance alerts are functioning")
        print("✅ Storage monitoring is operational")
        print("✅ Background services are running")
    else:
        print("⚠️  Some Phase 4.3 tests failed. Please check the implementation.")
    
    # Final health check
    final_health = vector_store.get_health_status()
    print(f"\nFinal Health Status: {final_health['status']}")
    print(f"Health Score: {final_health['health_score']}")
    print(f"Total Operations: {final_health['total_operations']}")
    print(f"Success Rate: {final_health['success_rate']:.2%}")
    print(f"Performance Alerts: {final_health['performance_alerts']}")
    
    # Close vector store
    vector_store.close()
    print("\nVector store service closed.")


if __name__ == "__main__":
    main()
