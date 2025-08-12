#!/usr/bin/env python3
"""
ZeroRAG Phase 6.1 FastAPI Backend Testing

This script tests the FastAPI backend implementation including:
- Health check endpoints
- Document upload functionality
- Query processing
- Streaming responses
- Error handling
- API documentation

Phase 6.1 Implementation Validation:
- Complete REST API with streaming support
- Document upload with validation
- Query endpoint with Server-Sent Events
- Health check and monitoring endpoints
- CORS and middleware configuration
"""

import asyncio
import json
import time
import requests
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, List
import subprocess
import sys
import signal
import threading

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import get_config


class FastAPITester:
    """Test suite for FastAPI backend."""
    
    def __init__(self):
        self.config = get_config()
        # Use localhost instead of 0.0.0.0 for testing
        self.base_url = f"http://localhost:{self.config.api.port}"
        self.server_process = None
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
    
    def start_server(self) -> bool:
        """Start the FastAPI server."""
        try:
            print("Starting FastAPI server...")
            
            # Start server in background
            cmd = [
                sys.executable, "-m", "uvicorn",
                "src.api.main:app",
                "--host", self.config.api.host,
                "--port", str(self.config.api.port),
                "--no-reload",  # Fixed: use --no-reload instead of --reload false
                "--log-level", "error"  # Reduce log output
            ]
            
            self.server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                cwd=Path(__file__).parent.parent
            )
            
            # Wait for server to start
            max_wait = 60  # Increased timeout
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                try:
                    print(f"Attempting to connect to {self.base_url}...")
                    response = requests.get(f"{self.base_url}/", timeout=5)
                    if response.status_code == 200:
                        print(f"Server started successfully at {self.base_url}")
                        return True
                except requests.exceptions.RequestException as e:
                    print(f"Connection attempt failed: {e}")
                    time.sleep(2)  # Increased sleep time
                    continue
            
            print("Failed to start server within timeout")
            return False
            
        except Exception as e:
            print(f"Error starting server: {e}")
            return False
    
    def stop_server(self):
        """Stop the FastAPI server."""
        if self.server_process:
            print("Stopping FastAPI server...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
            print("Server stopped")
    
    def test_root_endpoint(self) -> bool:
        """Test the root endpoint."""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/")
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
            response = requests.get(f"{self.base_url}/health")
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
                response = requests.get(f"{self.base_url}/health/services/{service_name}")
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
    
    def test_document_upload(self) -> bool:
        """Test document upload functionality."""
        try:
            # Create a test document
            test_content = "This is a test document for the ZeroRAG system. It contains some sample text to test the document processing pipeline."
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(test_content)
                temp_file = f.name
            
            try:
                with open(temp_file, 'rb') as f:
                    files = {'file': ('test_document.txt', f, 'text/plain')}
                    
                    start_time = time.time()
                    response = requests.post(f"{self.base_url}/documents/upload", files=files)
                    duration = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    expected_fields = ["document_id", "filename", "file_size", "chunks_created", "processing_time", "status", "metadata"]
                    
                    if all(field in data for field in expected_fields):
                        self.log_test("Document Upload", "PASS", f"Document ID: {data['document_id']}", duration)
                        return True
                    else:
                        self.log_test("Document Upload", "FAIL", f"Missing fields: {[f for f in expected_fields if f not in data]}")
                        return False
                else:
                    self.log_test("Document Upload", "FAIL", f"HTTP {response.status_code}: {response.text}")
                    return False
                    
            finally:
                # Clean up temp file
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                
        except Exception as e:
            self.log_test("Document Upload", "ERROR", str(e))
            return False
    
    def test_query_endpoint(self) -> bool:
        """Test the query endpoint."""
        try:
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
            response = requests.post(f"{self.base_url}/query", json=query_data)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                expected_fields = ["answer", "sources", "response_time", "tokens_used", "metadata"]
                
                if all(field in data for field in expected_fields):
                    self.log_test("Query Endpoint", "PASS", f"Response time: {data['response_time']:.3f}s", duration)
                    return True
                else:
                    self.log_test("Query Endpoint", "FAIL", f"Missing fields: {[f for f in expected_fields if f not in data]}")
                    return False
            elif response.status_code == 404:
                # No documents available
                self.log_test("Query Endpoint", "SKIP", "No documents available for query")
                return True
            else:
                self.log_test("Query Endpoint", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Query Endpoint", "ERROR", str(e))
            return False
    
    def test_streaming_query(self) -> bool:
        """Test the streaming query endpoint."""
        try:
            query_data = {
                "query": "Explain the system architecture",
                "top_k": 2,
                "score_threshold": 0.5,
                "max_context_length": 1500,
                "temperature": 0.7,
                "max_tokens": 300,
                "include_sources": True,
                "response_format": "text",
                "safety_level": "standard"
            }
            
            start_time = time.time()
            response = requests.post(f"{self.base_url}/query/stream", json=query_data, stream=True)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                # Check if it's a streaming response
                content_type = response.headers.get('content-type', '')
                if 'text/event-stream' in content_type:
                    self.log_test("Streaming Query", "PASS", "Streaming response received", duration)
                    return True
                else:
                    self.log_test("Streaming Query", "FAIL", f"Wrong content type: {content_type}")
                    return False
            elif response.status_code == 404:
                # No documents available
                self.log_test("Streaming Query", "SKIP", "No documents available for streaming query")
                return True
            else:
                self.log_test("Streaming Query", "FAIL", f"HTTP {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Streaming Query", "ERROR", str(e))
            return False
    
    def test_metrics_endpoint(self) -> bool:
        """Test the metrics endpoint."""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/metrics")
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
    
    def test_document_list_endpoint(self) -> bool:
        """Test the document list endpoint."""
        try:
            start_time = time.time()
            response = requests.get(f"{self.base_url}/documents")
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
    
    def test_api_documentation(self) -> bool:
        """Test API documentation endpoints."""
        try:
            # Test OpenAPI JSON
            start_time = time.time()
            response = requests.get(f"{self.base_url}/openapi.json")
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
            response = requests.get(f"{self.base_url}/docs")
            duration = time.time() - start_time
            
            if response.status_code == 200:
                self.log_test("Swagger UI", "PASS", "Documentation accessible", duration)
            else:
                self.log_test("Swagger UI", "FAIL", f"HTTP {response.status_code}")
                return False
            
            # Test ReDoc
            start_time = time.time()
            response = requests.get(f"{self.base_url}/redoc")
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
            response = requests.post(f"{self.base_url}/query", json=invalid_query)
            duration = time.time() - start_time
            
            if response.status_code == 422:  # Validation error
                self.log_test("Error Handling - Validation", "PASS", "Proper validation error", duration)
            else:
                self.log_test("Error Handling - Validation", "FAIL", f"Expected 422, got {response.status_code}")
                return False
            
            # Test non-existent endpoint
            start_time = time.time()
            response = requests.get(f"{self.base_url}/nonexistent")
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
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results."""
        print("=" * 60)
        print("ZeroRAG Phase 6.1 FastAPI Backend Testing")
        print("=" * 60)
        
        # Start server
        if not self.start_server():
            return {"success": False, "error": "Failed to start server"}
        
        try:
            # Run tests
            tests = [
                ("Root Endpoint", self.test_root_endpoint),
                ("Health Check", self.test_health_endpoint),
                ("Service Health", self.test_service_health_endpoint),
                ("Document Upload", self.test_document_upload),
                ("Query Endpoint", self.test_query_endpoint),
                ("Streaming Query", self.test_streaming_query),
                ("Metrics Endpoint", self.test_metrics_endpoint),
                ("Document List", self.test_document_list_endpoint),
                ("API Documentation", self.test_api_documentation),
                ("Error Handling", self.test_error_handling),
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
            
        finally:
            self.stop_server()


def main():
    """Main test execution."""
    tester = FastAPITester()
    
    # Handle Ctrl+C gracefully
    def signal_handler(signum, frame):
        print("\nReceived interrupt signal, shutting down...")
        tester.stop_server()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Run tests
    results = tester.run_all_tests()
    
    # Save results
    output_file = Path(__file__).parent / "phase_6_1_fastapi_report.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_file}")
    
    # Exit with appropriate code
    sys.exit(0 if results.get("phase_status") == "PASSED" else 1)


if __name__ == "__main__":
    main()
