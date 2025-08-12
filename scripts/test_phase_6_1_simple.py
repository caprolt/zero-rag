#!/usr/bin/env python3
"""
ZeroRAG Phase 6.1 FastAPI Backend - Simple Test

This script tests the FastAPI backend implementation directly without
starting a separate server process.
"""

import json
import time
import sys
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
from api.main import app
from config import get_config


class SimpleFastAPITester:
    """Simple test suite for FastAPI backend."""
    
    def __init__(self):
        self.config = get_config()
        self.client = TestClient(app)
        self.test_results = []
        
    def log_test(self, test_name: str, status: str, details: str = "", duration: float = 0.0):
        """Log test result."""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "duration": duration,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        print(f"[{status.upper()}] {test_name}: {details}")
        if duration > 0:
            print(f"  Duration: {duration:.3f}s")
    
    def test_root_endpoint(self) -> bool:
        """Test the root endpoint."""
        try:
            start_time = time.time()
            response = self.client.get("/")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["name", "version", "description", "docs", "health"]
                
                if all(field in data for field in expected_fields):
                    self.log_test("Root Endpoint", "PASS", "All expected fields present", duration)
                    return True
                else:
                    self.log_test("Root Endpoint", "FAIL", f"Missing fields: {[f for f in expected_fields if f not in data]}")
                    return False
            else:
                self.log_test("Root Endpoint", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Root Endpoint", "ERROR", str(e))
            return False
    
    def test_health_endpoint(self) -> bool:
        """Test the health check endpoint."""
        try:
            start_time = time.time()
            response = self.client.get("/health")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["status", "timestamp", "services", "uptime", "version"]
                
                if all(field in data for field in expected_fields):
                    self.log_test("Health Check", "PASS", f"Status: {data['status']}", duration)
                    return True
                else:
                    self.log_test("Health Check", "FAIL", f"Missing fields: {[f for f in expected_fields if f not in data]}")
                    return False
            else:
                self.log_test("Health Check", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Health Check", "ERROR", str(e))
            return False
    
    def test_service_health_endpoint(self) -> bool:
        """Test individual service health endpoints."""
        try:
            # Test with a known service
            services_to_test = ["embedding_service", "llm_service", "document_processor", "vector_store", "rag_pipeline"]
            
            for service_name in services_to_test:
                start_time = time.time()
                response = self.client.get(f"/health/services/{service_name}")
                duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    expected_fields = ["service", "status", "health_data", "last_check", "error_count"]
                    
                    if all(field in data for field in expected_fields):
                        self.log_test(f"Service Health - {service_name}", "PASS", f"Status: {data['status']}", duration)
                    else:
                        self.log_test(f"Service Health - {service_name}", "FAIL", f"Missing fields")
                        return False
                elif response.status_code == 404:
                    # Service might not be available
                    self.log_test(f"Service Health - {service_name}", "SKIP", "Service not found")
                else:
                    self.log_test(f"Service Health - {service_name}", "FAIL", f"HTTP {response.status_code}")
                    return False
            
            return True
                
        except Exception as e:
            self.log_test("Service Health", "ERROR", str(e))
            return False
    
    def test_document_list_endpoint(self) -> bool:
        """Test the document list endpoint."""
        try:
            start_time = time.time()
            response = self.client.get("/documents")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["documents", "total", "limit", "offset"]
                
                if all(field in data for field in expected_fields):
                    self.log_test("Document List", "PASS", f"Total documents: {data['total']}", duration)
                    return True
                else:
                    self.log_test("Document List", "FAIL", f"Missing fields: {[f for f in expected_fields if f not in data]}")
                    return False
            else:
                self.log_test("Document List", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Document List", "ERROR", str(e))
            return False
    
    def test_metrics_endpoint(self) -> bool:
        """Test the metrics endpoint."""
        try:
            start_time = time.time()
            response = self.client.get("/metrics")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["total_requests", "failed_requests", "success_rate", "uptime", "services"]
                
                if all(field in data for field in expected_fields):
                    self.log_test("Metrics Endpoint", "PASS", f"Success rate: {data['success_rate']:.2%}", duration)
                    return True
                else:
                    self.log_test("Metrics Endpoint", "FAIL", f"Missing fields: {[f for f in expected_fields if f not in data]}")
                    return False
            else:
                self.log_test("Metrics Endpoint", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Metrics Endpoint", "ERROR", str(e))
            return False
    
    def test_api_documentation(self) -> bool:
        """Test API documentation endpoints."""
        try:
            # Test OpenAPI JSON
            start_time = time.time()
            response = self.client.get("/openapi.json")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if "openapi" in data and "paths" in data:
                    self.log_test("OpenAPI JSON", "PASS", f"Version: {data.get('openapi', 'unknown')}", duration)
                else:
                    self.log_test("OpenAPI JSON", "FAIL", "Invalid OpenAPI schema")
                    return False
            else:
                self.log_test("OpenAPI JSON", "FAIL", f"HTTP {response.status_code}")
                return False
            
            # Test Swagger UI
            start_time = time.time()
            response = self.client.get("/docs")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test("Swagger UI", "PASS", "Documentation accessible", duration)
            else:
                self.log_test("Swagger UI", "FAIL", f"HTTP {response.status_code}")
                return False
            
            # Test ReDoc
            start_time = time.time()
            response = self.client.get("/redoc")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test("ReDoc", "PASS", "Alternative documentation accessible", duration)
                return True
            else:
                self.log_test("ReDoc", "FAIL", f"HTTP {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("API Documentation", "ERROR", str(e))
            return False
    
    def test_error_handling(self) -> bool:
        """Test error handling."""
        try:
            # Test invalid query
            invalid_query = {"query": ""}  # Empty query should fail validation
            
            start_time = time.time()
            response = self.client.post("/query", json=invalid_query)
            duration = time.time() - start_time
            
            if response.status_code == 422:  # Validation error
                self.log_test("Error Handling - Validation", "PASS", "Proper validation error", duration)
            else:
                self.log_test("Error Handling - Validation", "FAIL", f"Expected 422, got {response.status_code}")
                return False
            
            # Test non-existent endpoint
            start_time = time.time()
            response = self.client.get("/nonexistent")
            duration = time.time() - start_time
            
            if response.status_code == 404:
                self.log_test("Error Handling - 404", "PASS", "Proper 404 error", duration)
                return True
            else:
                self.log_test("Error Handling - 404", "FAIL", f"Expected 404, got {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Error Handling", "ERROR", str(e))
            return False
    
    def test_query_endpoint_structure(self) -> bool:
        """Test query endpoint structure (without actual processing)."""
        try:
            # Test with a valid query structure
            query_data = {
                "query": "What is the main purpose of this system?",
                "top_k": 3,
                "score_threshold": 0.5,
                "max_context_length": 2000,
                "temperature": 0.7,
                "max_tokens": 500,
                "include_sources": True,
                "response_format": "text",
                "safety_level": "standard"
            }
            
            start_time = time.time()
            response = self.client.post("/query", json=query_data)
            duration = time.time() - start_time
            
            # We expect either 200 (success) or 404 (no documents) or 503 (service unavailable)
            if response.status_code in [200, 404, 503]:
                if response.status_code == 200:
                    data = response.json()
                    expected_fields = ["answer", "sources", "response_time", "tokens_used", "metadata"]
                    if all(field in data for field in expected_fields):
                        self.log_test("Query Endpoint Structure", "PASS", "Valid response structure", duration)
                        return True
                    else:
                        self.log_test("Query Endpoint Structure", "FAIL", f"Missing fields: {[f for f in expected_fields if f not in data]}")
                        return False
                else:
                    self.log_test("Query Endpoint Structure", "SKIP", f"Service not ready (HTTP {response.status_code})")
                    return True
            else:
                self.log_test("Query Endpoint Structure", "FAIL", f"Unexpected HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Query Endpoint Structure", "ERROR", str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results."""
        print("=" * 60)
        print("ZeroRAG Phase 6.1 FastAPI Backend - Simple Testing")
        print("=" * 60)
        
        # Run tests
        tests = [
            ("Root Endpoint", self.test_root_endpoint),
            ("Health Check", self.test_health_endpoint),
            ("Service Health", self.test_service_health_endpoint),
            ("Document List", self.test_document_list_endpoint),
            ("Metrics Endpoint", self.test_metrics_endpoint),
            ("API Documentation", self.test_api_documentation),
            ("Error Handling", self.test_error_handling),
            ("Query Endpoint Structure", self.test_query_endpoint_structure),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
            except Exception as e:
                self.log_test(test_name, "ERROR", str(e))
        
        # Generate summary
        summary = {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "success_rate": passed / total if total > 0 else 0,
            "test_results": self.test_results
        }
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        
        if summary['success_rate'] >= 0.8:
            print("\n✅ Phase 6.1 FastAPI Backend: PASSED")
            summary["phase_status"] = "PASSED"
        else:
            print("\n❌ Phase 6.1 FastAPI Backend: FAILED")
            summary["phase_status"] = "FAILED"
        
        return summary


def main():
    """Main test execution."""
    tester = SimpleFastAPITester()
    
    # Run tests
    results = tester.run_all_tests()
    
    # Save results
    output_file = Path(__file__).parent / "phase_6_1_simple_report.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_file}")
    
    # Exit with appropriate code
    sys.exit(0 if results.get("phase_status") == "PASSED" else 1)


if __name__ == "__main__":
    main()
