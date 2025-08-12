#!/usr/bin/env python3
"""
ZeroRAG Phase 5.3: Simple Pipeline Testing

This script runs a simplified version of Phase 5.3 testing that:
1. Ingests test documents first
2. Runs basic pipeline validation
3. Tests error handling
4. Validates response quality
"""

import sys
import os
import time
import logging
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.service_factory import ServiceFactory
from services.rag_pipeline import RAGPipeline, RAGQuery, RAGResponse, QueryType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_and_ingest_documents():
    """Setup services and ingest test documents."""
    print("\n" + "="*60)
    print("🔧 SETUP AND DOCUMENT INGESTION")
    print("="*60)
    
    try:
        # Initialize service factory
        service_factory = ServiceFactory()
        
        # Get services
        document_processor = service_factory.get_document_processor()
        vector_store = service_factory.get_vector_store()
        rag_pipeline = service_factory.get_rag_pipeline()
        
        if not all([document_processor, vector_store, rag_pipeline]):
            print("❌ Required services not available")
            return False
        
        print("✅ Services initialized successfully")
        
        # Prepare test documents
        data_dir = Path(__file__).parent.parent / "data" / "test_documents"
        test_files = [
            "simple_test.txt",
            "test_document.txt", 
            "test_document.md",
            "test_data.csv"
        ]
        
        total_chunks = 0
        for file_name in test_files:
            file_path = data_dir / file_name
            if file_path.exists():
                print(f"📄 Processing: {file_name}")
                
                processed_docs, metadata = document_processor.process_document(str(file_path))
                if processed_docs:
                    for doc in processed_docs:
                        vector_store.insert_document(doc)
                    total_chunks += len(processed_docs)
                    print(f"   ✅ Added {len(processed_docs)} chunks")
                else:
                    print(f"   ❌ Failed to process")
            else:
                print(f"⚠️ File not found: {file_name}")
        
        print(f"\n📊 Total chunks ingested: {total_chunks}")
        
        if total_chunks == 0:
            print("❌ No documents ingested - cannot proceed with testing")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False


def test_basic_queries():
    """Test basic RAG queries."""
    print("\n" + "="*60)
    print("TEST 1: Basic RAG Queries")
    print("="*60)
    
    try:
        service_factory = ServiceFactory()
        rag_pipeline = service_factory.get_rag_pipeline()
        
        test_queries = [
            ("What is this document about?", QueryType.GENERAL),
            ("What are the main topics discussed?", QueryType.FACTUAL),
            ("Summarize the key points.", QueryType.SUMMARIZATION),
        ]
        
        success_count = 0
        for query_text, query_type in test_queries:
            print(f"\n🔍 Testing: {query_text}")
            
            try:
                response = rag_pipeline.query(
                    query_text,
                    query_type=query_type,
                    top_k=3,
                    max_tokens=150
                )
                
                if response and response.answer:
                    print(f"✅ Query successful")
                    print(f"   - Response: {response.answer[:100]}...")
                    print(f"   - Sources: {len(response.sources)}")
                    print(f"   - Response time: {response.response_time:.2f}s")
                    print(f"   - Validation: {response.validation_status}")
                    print(f"   - Safety score: {response.safety_score:.2f}")
                    success_count += 1
                else:
                    print(f"❌ No response generated")
                    
            except Exception as e:
                print(f"❌ Query failed: {e}")
        
        success_rate = success_count / len(test_queries)
        print(f"\n📊 Basic query test results: {success_count}/{len(test_queries)} ({success_rate:.1%})")
        
        return success_rate >= 0.6  # 60% success rate threshold
        
    except Exception as e:
        print(f"❌ Basic query test failed: {e}")
        return False


def test_error_handling():
    """Test error handling and edge cases."""
    print("\n" + "="*60)
    print("TEST 2: Error Handling")
    print("="*60)
    
    try:
        service_factory = ServiceFactory()
        rag_pipeline = service_factory.get_rag_pipeline()
        
        error_tests = [
            ("Empty query", ""),
            ("Very long query", "x" * 1000),
            ("Special characters", "!@#$%^&*()_+-=[]{}|;':\",./<>?"),
            ("Unicode query", "测试查询 with unicode 🚀"),
        ]
        
        success_count = 0
        for test_name, query in error_tests:
            print(f"\n🧪 Testing: {test_name}")
            
            try:
                response = rag_pipeline.query(
                    query,
                    top_k=1,
                    max_tokens=50
                )
                
                # Should handle gracefully without crashing
                if response is not None:
                    print(f"✅ Handled gracefully")
                    success_count += 1
                else:
                    print(f"❌ Failed to handle")
                    
            except Exception as e:
                print(f"❌ Exception occurred: {e}")
        
        success_rate = success_count / len(error_tests)
        print(f"\n📊 Error handling test results: {success_count}/{len(error_tests)} ({success_rate:.1%})")
        
        return success_rate >= 0.7  # 70% success rate threshold
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


