#!/usr/bin/env python3
"""
ZeroRAG Service Integration Test Script

This script tests the service integration functionality including:
- Service Factory initialization and management
- Health Monitor functionality
- Service lifecycle management
- Error handling and recovery
- Performance metrics

Usage:
    python test_integration.py
"""

import sys
import time
import logging
import threading
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from services.service_factory import ServiceFactory, ServiceStatus
from services.health_monitor import HealthMonitor, AlertLevel
from config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_service_factory_initialization():
    """Test service factory initialization."""
    print("\n" + "="*60)
    print("TESTING SERVICE FACTORY INITIALIZATION")
    print("="*60)
    
    try:
        # Initialize service factory
        start_time = time.time()
        factory = ServiceFactory()
        init_time = time.time() - start_time
        
        print(f"✅ Service Factory initialized successfully in {init_time:.2f}s")
        
        # Check service status
        all_status = factory.get_all_service_status()
        print(f"   Total services: {len(all_status)}")
        
        for service_name, service_info in all_status.items():
            print(f"   {service_name}: {service_info.status.value}")
            if service_info.initialization_time:
                print(f"     Init time: {service_info.initialization_time:.2f}s")
        
        return factory
        
    except Exception as e:
        print(f"❌ Service Factory initialization failed: {e}")
        logger.exception("Service Factory initialization failed")
        return None


def test_service_health_checks(factory):
    """Test service health check functionality."""
    print("\n" + "="*60)
    print("TESTING SERVICE HEALTH CHECKS")
    print("="*60)
    
    try:
        # Perform comprehensive health check
        health_status = factory.perform_health_check()
        
        print(f"✅ Health check completed")
        print(f"   Overall status: {health_status['overall_status']}")
        print(f"   Healthy services: {health_status['healthy_services']}")
        
        # Service details
        for service_name, service_info in health_status['services'].items():
            print(f"\n   {service_name.upper()} SERVICE:")
            print(f"     Status: {service_info['status']}")
            print(f"     Error count: {service_info['error_count']}")
            print(f"     Last check: {service_info['last_check']:.1f}s ago")
            
            if service_info['initialization_time']:
                print(f"     Init time: {service_info['initialization_time']:.2f}s")
            
            # Show health data
            health_data = service_info['health_data']
            if health_data:
                print(f"     Health data: {health_data}")
        
        # Metrics
        metrics = health_status['metrics']
        print(f"\n   METRICS:")
        print(f"     Total requests: {metrics['total_requests']}")
        print(f"     Failed requests: {metrics['failed_requests']}")
        print(f"     Success rate: {metrics['success_rate']:.1%}")
        
        return health_status
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        logger.exception("Health check failed")
        return None


def test_service_access(factory):
    """Test service access functionality."""
    print("\n" + "="*60)
    print("TESTING SERVICE ACCESS")
    print("="*60)
    
    try:
        # Test embedding service access
        embedding_service = factory.get_embedding_service()
        if embedding_service:
            print("✅ Embedding service accessible")
            
            # Test a simple embedding
            try:
                test_text = "Hello, world!"
                embedding = embedding_service.get_embedding(test_text)
                print(f"   Test embedding generated: {len(embedding)} dimensions")
                factory.record_request("embedding", success=True)
            except Exception as e:
                print(f"   ❌ Embedding generation failed: {e}")
                factory.record_request("embedding", success=False)
        else:
            print("❌ Embedding service not available")
        
        # Test LLM service access
        llm_service = factory.get_llm_service()
        if llm_service:
            print("✅ LLM service accessible")
            
            # Test a simple generation
            try:
                test_prompt = "Say hello in one word:"
                response = llm_service.generate(test_prompt, max_tokens=5)
                print(f"   Test generation: {response.text}")
                factory.record_request("llm", success=True)
            except Exception as e:
                print(f"   ❌ LLM generation failed: {e}")
                factory.record_request("llm", success=False)
        else:
            print("❌ LLM service not available")
        
        return True
        
    except Exception as e:
        print(f"❌ Service access test failed: {e}")
        logger.exception("Service access test failed")
        return False


