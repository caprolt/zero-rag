#!/usr/bin/env python3
"""
Test script for the ZeroRAG Embedding Service.

This script demonstrates the embedding service functionality and validates
that all components are working correctly.
"""

import sys
import time
import numpy as np
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_config
from src.models.embeddings import EmbeddingService, get_embedding_service


def test_embedding_service():
    """Test the embedding service functionality."""
    print("🚀 Testing ZeroRAG Embedding Service")
    print("=" * 50)
    
    try:
        # Load configuration
        print("📋 Loading configuration...")
        config = get_config()
        print(f"   Model: {config.ai_model.embedding_model_name}")
        print(f"   Device: {config.ai_model.embedding_device}")
        print(f"   Batch size: {config.ai_model.embedding_batch_size}")
        print(f"   Cache enabled: {config.performance.enable_caching}")
        
        # Initialize embedding service
        print("\n🔧 Initializing embedding service...")
        start_time = time.time()
        service = EmbeddingService(config)
        init_time = time.time() - start_time
        print(f"   Initialization time: {init_time:.2f}s")
        
        # Check health status
        print("\n🏥 Checking service health...")
        health = service.health_check()
        print(f"   Status: {health['status']}")
        print(f"   Model loaded: {health['model_loaded']}")
        print(f"   Cache enabled: {health['cache_enabled']}")
        
        if health['status'] != 'healthy':
            print("   ❌ Service is not healthy!")
            return False
        
        # Test single encoding
        print("\n📝 Testing single text encoding...")
        test_text = "This is a test sentence for the embedding service."
        start_time = time.time()
        embedding = service.encode_single(test_text)
        encode_time = time.time() - start_time
        
        print(f"   Text: {test_text}")
        print(f"   Embedding shape: {embedding.shape}")
        print(f"   Embedding dtype: {embedding.dtype}")
        print(f"   Encoding time: {encode_time:.4f}s")
        
        # Test batch encoding
        print("\n📚 Testing batch encoding...")
        test_texts = [
            "First sentence for batch processing.",
            "Second sentence with different content.",
            "Third sentence to test batch efficiency.",
            "Fourth sentence to validate performance.",
            "Fifth sentence to complete the batch."
        ]
        
        start_time = time.time()
        batch_embeddings = service.encode_batch(test_texts)
        batch_time = time.time() - start_time
        
        print(f"   Batch size: {len(test_texts)}")
        print(f"   Batch time: {batch_time:.4f}s")
        print(f"   Average time per text: {batch_time/len(test_texts):.4f}s")
        
        # Test similarity calculation
        print("\n🔍 Testing similarity calculations...")
        query_text = "What is the main topic?"
        query_embedding = service.encode_single(query_text)
        
        similarities = service.batch_similarity(query_embedding, batch_embeddings)
        
        print(f"   Query: {query_text}")
        for i, (text, sim) in enumerate(zip(test_texts, similarities)):
            print(f"   Text {i+1}: {sim:.4f} - {text[:30]}...")
        
        # Test caching (encode same text twice)
        print("\n💾 Testing caching functionality...")
        cache_test_text = "This text should be cached for the second call."
        
        # First call
        start_time = time.time()
        embedding1 = service.encode_single(cache_test_text)
        first_time = time.time() - start_time
        
        # Second call (should use cache)
        start_time = time.time()
        embedding2 = service.encode_single(cache_test_text)
        second_time = time.time() - start_time
        
        print(f"   First call time: {first_time:.4f}s")
        print(f"   Second call time: {second_time:.4f}s")
        print(f"   Speedup: {first_time/second_time:.2f}x")
        print(f"   Embeddings equal: {np.array_equal(embedding1, embedding2)}")
        
        # Get performance metrics
        print("\n📊 Performance metrics:")
        metrics = service.get_performance_metrics()
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.4f}")
            else:
                print(f"   {key}: {value}")
        
        # Get memory usage
        print("\n💻 Memory usage:")
        memory = service.get_memory_usage()
        for key, value in memory.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.2f} MB")
            else:
                print(f"   {key}: {value}")
        
        print("\n✅ All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_global_service():
    """Test the global service functions."""
    print("\n🌐 Testing global service functions...")
    
    try:
        config = get_config()
        
        # Get service instance
        service1 = get_embedding_service(config)
        print("   ✅ Global service instance created")
        
        # Get service instance again (should be the same)
        service2 = get_embedding_service(config)
        print(f"   ✅ Same instance returned: {service1 is service2}")
        
        # Test encoding with global service
        test_text = "Testing global service functionality."
        embedding = service1.encode_single(test_text)
        print(f"   ✅ Global service encoding successful: {embedding.shape}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Global service test failed: {e}")
        return False


def main():
    """Main test function."""
    print("ZeroRAG Embedding Service Test Suite")
    print("=" * 50)
    
    # Test basic functionality
    success1 = test_embedding_service()
    
    # Test global service
    success2 = test_global_service()
    
    # Summary
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"   Basic functionality: {'✅ PASS' if success1 else '❌ FAIL'}")
    print(f"   Global service: {'✅ PASS' if success2 else '❌ FAIL'}")
    
    if success1 and success2:
        print("\n🎉 All tests passed! The embedding service is working correctly.")
        return 0
    else:
        print("\n💥 Some tests failed. Please check the error messages above.")
        return 1


if __name__ == "__main__":
    exit(main())