def test_response_quality():
    """Test response quality and validation."""
    print("\n" + "="*60)
    print("TEST 3: Response Quality")
    print("="*60)
    
    try:
        service_factory = ServiceFactory()
        rag_pipeline = service_factory.get_rag_pipeline()
        
        quality_tests = [
            ("What is the main topic?", "general"),
            ("What are the key features?", "factual"),
            ("How does this work?", "analytical"),
        ]
        
        quality_scores = []
        
        for test_name, expected_type in quality_tests:
            print(f"\n🎯 Testing: {test_name}")
            
            try:
                response = rag_pipeline.query(
                    test_name,
                    query_type=QueryType(expected_type),
                    top_k=3,
                    max_tokens=100
                )
                
                if response and response.answer:
                    # Simple quality assessment
                    score = 0.0
                    
                    # Length check
                    if 20 <= len(response.answer) <= 500:
                        score += 0.3
                    
                    # Source attribution
                    if response.sources and len(response.sources) > 0:
                        score += 0.3
                    
                    # Validation status
                    if response.validation_status == "valid":
                        score += 0.2
                    
                    # Safety score
                    score += response.safety_score * 0.2
                    
                    quality_scores.append(score)
                    
                    print(f"   📝 Response length: {len(response.answer)} chars")
                    print(f"   🎯 Quality score: {score:.2f}/1.0")
                    print(f"   🔗 Sources: {len(response.sources)}")
                    print(f"   ✅ Validation: {response.validation_status}")
                    print(f"   🛡️ Safety: {response.safety_score:.2f}")
                    
                else:
                    print(f"   ❌ No response generated")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            print(f"\n📊 Average quality score: {avg_quality:.2f}/1.0")
            
            return avg_quality >= 0.5  # 50% quality threshold
        else:
            print("❌ No quality scores available")
            return False
        
    except Exception as e:
        print(f"❌ Response quality test failed: {e}")
        return False


def test_performance():
    """Test basic performance metrics."""
    print("\n" + "="*60)
    print("TEST 4: Performance")
    print("="*60)
    
    try:
        service_factory = ServiceFactory()
        rag_pipeline = service_factory.get_rag_pipeline()
        
        # Run multiple queries to test performance
        times = []
        for i in range(3):
            print(f"\n⚡ Performance test iteration {i+1}")
            
            start_time = time.time()
            response = rag_pipeline.query(
                "What is the main topic?",
                top_k=2,
                max_tokens=50
            )
            end_time = time.time()
            
            if response and response.answer:
                response_time = end_time - start_time
                times.append(response_time)
                print(f"   Response time: {response_time:.2f}s")
            else:
                print(f"   Query failed")
        
        if times:
            avg_time = sum(times) / len(times)
            print(f"\n📊 Average response time: {avg_time:.2f}s")
            
            # Performance threshold: under 10 seconds
            performance_acceptable = avg_time < 10.0
            
            if performance_acceptable:
                print("✅ Performance acceptable")
            else:
                print("⚠️ Performance slow")
            
            return performance_acceptable
        else:
            print("❌ No successful queries for performance testing")
            return False
        
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        return False


def generate_report(test_results):
    """Generate test report."""
    print("\n" + "="*80)
    print("📊 PHASE 5.3 SIMPLE TEST REPORT")
    print("="*80)
    
    successful_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)
    overall_success_rate = successful_tests / total_tests if total_tests > 0 else 0
    
    print(f"🎯 Overall Success Rate: {overall_success_rate:.1%} ({successful_tests}/{total_tests})")
    
    for test_name, result in test_results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"   {test_name}: {status}")
    
    if overall_success_rate >= 0.8:
        print("\n✅ Phase 5.3 PASSED - Pipeline ready for next phase")
    elif overall_success_rate >= 0.6:
        print("\n⚠️ Phase 5.3 PARTIAL - Some issues need attention")
    else:
        print("\n❌ Phase 5.3 FAILED - Significant issues detected")
    
    # Save report
    report = {
        'phase': '5.3_simple',
        'test_date': time.strftime('%Y-%m-%d %H:%M:%S'),
        'overall_success_rate': overall_success_rate,
        'successful_tests': successful_tests,
        'total_tests': total_tests,
        'test_results': test_results
    }
    
    report_file = Path(__file__).parent / "phase_5_3_simple_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Test report saved to: {report_file}")
    
    return overall_success_rate >= 0.8


def main():
    """Main testing function."""
    print("🚀 ZeroRAG Phase 5.3: Simple Pipeline Testing")
    print("="*80)
    
    # Setup and ingest documents
    if not setup_and_ingest_documents():
        print("❌ Setup failed - cannot proceed with testing")
        return False
    
    # Run tests
    test_results = {
        "Basic Queries": test_basic_queries(),
        "Error Handling": test_error_handling(),
        "Response Quality": test_response_quality(),
        "Performance": test_performance(),
    }
    
    # Generate report
    success = generate_report(test_results)
    
    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