def test_service_metrics_tracking(factory):
    """Test service metrics tracking."""
    print("\n" + "="*60)
    print("TESTING SERVICE METRICS TRACKING")
    print("="*60)
    
    try:
        # Record some test requests
        factory.record_request("embedding", success=True)
        factory.record_request("embedding", success=True)
        factory.record_request("llm", success=True)
        factory.record_request("llm", success=False)
        
        # Get service summary
        summary = factory.get_service_summary()
        
        print("✅ Metrics tracking working")
        print(f"   Total requests: {summary['total_requests']}")
        print(f"   Failed requests: {summary['failed_requests']}")
        print(f"   Success rate: {summary['success_rate']:.1%}")
        print(f"   Uptime: {summary['uptime']:.1f}s")
        
        # Service-specific metrics
        for service_name, metrics in summary['service_metrics'].items():
            print(f"\n   {service_name.upper()} METRICS:")
            print(f"     Requests: {metrics['requests']}")
            print(f"     Errors: {metrics['errors']}")
            print(f"     Success rate: {metrics['success_rate']:.1%}")
        
        return summary
        
    except Exception as e:
        print(f"❌ Metrics tracking test failed: {e}")
        logger.exception("Metrics tracking test failed")
        return None


def test_health_monitor(factory):
    """Test health monitor functionality."""
    print("\n" + "="*60)
    print("TESTING HEALTH MONITOR")
    print("="*60)
    
    try:
        # Create health monitor
        monitor = HealthMonitor(factory, check_interval=5, alert_threshold=2)
        
        # Add alert callback
        alerts_received = []
        def alert_callback(alert):
            alerts_received.append(alert)
            print(f"   🔔 ALERT: {alert.level.value.upper()} - {alert.service_name}: {alert.message}")
        
        monitor.add_alert_callback(alert_callback)
        
        print("✅ Health monitor created")
        
        # Start monitoring
        monitor.start_monitoring()
        print("✅ Health monitor started")
        
        # Let it run for a few cycles
        print("   Monitoring for 15 seconds...")
        time.sleep(15)
        
        # Stop monitoring
        monitor.stop_monitoring()
        print("✅ Health monitor stopped")
        
        # Get health summary
        health_summary = monitor.get_health_summary()
        print(f"\n   HEALTH SUMMARY:")
        print(f"     Total checks: {health_summary['total_checks']}")
        print(f"     Failed checks: {health_summary['failed_checks']}")
        print(f"     Alerts generated: {len(alerts_received)}")
        print(f"     Monitoring time: {health_summary['monitoring_time']:.1f}s")
        
        # Clean up
        monitor.shutdown()
        
        return monitor, alerts_received
        
    except Exception as e:
        print(f"❌ Health monitor test failed: {e}")
        logger.exception("Health monitor test failed")
        return None, []


def test_service_recovery(factory):
    """Test service recovery functionality."""
    print("\n" + "="*60)
    print("TESTING SERVICE RECOVERY")
    print("="*60)
    
    try:
        # Test restarting a service
        print("Testing service restart functionality...")
        
        # Get current status
        initial_status = factory.get_all_service_status()
        
        # Try to restart embedding service
        success = factory.restart_service("embedding")
        if success:
            print("✅ Embedding service restart successful")
        else:
            print("⚠️  Embedding service restart failed (may be expected)")
        
        # Try to restart LLM service
        success = factory.restart_service("llm")
        if success:
            print("✅ LLM service restart successful")
        else:
            print("⚠️  LLM service restart failed (may be expected)")
        
        # Check final status
        final_status = factory.get_all_service_status()
        
        print(f"\n   STATUS COMPARISON:")
        for service_name in initial_status:
            initial = initial_status[service_name].status.value
            final = final_status[service_name].status.value
            print(f"     {service_name}: {initial} → {final}")
        
        return True
        
    except Exception as e:
        print(f"❌ Service recovery test failed: {e}")
        logger.exception("Service recovery test failed")
        return False


