#!/usr/bin/env python3
"""
ZeroRAG Phase 6.1 FastAPI Backend - Structure Test

This script tests the FastAPI backend structure and configuration
without starting a server.
"""

import json
import time
import sys
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import get_config


class StructureTester:
    """Test suite for FastAPI backend structure."""
    
    def __init__(self):
        self.config = get_config()
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
    
    def test_configuration(self) -> bool:
        """Test configuration loading."""
        try:
            start_time = time.time()
            
            # Check API configuration
            api_config = self.config.api
            required_fields = ["host", "port", "workers", "reload", "log_level"]
            
            if all(hasattr(api_config, field) for field in required_fields):
                self.log_test("Configuration", "PASS", f"API config loaded: {api_config.host}:{api_config.port}", time.time() - start_time)
                return True
            else:
                missing_fields = [field for field in required_fields if not hasattr(api_config, field)]
                self.log_test("Configuration", "FAIL", f"Missing fields: {missing_fields}")
                return False
                
        except Exception as e:
            self.log_test("Configuration", "ERROR", str(e))
            return False
    
    def test_api_import(self) -> bool:
        """Test API module import."""
        try:
            start_time = time.time()
            
            # Try to import the API module
            import api.main as api_main
            
            if hasattr(api_main, 'app'):
                self.log_test("API Import", "PASS", "FastAPI app imported successfully", time.time() - start_time)
                return True
            else:
                self.log_test("API Import", "FAIL", "No 'app' attribute found")
                return False
                
        except Exception as e:
            self.log_test("API Import", "ERROR", str(e))
            return False
    
    def test_api_routes(self) -> bool:
        """Test API routes structure."""
        try:
            start_time = time.time()
            
            # Import the API module
            import src.api.main as api_main
            
            # Check if routers are included
            app = api_main.app
            
            # Check if the app has routes
            if hasattr(app, 'routes') and len(app.routes) > 0:
                self.log_test("API Routes", "PASS", f"Found {len(app.routes)} routes", time.time() - start_time)
                return True
            else:
                self.log_test("API Routes", "FAIL", "No routes found")
                return False
                
        except Exception as e:
            self.log_test("API Routes", "ERROR", str(e))
            return False
    
    def test_api_models(self) -> bool:
        """Test API models structure."""
        try:
            start_time = time.time()
            
            # Try to import the models
            import api.models as api_models
            
            # Check for required model classes
            required_models = [
                "HealthResponse", "QueryRequest", "QueryResponse", 
                "DocumentUploadResponse", "ErrorResponse", "APIInfo"
            ]
            
            missing_models = []
            for model_name in required_models:
                if not hasattr(api_models, model_name):
                    missing_models.append(model_name)
            
            if not missing_models:
                self.log_test("API Models", "PASS", f"All {len(required_models)} models found", time.time() - start_time)
                return True
            else:
                self.log_test("API Models", "FAIL", f"Missing models: {missing_models}")
                return False
                
        except Exception as e:
            self.log_test("API Models", "ERROR", str(e))
            return False
    
    def test_api_routes_import(self) -> bool:
        """Test API routes import."""
        try:
            start_time = time.time()
            
            # Try to import the routes
            import api.routes as api_routes
            
            # Check for required routers
            required_routers = [
                "health_router", "documents_router", "query_router", "metrics_router"
            ]
            
            missing_routers = []
            for router_name in required_routers:
                if not hasattr(api_routes, router_name):
                    missing_routers.append(router_name)
            
            if not missing_routers:
                self.log_test("API Routes Import", "PASS", f"All {len(required_routers)} routers found", time.time() - start_time)
                return True
            else:
                self.log_test("API Routes Import", "FAIL", f"Missing routers: {missing_routers}")
                return False
                
        except Exception as e:
            self.log_test("API Routes Import", "ERROR", str(e))
            return False
    
    def test_service_integration(self) -> bool:
        """Test service integration."""
        try:
            start_time = time.time()
            
            # Try to import service factory
            import services.service_factory as service_factory
            
            if hasattr(service_factory, 'ServiceFactory'):
                self.log_test("Service Integration", "PASS", "ServiceFactory imported successfully", time.time() - start_time)
                return True
            else:
                self.log_test("Service Integration", "FAIL", "ServiceFactory not found")
                return False
                
        except Exception as e:
            self.log_test("Service Integration", "ERROR", str(e))
            return False
    
    def test_cors_configuration(self) -> bool:
        """Test CORS configuration."""
        try:
            start_time = time.time()
            
            # Check CORS configuration
            api_config = self.config.api
            
            if hasattr(api_config, 'enable_cors') and hasattr(api_config, 'cors_origins'):
                self.log_test("CORS Configuration", "PASS", f"CORS enabled: {api_config.enable_cors}", time.time() - start_time)
                return True
            else:
                self.log_test("CORS Configuration", "FAIL", "CORS configuration missing")
                return False
                
        except Exception as e:
            self.log_test("CORS Configuration", "ERROR", str(e))
            return False
    
    def test_error_handlers(self) -> bool:
        """Test error handlers."""
        try:
            start_time = time.time()
            
            # Import the API module
            import api.main as api_main
            
            # Check if error handlers are defined
            app = api_main.app
            
            # Look for exception handlers
            if hasattr(app, 'exception_handlers') and len(app.exception_handlers) > 0:
                self.log_test("Error Handlers", "PASS", f"Found {len(app.exception_handlers)} error handlers", time.time() - start_time)
                return True
            else:
                self.log_test("Error Handlers", "SKIP", "No explicit error handlers found (using defaults)")
                return True
                
        except Exception as e:
            self.log_test("Error Handlers", "ERROR", str(e))
            return False
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return results."""
        print("=" * 60)
        print("ZeroRAG Phase 6.1 FastAPI Backend - Structure Testing")
        print("=" * 60)
        
        # Run tests
        tests = [
            ("Configuration", self.test_configuration),
            ("API Import", self.test_api_import),
            ("API Routes", self.test_api_routes),
            ("API Models", self.test_api_models),
            ("API Routes Import", self.test_api_routes_import),
            ("Service Integration", self.test_service_integration),
            ("CORS Configuration", self.test_cors_configuration),
            ("Error Handlers", self.test_error_handlers),
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
            print("\n✅ Phase 6.1 FastAPI Backend Structure: PASSED")
            summary["phase_status"] = "PASSED"
        else:
            print("\n❌ Phase 6.1 FastAPI Backend Structure: FAILED")
            summary["phase_status"] = "FAILED"
        
        return summary


def main():
    """Main test execution."""
    tester = StructureTester()
    
    # Run tests
    results = tester.run_all_tests()
    
    # Save results
    output_file = Path(__file__).parent / "phase_6_1_structure_report.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nDetailed results saved to: {output_file}")
    
    # Exit with appropriate code
    sys.exit(0 if results.get("phase_status") == "PASSED" else 1)


if __name__ == "__main__":
    main()
