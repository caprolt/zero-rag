#!/usr/bin/env python3
"""
Test Script for Phase 6.2: Advanced API Features

This script tests the advanced API features implemented in Phase 6.2:
- Enhanced file upload handling with progress tracking
- Advanced file validation and preprocessing
- Streaming responses with connection management
- Cleanup mechanisms and storage management
"""

import asyncio
import json
import time
import uuid
from pathlib import Path
from typing import Dict, Any

import httpx
import pytest

# Test configuration
API_BASE_URL = "http://localhost:8000"
TEST_FILES_DIR = Path("data/test_documents")


class TestPhase62AdvancedFeatures:
    """Test suite for Phase 6.2 advanced API features."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_results = []
    
    async def setup(self):
        """Setup test environment."""
        print("🔧 Setting up Phase 6.2 Advanced Features test environment...")
        
        # Ensure test files directory exists
        TEST_FILES_DIR.mkdir(parents=True, exist_ok=True)
        
        # Create test files
        await self._create_test_files()
        
        print("✅ Test environment setup complete")
    
    async def _create_test_files(self):
        """Create test files for validation testing."""
        test_files = {
            "valid_document.txt": "This is a valid test document with some content.",
            "large_document.txt": "Large document content. " * 1000,  # ~25KB
            "markdown_document.md": "# Test Document\n\nThis is a **markdown** document with `code`.",
            "csv_document.csv": "name,age,city\nJohn,30,New York\nJane,25,Los Angeles",
            "json_document.json": '{"name": "test", "data": [1, 2, 3], "nested": {"key": "value"}}'
        }
        
        for filename, content in test_files.items():
            file_path = TEST_FILES_DIR / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
    
    async def test_1_file_validation(self):
        """Test file validation endpoint."""
        print("\n🧪 Testing file validation...")
        
        test_cases = [
            {
                "name": "valid_txt_file",
                "request": {
                    "filename": "document.txt",
                    "file_size": 1024,
                    "content_type": "text/plain"
                },
                "expected_valid": True
            },
            {
                "name": "large_file",
                "request": {
                    "filename": "large_document.txt",
                    "file_size": 100 * 1024 * 1024,  # 100MB
                    "content_type": "text/plain"
                },
                "expected_valid": False
            },
            {
                "name": "unsupported_format",
                "request": {
                    "filename": "document.exe",
                    "file_size": 1024,
                    "content_type": "application/octet-stream"
                },
                "expected_valid": False
            },
            {
                "name": "markdown_file",
                "request": {
                    "filename": "document.md",
                    "file_size": 2048,
                    "content_type": "text/markdown"
                },
                "expected_valid": True
            }
        ]
        
        for test_case in test_cases:
            try:
                response = await self.client.post(
                    f"{API_BASE_URL}/documents/validate",
                    json=test_case["request"]
                )
                
                if response.status_code == 200:
                    result = response.json()
                    is_valid = result["is_valid"] == test_case["expected_valid"]
                    
                    self.test_results.append({
                        "test": f"file_validation_{test_case['name']}",
                        "status": "PASS" if is_valid else "FAIL",
                        "details": {
                            "expected_valid": test_case["expected_valid"],
                            "actual_valid": result["is_valid"],
                            "errors": result.get("errors", []),
                            "warnings": result.get("warnings", []),
                            "supported_features": result.get("supported_features", [])
                        }
                    })
                    
                    print(f"  ✅ {test_case['name']}: {'PASS' if is_valid else 'FAIL'}")
                else:
                    self.test_results.append({
                        "test": f"file_validation_{test_case['name']}",
                        "status": "ERROR",
                        "details": {"error": f"HTTP {response.status_code}: {response.text}"}
                    })
                    print(f"  ❌ {test_case['name']}: ERROR (HTTP {response.status_code})")
                    
            except Exception as e:
                self.test_results.append({
                    "test": f"file_validation_{test_case['name']}",
                    "status": "ERROR",
                    "details": {"error": str(e)}
                })
                print(f"  ❌ {test_case['name']}: ERROR ({e})")
    
    async def test_2_enhanced_upload_with_progress(self):
        """Test enhanced file upload with progress tracking."""
        print("\n🧪 Testing enhanced file upload with progress tracking...")
        
        try:
            # Upload a test file
            test_file_path = TEST_FILES_DIR / "valid_document.txt"
            
            with open(test_file_path, 'rb') as f:
                files = {"file": ("valid_document.txt", f, "text/plain")}
                response = await self.client.post(
                    f"{API_BASE_URL}/documents/upload",
                    files=files
                )
            
            if response.status_code == 200:
                upload_result = response.json()
                document_id = upload_result["document_id"]
                
                print(f"  📤 Upload initiated: {document_id}")
                
                # Monitor progress
                max_attempts = 30
                for attempt in range(max_attempts):
                    progress_response = await self.client.get(
                        f"{API_BASE_URL}/documents/upload/{document_id}/progress"
                    )
                    
                    if progress_response.status_code == 200:
                        progress = progress_response.json()
                        print(f"  📊 Progress: {progress['progress']:.1f}% - {progress['current_step']}")
                        
                        if progress['status'] in ['completed', 'failed']:
                            break
                    
                    await asyncio.sleep(2)
                
                # Final progress check
                final_progress = await self.client.get(
                    f"{API_BASE_URL}/documents/upload/{document_id}/progress"
                )
                
                if final_progress.status_code == 200:
                    final_result = final_progress.json()
                    success = final_result['status'] == 'completed'
                    
                    self.test_results.append({
                        "test": "enhanced_upload_with_progress",
                        "status": "PASS" if success else "FAIL",
                        "details": {
                            "document_id": document_id,
                            "final_status": final_result['status'],
                            "final_progress": final_result['progress'],
                            "processing_time": final_result.get('estimated_time_remaining'),
                            "error_message": final_result.get('error_message')
                        }
                    })
                    
                    print(f"  ✅ Upload progress tracking: {'PASS' if success else 'FAIL'}")
                else:
                    self.test_results.append({
                        "test": "enhanced_upload_with_progress",
                        "status": "ERROR",
                        "details": {"error": f"Failed to get final progress: HTTP {final_progress.status_code}"}
                    })
                    print(f"  ❌ Upload progress tracking: ERROR")
            else:
                self.test_results.append({
                    "test": "enhanced_upload_with_progress",
                    "status": "ERROR",
                    "details": {"error": f"Upload failed: HTTP {response.status_code}"}
                })
                print(f"  ❌ Upload progress tracking: ERROR (Upload failed)")
                
        except Exception as e:
            self.test_results.append({
                "test": "enhanced_upload_with_progress",
                "status": "ERROR",
                "details": {"error": str(e)}
            })
            print(f"  ❌ Upload progress tracking: ERROR ({e})")
    
    async def test_3_streaming_connection_management(self):
        """Test streaming connection management."""
        print("\n🧪 Testing streaming connection management...")
        
        try:
            # Start a streaming query
            query_data = {
                "query": "What is artificial intelligence?",
                "top_k": 3,
                "include_sources": True
            }
            
            # Create streaming connection
            async with self.client.stream(
                "POST",
                f"{API_BASE_URL}/query/stream",
                json=query_data
            ) as response:
                
                if response.status_code == 200:
                    connection_id = response.headers.get("X-Connection-ID")
                    print(f"  🔗 Streaming connection created: {connection_id}")
                    
                    # List active connections
                    connections_response = await self.client.get(
                        f"{API_BASE_URL}/advanced/connections"
                    )
                    
                    if connections_response.status_code == 200:
                        connections = connections_response.json()
                        active_connections = [c for c in connections if c['status'] == 'active']
                        
                        connection_found = any(c['connection_id'] == connection_id for c in active_connections)
                        
                        self.test_results.append({
                            "test": "streaming_connection_management",
                            "status": "PASS" if connection_found else "FAIL",
                            "details": {
                                "connection_id": connection_id,
                                "active_connections_count": len(active_connections),
                                "connection_found": connection_found
                            }
                        })
                        
                        print(f"  ✅ Connection management: {'PASS' if connection_found else 'FAIL'}")
                        
                        # Close the connection
                        if connection_id:
                            close_response = await self.client.delete(
                                f"{API_BASE_URL}/advanced/connections/{connection_id}"
                            )
                            
                            if close_response.status_code == 200:
                                print(f"  🔒 Connection closed: {connection_id}")
                            else:
                                print(f"  ⚠️ Failed to close connection: HTTP {close_response.status_code}")
                    else:
                        self.test_results.append({
                            "test": "streaming_connection_management",
                            "status": "ERROR",
                            "details": {"error": f"Failed to list connections: HTTP {connections_response.status_code}"}
                        })
                        print(f"  ❌ Connection management: ERROR")
                else:
                    self.test_results.append({
                        "test": "streaming_connection_management",
                        "status": "ERROR",
                        "details": {"error": f"Streaming query failed: HTTP {response.status_code}"}
                    })
                    print(f"  ❌ Connection management: ERROR (Streaming failed)")
                    
        except Exception as e:
            self.test_results.append({
                "test": "streaming_connection_management",
                "status": "ERROR",
                "details": {"error": str(e)}
            })
            print(f"  ❌ Connection management: ERROR ({e})")
    
    async def test_4_cleanup_mechanisms(self):
        """Test cleanup mechanisms."""
        print("\n🧪 Testing cleanup mechanisms...")
        
        try:
            # Get storage stats before cleanup
            stats_before = await self.client.get(f"{API_BASE_URL}/advanced/storage/stats")
            
            if stats_before.status_code == 200:
                before_stats = stats_before.json()
                print(f"  📊 Storage before cleanup: {before_stats.get('total_size', 0)} bytes")
                
                # Perform dry run cleanup
                cleanup_request = {
                    "older_than_days": 1,
                    "dry_run": True
                }
                
                cleanup_response = await self.client.post(
                    f"{API_BASE_URL}/advanced/cleanup",
                    json=cleanup_request
                )
                
                if cleanup_response.status_code == 200:
                    cleanup_result = cleanup_response.json()
                    
                    self.test_results.append({
                        "test": "cleanup_mechanisms",
                        "status": "PASS",
                        "details": {
                            "dry_run": cleanup_result['dry_run'],
                            "deleted_documents": cleanup_result['deleted_documents'],
                            "deleted_files": cleanup_result['deleted_files'],
                            "freed_space_bytes": cleanup_result['freed_space_bytes'],
                            "errors": cleanup_result['errors']
                        }
                    })
                    
                    print(f"  ✅ Cleanup mechanisms: PASS")
                    print(f"    📁 Would delete {cleanup_result['deleted_files']} files")
                    print(f"    💾 Would free {cleanup_result['freed_space_bytes']} bytes")
                else:
                    self.test_results.append({
                        "test": "cleanup_mechanisms",
                        "status": "ERROR",
                        "details": {"error": f"Cleanup failed: HTTP {cleanup_response.status_code}"}
                    })
                    print(f"  ❌ Cleanup mechanisms: ERROR")
            else:
                self.test_results.append({
                    "test": "cleanup_mechanisms",
                    "status": "ERROR",
                    "details": {"error": f"Failed to get storage stats: HTTP {stats_before.status_code}"}
                })
                print(f"  ❌ Cleanup mechanisms: ERROR")
                
        except Exception as e:
            self.test_results.append({
                "test": "cleanup_mechanisms",
                "status": "ERROR",
                "details": {"error": str(e)}
            })
            print(f"  ❌ Cleanup mechanisms: ERROR ({e})")
    
    async def test_5_health_monitoring(self):
        """Test enhanced health monitoring."""
        print("\n🧪 Testing enhanced health monitoring...")
        
        try:
            # Test overall health
            health_response = await self.client.get(f"{API_BASE_URL}/health")
            
            if health_response.status_code == 200:
                health_data = health_response.json()
                
                # Test individual service health
                services = health_data.get('services', {})
                service_tests = []
                
                for service_name in services.keys():
                    service_response = await self.client.get(
                        f"{API_BASE_URL}/health/services/{service_name}"
                    )
                    
                    if service_response.status_code == 200:
                        service_data = service_response.json()
                        service_tests.append({
                            "service": service_name,
                            "status": service_data['status'],
                            "error_count": service_data['error_count']
                        })
                
                # Test metrics
                metrics_response = await self.client.get(f"{API_BASE_URL}/metrics")
                
                if metrics_response.status_code == 200:
                    metrics_data = metrics_response.json()
                    
                    self.test_results.append({
                        "test": "health_monitoring",
                        "status": "PASS",
                        "details": {
                            "overall_status": health_data['status'],
                            "services_count": len(services),
                            "service_tests": service_tests,
                            "total_requests": metrics_data.get('total_requests', 0),
                            "success_rate": metrics_data.get('success_rate', 0),
                            "uptime": metrics_data.get('uptime', 0)
                        }
                    })
                    
                    print(f"  ✅ Health monitoring: PASS")
                    print(f"    🏥 Overall status: {health_data['status']}")
                    print(f"    📊 Services monitored: {len(services)}")
                    print(f"    📈 Success rate: {metrics_data.get('success_rate', 0):.2%}")
                else:
                    self.test_results.append({
                        "test": "health_monitoring",
                        "status": "ERROR",
                        "details": {"error": f"Metrics failed: HTTP {metrics_response.status_code}"}
                    })
                    print(f"  ❌ Health monitoring: ERROR (Metrics failed)")
            else:
                self.test_results.append({
                    "test": "health_monitoring",
                    "status": "ERROR",
                    "details": {"error": f"Health check failed: HTTP {health_response.status_code}"}
                })
                print(f"  ❌ Health monitoring: ERROR")
                
        except Exception as e:
            self.test_results.append({
                "test": "health_monitoring",
                "status": "ERROR",
                "details": {"error": str(e)}
            })
            print(f"  ❌ Health monitoring: ERROR ({e})")
    
    async def run_all_tests(self):
        """Run all Phase 6.2 tests."""
        print("🚀 Starting Phase 6.2 Advanced API Features Tests")
        print("=" * 60)
        
        await self.setup()
        
        # Run tests
        await self.test_1_file_validation()
        await self.test_2_enhanced_upload_with_progress()
        await self.test_3_streaming_connection_management()
        await self.test_4_cleanup_mechanisms()
        await self.test_5_health_monitoring()
        
        # Generate report
        await self.generate_report()
        
        # Cleanup
        await self.client.aclose()
    
    async def generate_report(self):
        """Generate test report."""
        print("\n" + "=" * 60)
        print("📊 Phase 6.2 Advanced API Features Test Report")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        error_tests = len([r for r in self.test_results if r['status'] == 'ERROR'])
        
        print(f"📈 Test Summary:")
        print(f"   Total Tests: {total_tests}")
        print(f"   ✅ Passed: {passed_tests}")
        print(f"   ❌ Failed: {failed_tests}")
        print(f"   ⚠️ Errors: {error_tests}")
        print(f"   📊 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print(f"\n📋 Detailed Results:")
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌" if result['status'] == 'FAIL' else "⚠️"
            print(f"   {status_icon} {result['test']}: {result['status']}")
            if result['details']:
                for key, value in result['details'].items():
                    if isinstance(value, (dict, list)):
                        print(f"      {key}: {json.dumps(value, indent=6)}")
                    else:
                        print(f"      {key}: {value}")
        
        # Save detailed report
        report_file = Path("scripts/phase_6_2_advanced_features_report.json")
        report_data = {
            "phase": "6.2",
            "title": "Advanced API Features",
            "timestamp": time.time(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "error_tests": error_tests,
                "success_rate": (passed_tests/total_tests)*100
            },
            "results": self.test_results
        }
        
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"\n📄 Detailed report saved to: {report_file}")
        
        # Overall assessment
        if passed_tests == total_tests:
            print(f"\n🎉 Phase 6.2 Advanced API Features: ALL TESTS PASSED!")
            return True
        elif passed_tests >= total_tests * 0.8:
            print(f"\n⚠️ Phase 6.2 Advanced API Features: MOSTLY PASSED ({passed_tests}/{total_tests})")
            return True
        else:
            print(f"\n❌ Phase 6.2 Advanced API Features: SIGNIFICANT ISSUES DETECTED")
            return False


async def main():
    """Main test runner."""
    tester = TestPhase62AdvancedFeatures()
    success = await tester.run_all_tests()
    
    if success:
        print(f"\n✅ Phase 6.2 Advanced API Features implementation is ready!")
    else:
        print(f"\n❌ Phase 6.2 Advanced API Features needs attention.")
    
    return success


if __name__ == "__main__":
    asyncio.run(main())
