#!/usr/bin/env python3
"""
Test Phase 7.1: Streamlit UI Foundation

This script tests the basic Streamlit UI implementation including:
- UI structure and layout
- Document upload interface
- File validation
- Upload progress tracking
- Basic chat interface

Phase 7.1 Implementation Test:
- Basic Streamlit application structure
- Page configuration and layout
- Document upload interface with validation
- Upload progress and status display
"""

import sys
import os
import time
import requests
import json
from pathlib import Path
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_api_availability() -> bool:
    """Test if the API is available."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def test_streamlit_import() -> bool:
    """Test if Streamlit can be imported."""
    try:
        import streamlit
        return True
    except ImportError:
        return False

def test_ui_module_import() -> bool:
    """Test if the UI module can be imported."""
    try:
        from src.ui import streamlit_app
        return True
    except ImportError as e:
        print(f"❌ UI module import failed: {e}")
        return False

def test_file_upload_endpoints() -> Dict[str, Any]:
    """Test file upload related endpoints."""
    results = {}
    
    # Test document validation endpoint
    try:
        # Create a simple test file
        test_content = "This is a test document for validation."
        files = {"file": ("test.txt", test_content, "text/plain")}
        
        response = requests.post(
            "http://localhost:8000/documents/validate",
            files=files,
            timeout=10
        )
        
        if response.status_code == 200:
            results["validation"] = "✅ Pass"
        else:
            results["validation"] = f"❌ Fail (Status: {response.status_code})"
    except requests.RequestException as e:
        results["validation"] = f"❌ Fail (Error: {e})"
    
    # Test document upload endpoint
    try:
        files = {"file": ("test_upload.txt", test_content, "text/plain")}
        
        response = requests.post(
            "http://localhost:8000/documents/upload",
            files=files,
            timeout=30
        )
        
        if response.status_code == 200:
            upload_data = response.json()
            document_id = upload_data.get("document_id")
            results["upload"] = f"✅ Pass (ID: {document_id})"
            
            # Test progress endpoint if document_id is available
            if document_id:
                try:
                    progress_response = requests.get(
                        f"http://localhost:8000/documents/upload/{document_id}/progress",
                        timeout=5
                    )
                    if progress_response.status_code == 200:
                        results["progress"] = "✅ Pass"
                    else:
                        results["progress"] = f"❌ Fail (Status: {progress_response.status_code})"
                except requests.RequestException as e:
                    results["progress"] = f"❌ Fail (Error: {e})"
        else:
            results["upload"] = f"❌ Fail (Status: {response.status_code})"
    except requests.RequestException as e:
        results["upload"] = f"❌ Fail (Error: {e})"
    
    return results

def test_query_endpoint() -> str:
    """Test the query endpoint."""
    try:
        data = {"query": "What is this document about?", "stream": False}
        
        response = requests.post(
            "http://localhost:8000/query",
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            return "✅ Pass"
        else:
            return f"❌ Fail (Status: {response.status_code})"
    except requests.RequestException as e:
        return f"❌ Fail (Error: {e})"

def test_ui_functions() -> Dict[str, Any]:
    """Test UI helper functions."""
    results = {}
    
    try:
        from src.ui.streamlit_app import (
            check_api_health,
            validate_file,
            upload_document,
            get_upload_progress,
            query_rag
        )
        results["import"] = "✅ Pass"
        
        # Test API health check
        health_result = check_api_health()
        results["health_check"] = "✅ Pass" if health_result else "❌ Fail"
        
    except ImportError as e:
        results["import"] = f"❌ Fail (Error: {e})"
    
    return results

def generate_test_report() -> Dict[str, Any]:
    """Generate a comprehensive test report."""
    report = {
        "phase": "7.1",
        "title": "Streamlit UI Foundation",
        "timestamp": time.time(),
        "tests": {}
    }
    
    print("🧪 Testing Phase 7.1: Streamlit UI Foundation")
    print("=" * 50)
    
    # Test 1: API Availability
    print("1. Testing API availability...")
    api_available = test_api_availability()
    report["tests"]["api_availability"] = "✅ Pass" if api_available else "❌ Fail"
    print(f"   Result: {report['tests']['api_availability']}")
    
    # Test 2: Streamlit Import
    print("2. Testing Streamlit import...")
    streamlit_available = test_streamlit_import()
    report["tests"]["streamlit_import"] = "✅ Pass" if streamlit_available else "❌ Fail"
    print(f"   Result: {report['tests']['streamlit_import']}")
    
    # Test 3: UI Module Import
    print("3. Testing UI module import...")
    ui_import_success = test_ui_module_import()
    report["tests"]["ui_module_import"] = "✅ Pass" if ui_import_success else "❌ Fail"
    print(f"   Result: {report['tests']['ui_module_import']}")
    
    # Test 4: UI Functions
    print("4. Testing UI helper functions...")
    ui_function_results = test_ui_functions()
    report["tests"]["ui_functions"] = ui_function_results
    for test_name, result in ui_function_results.items():
        print(f"   {test_name}: {result}")
    
    # Test 5: File Upload Endpoints (only if API is available)
    if api_available:
        print("5. Testing file upload endpoints...")
        upload_results = test_file_upload_endpoints()
        report["tests"]["file_upload_endpoints"] = upload_results
        for endpoint, result in upload_results.items():
            print(f"   {endpoint}: {result}")
    else:
        print("5. Skipping file upload tests (API not available)")
        report["tests"]["file_upload_endpoints"] = "⏭️ Skipped (API not available)"
    
    # Test 6: Query Endpoint (only if API is available)
    if api_available:
        print("6. Testing query endpoint...")
        query_result = test_query_endpoint()
        report["tests"]["query_endpoint"] = query_result
        print(f"   Result: {query_result}")
    else:
        print("6. Skipping query test (API not available)")
        report["tests"]["query_endpoint"] = "⏭️ Skipped (API not available)"
    
    # Calculate overall status
    passed_tests = 0
    total_tests = 0
    
    for test_category, results in report["tests"].items():
        if isinstance(results, dict):
            for test_name, result in results.items():
                total_tests += 1
                if result.startswith("✅"):
                    passed_tests += 1
        else:
            total_tests += 1
            if results.startswith("✅"):
                passed_tests += 1
    
    report["summary"] = {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": total_tests - passed_tests,
        "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0
    }
    
    print("\n" + "=" * 50)
    print("📊 Test Summary")
    print(f"   Total Tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {total_tests - passed_tests}")
    print(f"   Success Rate: {report['summary']['success_rate']:.1f}%")
    
    if report["summary"]["success_rate"] >= 80:
        print("🎉 Phase 7.1 tests PASSED!")
        report["status"] = "PASSED"
    else:
        print("❌ Phase 7.1 tests FAILED!")
        report["status"] = "FAILED"
    
    return report

def save_test_report(report: Dict[str, Any]) -> None:
    """Save the test report to a JSON file."""
    report_file = project_root / "scripts" / "phase_7_1_streamlit_report.json"
    
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Test report saved to: {report_file}")

def main():
    """Run all tests and generate report."""
    try:
        report = generate_test_report()
        save_test_report(report)
        
        # Exit with appropriate code
        if report["status"] == "PASSED":
            sys.exit(0)
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Test execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
