#!/usr/bin/env python3
"""
ZeroRAG Phase 5.3: Pipeline Testing

This script implements comprehensive testing for the RAG pipeline including:
- End-to-end testing with various document types
- Error handling and retry mechanisms
- Performance benchmarking
- Response quality validation
- Graceful degradation testing
- Memory and resource monitoring

Phase 5.3 Deliverables:
- Comprehensive test suite
- Error handling validation
- Performance testing
- Response quality assessment
"""

import sys
import os
import time
import logging
import json
import psutil
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import asdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.service_factory import ServiceFactory
from services.rag_pipeline import RAGPipeline, RAGQuery, RAGResponse, QueryType
from services.document_processor import DocumentProcessor
from services.vector_store import VectorStoreService
from models.embeddings import EmbeddingService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PipelineTester:
    """Comprehensive RAG pipeline testing framework."""
    
    def __init__(self):
        self.service_factory = None
        self.rag_pipeline = None
        self.test_results = {}
        self.performance_metrics = {}
        self.error_log = []
        
    def setup(self) -> bool:
        """Initialize testing environment."""
        print("\n" + "="*80)
        print("🔧 SETTING UP PHASE 5.3 PIPELINE TESTING")
        print("="*80)
        
        try:
            # Initialize service factory
            self.service_factory = ServiceFactory()
            
            # Get RAG pipeline
            self.rag_pipeline = self.service_factory.get_rag_pipeline()
            
            if not self.rag_pipeline:
                print("❌ RAG Pipeline not available")
                return False
            
            # Check service health
            health_status = self.rag_pipeline.health_check()
            if health_status['status'] != 'healthy':
                print(f"❌ Pipeline health check failed: {health_status}")
                return False
            
            print("✅ Testing environment initialized successfully")
            print(f"   - Pipeline status: {health_status['status']}")
            print(f"   - Services healthy: {self.service_factory.are_all_services_healthy()}")
            
            return True
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            self.error_log.append(f"Setup error: {e}")
            return False
    
    def test_end_to_end_workflow(self) -> bool:
        """Test complete end-to-end RAG workflow."""
        print("\n" + "="*60)
        print("TEST 1: End-to-End Workflow")
        print("="*60)
        
        try:
            # Prepare test documents
            test_docs = self._prepare_test_documents()
            if not test_docs:
                print("❌ Failed to prepare test documents")
                return False
            
            # Ingest documents
            print("📄 Ingesting test documents...")
            ingestion_success = self._ingest_documents(test_docs)
            if not ingestion_success:
                print("❌ Document ingestion failed")
                return False
            
            # Test various query types
            test_queries = [
                ("What is the main topic of the documents?", QueryType.GENERAL),
                ("What are the key features mentioned?", QueryType.FACTUAL),
                ("How do the different concepts relate to each other?", QueryType.ANALYTICAL),
                ("Compare the different approaches discussed.", QueryType.COMPARATIVE),
                ("Summarize the main points.", QueryType.SUMMARIZATION),
                ("Create a creative interpretation of the content.", QueryType.CREATIVE)
            ]
            
            success_count = 0
            for query_text, query_type in test_queries:
                print(f"\n🔍 Testing query: {query_text[:50]}...")
                
                response = self.rag_pipeline.query(
                    query_text,
                    query_type=query_type,
                    top_k=3,
                    max_tokens=200
                )
                
                if response and response.answer:
                    print(f"✅ Query successful")
                    print(f"   - Response length: {len(response.answer)} chars")
                    print(f"   - Sources: {len(response.sources)}")
                    print(f"   - Response time: {response.response_time:.2f}s")
                    success_count += 1
                else:
                    print(f"❌ Query failed")
            
            success_rate = success_count / len(test_queries)
            print(f"\n📊 End-to-end test results: {success_count}/{len(test_queries)} ({success_rate:.1%})")
            
            self.test_results['end_to_end'] = {
                'success_rate': success_rate,
                'total_queries': len(test_queries),
                'successful_queries': success_count
            }
            
            return success_rate >= 0.8  # 80% success rate threshold
            
        except Exception as e:
            print(f"❌ End-to-end test failed: {e}")
            self.error_log.append(f"End-to-end test error: {e}")
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling and graceful degradation."""
        print("\n" + "="*60)
        print("TEST 2: Error Handling & Graceful Degradation")
        print("="*60)
        
        error_tests = [
            ("Empty query", ""),
            ("Very long query", "x" * 10000),
            ("Special characters", "!@#$%^&*()_+-=[]{}|;':\",./<>?"),
            ("Unicode query", "测试查询 with unicode 🚀"),
            ("SQL injection attempt", "'; DROP TABLE users; --"),
            ("XSS attempt", "<script>alert('xss')</script>"),
        ]
        
        success_count = 0
        for test_name, query in error_tests:
            print(f"\n🧪 Testing: {test_name}")
            
            try:
                response = self.rag_pipeline.query(
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
                self.error_log.append(f"Error handling test '{test_name}': {e}")
        
        success_rate = success_count / len(error_tests)
        print(f"\n📊 Error handling test results: {success_count}/{len(error_tests)} ({success_rate:.1%})")
        
        self.test_results['error_handling'] = {
            'success_rate': success_rate,
            'total_tests': len(error_tests),
            'successful_tests': success_count
        }
        
        return success_rate >= 0.8
    
    def test_retry_mechanisms(self) -> bool:
        """Test retry mechanisms and resilience."""
        print("\n" + "="*60)
        print("TEST 3: Retry Mechanisms & Resilience")
        print("="*60)
        
        # Test with different service states
        retry_tests = [
            ("Normal operation", "test query", True),
            ("High load simulation", "test query under load", True),
            ("Service interruption simulation", "test query with service issues", False)
        ]
        
        success_count = 0
        for test_name, query, expect_success in retry_tests:
            print(f"\n🔄 Testing: {test_name}")
            
            try:
                start_time = time.time()
                response = self.rag_pipeline.query(
                    query,
                    top_k=2,
                    max_tokens=100
                )
                response_time = time.time() - start_time
                
                if response and response.answer:
                    print(f"✅ Query successful in {response_time:.2f}s")
                    success_count += 1
                else:
                    print(f"❌ Query failed")
                    
            except Exception as e:
                print(f"❌ Exception: {e}")
                self.error_log.append(f"Retry test '{test_name}': {e}")
        
        success_rate = success_count / len(retry_tests)
        print(f"\n📊 Retry mechanism test results: {success_count}/{len(retry_tests)} ({success_rate:.1%})")
        
        self.test_results['retry_mechanisms'] = {
            'success_rate': success_rate,
            'total_tests': len(retry_tests),
            'successful_tests': success_count
        }
        
        return success_rate >= 0.6  # Lower threshold for retry tests
    
    def test_performance_benchmarks(self) -> bool:
        """Test performance benchmarks and optimization."""
        print("\n" + "="*60)
        print("TEST 4: Performance Benchmarks")
        print("="*60)
        
        # Performance test scenarios
        performance_tests = [
            ("Short query", "What is AI?", 50),
            ("Medium query", "Explain the benefits of machine learning in detail", 100),
            ("Long query", "Provide a comprehensive analysis of artificial intelligence, machine learning, and deep learning technologies, including their applications, limitations, and future prospects", 200),
        ]
        
        performance_results = {}
        
        for test_name, query, max_tokens in performance_tests:
            print(f"\n⚡ Testing: {test_name}")
            
            # Run multiple iterations for accurate timing
            times = []
            for i in range(3):
                try:
                    start_time = time.time()
                    response = self.rag_pipeline.query(
                        query,
                        top_k=3,
                        max_tokens=max_tokens
                    )
                    end_time = time.time()
                    
                    if response and response.answer:
                        times.append(end_time - start_time)
                        print(f"   Iteration {i+1}: {times[-1]:.2f}s")
                    else:
                        print(f"   Iteration {i+1}: Failed")
                        
                except Exception as e:
                    print(f"   Iteration {i+1}: Error - {e}")
            
            if times:
                avg_time = sum(times) / len(times)
                min_time = min(times)
                max_time = max(times)
                
                performance_results[test_name] = {
                    'avg_time': avg_time,
                    'min_time': min_time,
                    'max_time': max_time,
                    'iterations': len(times)
                }
                
                print(f"   📊 Average: {avg_time:.2f}s (min: {min_time:.2f}s, max: {max_time:.2f}s)")
                
                # Performance thresholds
                if avg_time < 5.0:  # 5 second threshold
                    print(f"   ✅ Performance acceptable")
                else:
                    print(f"   ⚠️ Performance slow")
        
        self.test_results['performance'] = performance_results
        
        # Check if all tests meet performance criteria
        acceptable_performance = all(
            result['avg_time'] < 5.0 
            for result in performance_results.values()
        )
        
        return acceptable_performance
    
    def test_response_quality(self) -> bool:
        """Test response quality and validation."""
        print("\n" + "="*60)
        print("TEST 5: Response Quality Validation")
        print("="*60)
        
        quality_tests = [
            ("Factual query", "What are the main benefits of AI?", "factual"),
            ("Analytical query", "How does machine learning work?", "analytical"),
            ("Creative query", "Imagine a future with advanced AI", "creative"),
        ]
        
        quality_scores = []
        
        for test_name, query, expected_type in quality_tests:
            print(f"\n🎯 Testing: {test_name}")
            
            try:
                response = self.rag_pipeline.query(
                    query,
                    query_type=QueryType(expected_type),
                    top_k=3,
                    max_tokens=150
                )
                
                if response and response.answer:
                    # Quality assessment
                    quality_score = self._assess_response_quality(response, expected_type)
                    quality_scores.append(quality_score)
                    
                    print(f"   📝 Response length: {len(response.answer)} chars")
                    print(f"   🎯 Quality score: {quality_score:.2f}/1.0")
                    print(f"   🔗 Sources: {len(response.sources)}")
                    print(f"   ✅ Validation status: {response.validation_status}")
                    print(f"   🛡️ Safety score: {response.safety_score:.2f}")
                    
                else:
                    print(f"   ❌ No response generated")
                    
            except Exception as e:
                print(f"   ❌ Error: {e}")
                self.error_log.append(f"Quality test '{test_name}': {e}")
        
        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)
            print(f"\n📊 Average quality score: {avg_quality:.2f}/1.0")
            
            self.test_results['response_quality'] = {
                'avg_quality_score': avg_quality,
                'total_tests': len(quality_scores),
                'quality_scores': quality_scores
            }
            
            return avg_quality >= 0.6  # 60% quality threshold
        else:
            print("❌ No quality scores available")
            return False
    
    def test_memory_and_resources(self) -> bool:
        """Test memory usage and resource monitoring."""
        print("\n" + "="*60)
        print("TEST 6: Memory & Resource Monitoring")
        print("="*60)
        
        try:
            # Get initial memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            print(f"📊 Initial memory usage: {initial_memory:.1f} MB")
            
            # Run multiple queries to test memory growth
            memory_samples = [initial_memory]
            
            for i in range(5):
                print(f"\n🔄 Memory test iteration {i+1}")
                
                response = self.rag_pipeline.query(
                    f"Test query number {i+1} for memory monitoring",
                    top_k=2,
                    max_tokens=100
                )
                
                current_memory = process.memory_info().rss / 1024 / 1024
                memory_samples.append(current_memory)
                
                print(f"   Current memory: {current_memory:.1f} MB")
                print(f"   Memory change: {current_memory - initial_memory:+.1f} MB")
            
            # Analyze memory patterns
            max_memory = max(memory_samples)
            min_memory = min(memory_samples)
            avg_memory = sum(memory_samples) / len(memory_samples)
            
            print(f"\n📊 Memory Analysis:")
            print(f"   - Peak memory: {max_memory:.1f} MB")
            print(f"   - Average memory: {avg_memory:.1f} MB")
            print(f"   - Memory growth: {max_memory - initial_memory:.1f} MB")
            
            # Check for memory leaks (growth > 100MB)
            memory_growth = max_memory - initial_memory
            memory_acceptable = memory_growth < 100
            
            if memory_acceptable:
                print("✅ Memory usage acceptable")
            else:
                print("⚠️ Potential memory leak detected")
            
            self.test_results['memory_usage'] = {
                'initial_memory_mb': initial_memory,
                'peak_memory_mb': max_memory,
                'avg_memory_mb': avg_memory,
                'memory_growth_mb': memory_growth,
                'memory_acceptable': memory_acceptable
            }
            
            return memory_acceptable
            
        except Exception as e:
            print(f"❌ Memory monitoring failed: {e}")
            self.error_log.append(f"Memory monitoring error: {e}")
            return False
    
    def test_concurrent_operations(self) -> bool:
        """Test concurrent operations and threading."""
        print("\n" + "="*60)
        print("TEST 7: Concurrent Operations")
        print("="*60)
        
        def run_query(query_id: int) -> Dict[str, Any]:
            """Run a single query in a thread."""
            try:
                start_time = time.time()
                response = self.rag_pipeline.query(
                    f"Concurrent test query {query_id}",
                    top_k=2,
                    max_tokens=50
                )
                end_time = time.time()
                
                return {
                    'query_id': query_id,
                    'success': response is not None and response.answer is not None,
                    'response_time': end_time - start_time,
                    'response_length': len(response.answer) if response and response.answer else 0
                }
            except Exception as e:
                return {
                    'query_id': query_id,
                    'success': False,
                    'error': str(e),
                    'response_time': 0,
                    'response_length': 0
                }
        
        # Run concurrent queries
        num_concurrent = 3
        threads = []
        results = []
        
        print(f"🚀 Starting {num_concurrent} concurrent queries...")
        
        for i in range(num_concurrent):
            thread = threading.Thread(
                target=lambda i=i: results.append(run_query(i)),
                daemon=True
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join(timeout=30)  # 30 second timeout
        
        # Analyze results
        successful_queries = [r for r in results if r['success']]
        failed_queries = [r for r in results if not r['success']]
        
        if successful_queries:
            avg_response_time = sum(r['response_time'] for r in successful_queries) / len(successful_queries)
            print(f"✅ Concurrent test completed")
            print(f"   - Successful queries: {len(successful_queries)}/{num_concurrent}")
            print(f"   - Average response time: {avg_response_time:.2f}s")
            print(f"   - Failed queries: {len(failed_queries)}")
        else:
            print("❌ All concurrent queries failed")
        
        success_rate = len(successful_queries) / num_concurrent
        
        self.test_results['concurrent_operations'] = {
            'success_rate': success_rate,
            'total_queries': num_concurrent,
            'successful_queries': len(successful_queries),
            'avg_response_time': avg_response_time if successful_queries else 0,
            'failed_queries': len(failed_queries)
        }
        
        return success_rate >= 0.6  # 60% success rate for concurrent operations
    
    def _prepare_test_documents(self) -> List[Path]:
        """Prepare test documents for ingestion."""
        data_dir = Path(__file__).parent.parent / "data" / "test_documents"
        
        if not data_dir.exists():
            print(f"❌ Test documents directory not found: {data_dir}")
            return []
        
        test_files = [
            "simple_test.txt",
            "sample_data.csv",
            "markdown_test.md"
        ]
        
        available_files = []
        for file_name in test_files:
            file_path = data_dir / file_name
            if file_path.exists():
                available_files.append(file_path)
            else:
                print(f"⚠️ Test file not found: {file_name}")
        
        return available_files
    
    def _ingest_documents(self, document_paths: List[Path]) -> bool:
        """Ingest documents into the vector store."""
        try:
            document_processor = self.service_factory.get_document_processor()
            vector_store = self.service_factory.get_vector_store()
            
            if not document_processor or not vector_store:
                return False
            
            total_chunks = 0
            for doc_path in document_paths:
                print(f"   Processing: {doc_path.name}")
                
                processed_docs = document_processor.process_file(str(doc_path))
                if processed_docs:
                    for doc in processed_docs:
                        vector_store.add_document(doc)
                    total_chunks += len(processed_docs)
                    print(f"     Added {len(processed_docs)} chunks")
                else:
                    print(f"     Failed to process")
            
            print(f"📊 Total chunks ingested: {total_chunks}")
            return total_chunks > 0
            
        except Exception as e:
            print(f"❌ Document ingestion failed: {e}")
            self.error_log.append(f"Document ingestion error: {e}")
            return False
    
    def _assess_response_quality(self, response: RAGResponse, expected_type: str) -> float:
        """Assess response quality based on various criteria."""
        if not response or not response.answer:
            return 0.0
        
        score = 0.0
        answer = response.answer.lower()
        
        # Length assessment (not too short, not too long)
        if 50 <= len(response.answer) <= 500:
            score += 0.2
        elif 20 <= len(response.answer) <= 1000:
            score += 0.1
        
        # Source attribution
        if response.sources and len(response.sources) > 0:
            score += 0.2
        
        # Validation status
        if response.validation_status == "valid":
            score += 0.2
        elif response.validation_status == "warning":
            score += 0.1
        
        # Safety score
        score += response.safety_score * 0.2
        
        # Content relevance (basic keyword matching)
        relevant_keywords = ["ai", "machine", "learning", "technology", "data", "algorithm"]
        keyword_matches = sum(1 for keyword in relevant_keywords if keyword in answer)
        score += min(keyword_matches / len(relevant_keywords), 0.2)
        
        return min(score, 1.0)
    
    def generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report."""
        print("\n" + "="*80)
        print("📊 PHASE 5.3 TEST REPORT")
        print("="*80)
        
        # Calculate overall success rate
        test_categories = [
            'end_to_end', 'error_handling', 'retry_mechanisms', 
            'performance', 'response_quality', 'memory_usage', 'concurrent_operations'
        ]
        
        successful_tests = 0
        total_tests = 0
        
        for category in test_categories:
            if category in self.test_results:
                if 'success_rate' in self.test_results[category]:
                    successful_tests += 1 if self.test_results[category]['success_rate'] >= 0.8 else 0
                    total_tests += 1
                elif category == 'performance':
                    # Performance test passes if all tests meet criteria
                    performance_acceptable = all(
                        result['avg_time'] < 5.0 
                        for result in self.test_results[category].values()
                        if isinstance(result, dict) and 'avg_time' in result
                    )
                    successful_tests += 1 if performance_acceptable else 0
                    total_tests += 1
                elif category == 'memory_usage':
                    successful_tests += 1 if self.test_results[category].get('memory_acceptable', False) else 0
                    total_tests += 1
                elif category == 'response_quality':
                    avg_quality = self.test_results[category].get('avg_quality_score', 0)
                    successful_tests += 1 if avg_quality >= 0.6 else 0
                    total_tests += 1
                elif category == 'concurrent_operations':
                    success_rate = self.test_results[category].get('success_rate', 0)
                    successful_tests += 1 if success_rate >= 0.6 else 0
                    total_tests += 1
        
        overall_success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        # Generate report
        report = {
            'phase': '5.3',
            'test_date': time.strftime('%Y-%m-%d %H:%M:%S'),
            'overall_success_rate': overall_success_rate,
            'successful_tests': successful_tests,
            'total_tests': total_tests,
            'test_results': self.test_results,
            'error_log': self.error_log,
            'recommendations': self._generate_recommendations()
        }
        
        # Print summary
        print(f"🎯 Overall Success Rate: {overall_success_rate:.1%} ({successful_tests}/{total_tests})")
        print(f"📝 Error Count: {len(self.error_log)}")
        
        if overall_success_rate >= 0.8:
            print("✅ Phase 5.3 PASSED - Pipeline ready for production")
        elif overall_success_rate >= 0.6:
            print("⚠️ Phase 5.3 PARTIAL - Some issues need attention")
        else:
            print("❌ Phase 5.3 FAILED - Significant issues detected")
        
        # Print detailed results
        for category, results in self.test_results.items():
            print(f"\n📋 {category.replace('_', ' ').title()}:")
            if isinstance(results, dict):
                for key, value in results.items():
                    if isinstance(value, float):
                        print(f"   {key}: {value:.3f}")
                    else:
                        print(f"   {key}: {value}")
        
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results."""
        recommendations = []
        
        # Analyze test results and generate recommendations
        if 'end_to_end' in self.test_results:
            success_rate = self.test_results['end_to_end']['success_rate']
            if success_rate < 0.8:
                recommendations.append("Improve end-to-end workflow reliability")
        
        if 'error_handling' in self.test_results:
            success_rate = self.test_results['error_handling']['success_rate']
            if success_rate < 0.8:
                recommendations.append("Enhance error handling mechanisms")
        
        if 'performance' in self.test_results:
            for test_name, results in self.test_results['performance'].items():
                if results['avg_time'] > 5.0:
                    recommendations.append(f"Optimize performance for {test_name}")
        
        if 'memory_usage' in self.test_results:
            if not self.test_results['memory_usage']['memory_acceptable']:
                recommendations.append("Investigate memory usage patterns")
        
        if 'response_quality' in self.test_results:
            avg_quality = self.test_results['response_quality']['avg_quality_score']
            if avg_quality < 0.6:
                recommendations.append("Improve response quality and validation")
        
        if not recommendations:
            recommendations.append("All systems performing well - ready for next phase")
        
        return recommendations


def main():
    """Main testing function."""
    print("🚀 ZeroRAG Phase 5.3: Pipeline Testing")
    print("="*80)
    
    # Initialize tester
    tester = PipelineTester()
    
    # Run setup
    if not tester.setup():
        print("❌ Setup failed - cannot proceed with testing")
        return False
    
    # Run all tests
    tests = [
        ("End-to-End Workflow", tester.test_end_to_end_workflow),
        ("Error Handling", tester.test_error_handling),
        ("Retry Mechanisms", tester.test_retry_mechanisms),
        ("Performance Benchmarks", tester.test_performance_benchmarks),
        ("Response Quality", tester.test_response_quality),
        ("Memory & Resources", tester.test_memory_and_resources),
        ("Concurrent Operations", tester.test_concurrent_operations),
    ]
    
    print(f"\n🧪 Running {len(tests)} test categories...")
    
    for test_name, test_func in tests:
        try:
            test_func()
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
            tester.error_log.append(f"{test_name} test exception: {e}")
    
    # Generate and save report
    report = tester.generate_test_report()
    
    # Save report to file
    report_file = Path(__file__).parent / "phase_5_3_test_report.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Test report saved to: {report_file}")
    
    return report['overall_success_rate'] >= 0.8


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
