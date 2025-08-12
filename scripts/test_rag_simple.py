#!/usr/bin/env python3
"""
Simple RAG Pipeline Test

This script tests basic RAG pipeline functionality without the full test suite.
"""

import sys
import os
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.service_factory import ServiceFactory
from services.rag_pipeline import RAGPipeline

def main():
    """Test basic RAG pipeline functionality."""
    print("🚀 Simple RAG Pipeline Test")
    print("="*50)
    
    try:
        # Initialize service factory
        print("📦 Initializing services...")
        service_factory = ServiceFactory()
        
        # Check service health
        print("\n🏥 Checking service health...")
        health_status = service_factory.perform_health_check()
        
        print(f"Overall status: {health_status['overall_status']}")
        for service_name, service_info in health_status['services'].items():
            print(f"  {service_name}: {service_info['status']}")
        
        # Get RAG pipeline
        print("\n🔍 Getting RAG pipeline...")
        rag_pipeline = service_factory.get_rag_pipeline()
        
        if not rag_pipeline:
            print("❌ RAG Pipeline not available")
            print("Available services:")
            for service_name, service_info in health_status['services'].items():
                if service_info['status'] == 'healthy':
                    print(f"  ✅ {service_name}")
                else:
                    print(f"  ❌ {service_name}: {service_info.get('health_data', {}).get('error', 'Unknown error')}")
            return 1
        
        print("✅ RAG Pipeline available")
        
        # Test basic query
        print("\n🔍 Testing basic query...")
        test_query = "Hello, how are you?"
        
        start_time = time.time()
        response = rag_pipeline.query(test_query, max_tokens=50)
        query_time = time.time() - start_time
        
        print(f"✅ Query completed in {query_time:.2f}s")
        print(f"📝 Answer: {response.answer}")
        print(f"📊 Response time: {response.response_time:.2f}s")
        print(f"📄 Documents retrieved: {len(response.context.retrieved_documents)}")
        
        # Test metrics
        print("\n📊 Pipeline metrics:")
        metrics = rag_pipeline.get_metrics()
        print(f"  Total queries: {metrics['metrics']['total_queries']}")
        print(f"  Success rate: {metrics['metrics']['success_rate']:.2%}")
        print(f"  Avg response time: {metrics['metrics']['avg_response_time']:.3f}s")
        
        print("\n🎉 RAG Pipeline is working!")
        return 0
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