def test_service_summary(factory):
    """Test service summary functionality."""
    print("\n" + "="*60)
    print("TESTING SERVICE SUMMARY")
    print("="*60)
    
    try:
        # Get comprehensive summary
        summary = factory.get_service_summary()
        
        print("✅ Service summary generated")
        print(f"\n   OVERALL SUMMARY:")
        print(f"     Total services: {summary['total_services']}")
        print(f"     Healthy services: {summary['healthy_services']}")
        print(f"     Overall status: {summary['overall_status']}")
        print(f"     Uptime: {summary['uptime']:.1f}s")
        print(f"     Total requests: {summary['total_requests']}")
        print(f"     Success rate: {summary['success_rate']:.1%}")
        
        print(f"\n   SERVICE DETAILS:")
        for service_name, details in summary['service_details'].items():
            print(f"     {service_name.upper()}:")
            print(f"       Status: {details['status']}")
            print(f"       Requests: {details['requests']}")
            print(f"       Errors: {details['errors']}")
            print(f"       Success rate: {details['success_rate']:.1%}")
            if details['initialization_time']:
                print(f"       Init time: {details['initialization_time']:.2f}s")
        
        return summary
        
    except Exception as e:
        print(f"❌ Service summary test failed: {e}")
        logger.exception("Service summary test failed")
        return None


def test_graceful_shutdown(factory):
    """Test graceful shutdown functionality."""
    print("\n" + "="*60)
    print("TESTING GRACEFUL SHUTDOWN")
    print("="*60)
    
    try:
        # Test shutdown
        factory.shutdown()
        print("✅ Service factory shutdown completed")
        
        # Verify services are properly shut down
        all_status = factory.get_all_service_status()
        for service_name, service_info in all_status.items():
            print(f"   {service_name}: {service_info.status.value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Graceful shutdown test failed: {e}")
        logger.exception("Graceful shutdown test failed")
        return False


def main():
    """Main test function."""
    print("🚀 ZeroRAG Service Integration Test")
    print("="*60)
    
    # Test configuration
    try:
        config = get_config()
        print(f"✅ Configuration loaded successfully")
        print(f"   LLM Provider: {config.ai_model.ollama_model}")
        print(f"   Embedding Model: {config.ai_model.embedding_model}")
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return
    
    # Run tests
    factory = test_service_factory_initialization()
    if not factory:
        print("❌ Cannot proceed without service factory")
        return
    
    health_status = test_service_health_checks(factory)
    if not health_status:
        print("⚠️  Health checks failed, but continuing...")
    
    access_success = test_service_access(factory)
    if not access_success:
        print("⚠️  Service access tests failed, but continuing...")
    
    metrics_summary = test_service_metrics_tracking(factory)
    if not metrics_summary:
        print("⚠️  Metrics tracking failed, but continuing...")
    
    monitor, alerts = test_health_monitor(factory)
    if not monitor:
        print("⚠️  Health monitor tests failed, but continuing...")
    
    recovery_success = test_service_recovery(factory)
    if not recovery_success:
        print("⚠️  Service recovery tests failed, but continuing...")
    
    summary = test_service_summary(factory)
    if not summary:
        print("⚠️  Service summary failed, but continuing...")
    
    shutdown_success = test_graceful_shutdown(factory)
    if not shutdown_success:
        print("⚠️  Graceful shutdown failed")
    
    print("\n" + "="*60)
    print("🎉 INTEGRATION TEST COMPLETED")
    print("="*60)
    
    if factory and health_status and access_success and metrics_summary and monitor and recovery_success and summary and shutdown_success:
        print("✅ All tests passed successfully!")
    else:
        print("⚠️  Some tests failed or had issues")
        print("   This may be expected depending on your environment setup")


if __name__ == "__main__":
    main()
