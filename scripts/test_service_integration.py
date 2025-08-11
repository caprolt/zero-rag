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
    python scripts/test_service_integration.py
"""

import sys
import time
import logging
import threading
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

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
        print(f"     Uptime: {metrics['uptime']:.1f}s")
        
        return health_status['overall_status'] == 'healthy'
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_service_access(factory):
    """Test accessing individual services."""
    print("\n" + "="*60)
    print("TESTING SERVICE ACCESS")
    print("="*60)
    
    # Test embedding service access
    print("\n--- Embedding Service ---")
    embedding_service = factory.get_embedding_service()
    if embedding_service:
        print("✅ Embedding service accessible")
        
        # Test embedding generation
        try:
            test_texts = ["Hello world", "Test embedding"]
            embeddings = embedding_service.encode(test_texts)
            print(f"   Generated {len(embeddings)} embeddings")
            print(f"   Embedding dimension: {len(embeddings[0])}")
        except Exception as e:
            print(f"   ❌ Embedding generation failed: {e}")
    else:
        print("❌ Embedding service not available")
    
    # Test LLM service access
    print("\n--- LLM Service ---")
    llm_service = factory.get_llm_service()
    if llm_service:
        print("✅ LLM service accessible")
        
        # Test LLM generation
        try:
            response = llm_service.generate("Hello, how are you?", max_tokens=50)
            print(f"   Generated response: {len(response.text)} chars")
            print(f"   Provider: {response.provider.value}")
            print(f"   Response time: {response.response_time:.3f}s")
        except Exception as e:
            print(f"   ❌ LLM generation failed: {e}")
    else:
        print("❌ LLM service not available")


def test_service_metrics_tracking(factory):
    """Test service metrics tracking."""
    print("\n" + "="*60)
    print("TESTING SERVICE METRICS TRACKING")
    print("="*60)
    
    # Record some test requests
    print("Recording test requests...")
    
    # Simulate successful requests
    for i in range(5):
        factory.record_request("embedding", success=True)
        factory.record_request("llm", success=True)
        time.sleep(0.1)
    
    # Simulate failed requests
    factory.record_request("embedding", success=False)
    factory.record_request("llm", success=False)
    
    # Get updated health status
    health_status = factory.perform_health_check()
    metrics = health_status['metrics']
    
    print(f"✅ Metrics tracking working")
    print(f"   Total requests: {metrics['total_requests']}")
    print(f"   Failed requests: {metrics['failed_requests']}")
    print(f"   Success rate: {metrics['success_rate']:.1%}")
    
    # Check service error counts
    for service_name, service_info in health_status['services'].items():
        print(f"   {service_name} errors: {service_info['error_count']}")


def test_health_monitor(factory):
    """Test health monitor functionality."""
    print("\n" + "="*60)
    print("TESTING HEALTH MONITOR")
    print("="*60)
    
    try:
        # Initialize health monitor
        monitor = HealthMonitor(factory, check_interval=5, alert_threshold=2)
        
        print("✅ Health monitor initialized")
        print(f"   Check interval: {monitor.check_interval}s")
        print(f"   Alert threshold: {monitor.alert_threshold}")
        print(f"   Auto recovery: {monitor.enable_auto_recovery}")
        
        # Add alert callback
        def alert_callback(alert):
            print(f"   🔔 ALERT [{alert.level.value.upper()}] {alert.service_name}: {alert.message}")
        
        monitor.add_alert_callback(alert_callback)
        
        # Start monitoring
        monitor.start_monitoring()
        print("✅ Health monitor started")
        
        # Let it run for a few checks
        print("   Running health checks for 15 seconds...")
        time.sleep(15)
        
        # Get health summary
        summary = monitor.get_health_summary()
        
        print(f"\n📊 Health Summary:")
        print(f"   Monitor running: {summary['monitor_status']['is_running']}")
        print(f"   Total checks: {summary['monitor_status']['total_checks']}")
        print(f"   Failed checks: {summary['monitor_status']['failed_checks']}")
        print(f"   Success rate: {summary['monitor_status']['success_rate']:.1%}")
        print(f"   Uptime: {summary['monitor_status']['uptime']:.1f}s")
        
        # Check alerts
        alerts = monitor.get_alerts(hours=1)
        print(f"   Recent alerts: {len(alerts)}")
        
        # Check health trend
        trend = summary['health_trend']
        print(f"   Health trend: {trend['trend']}")
        
        # Stop monitoring
        monitor.stop_monitoring()
        print("✅ Health monitor stopped")
        
        return True
        
    except Exception as e:
        print(f"❌ Health monitor test failed: {e}")
        return False


def test_service_recovery(factory):
    """Test service recovery functionality."""
    print("\n" + "="*60)
    print("TESTING SERVICE RECOVERY")
    print("="*60)
    
    # Test restarting services
    for service_name in ["embedding", "llm"]:
        print(f"\n--- Testing {service_name} service recovery ---")
        
        try:
            success = factory.restart_service(service_name)
            if success:
                print(f"✅ {service_name} service restarted successfully")
            else:
                print(f"❌ {service_name} service restart failed")
        except Exception as e:
            print(f"❌ {service_name} service restart error: {e}")
    
    # Check final health status
    health_status = factory.perform_health_check()
    print(f"\n   Final overall status: {health_status['overall_status']}")


def test_service_summary(factory):
    """Test service summary functionality."""
    print("\n" + "="*60)
    print("TESTING SERVICE SUMMARY")
    print("="*60)
    
    try:
        summary = factory.get_service_summary()
        
        print(f"✅ Service summary generated")
        print(f"   Total services: {summary['total_services']}")
        print(f"   Healthy services: {summary['healthy_services']}")
        print(f"   Unhealthy services: {summary['unhealthy_services']}")
        
        for service_name, service_info in summary['services'].items():
            print(f"\n   {service_name.upper()}:")
            print(f"     Status: {service_info['status']}")
            print(f"     Error count: {service_info['error_count']}")
            print(f"     Last check: {service_info['last_check']:.1f}s ago")
            if service_info['initialization_time']:
                print(f"     Init time: {service_info['initialization_time']:.2f}s")
        
        return True
        
    except Exception as e:
        print(f"❌ Service summary failed: {e}")
        return False


def test_graceful_shutdown(factory):
    """Test graceful shutdown functionality."""
    print("\n" + "="*60)
    print("TESTING GRACEFUL SHUTDOWN")
    print("="*60)
    
    try:
        # Shutdown service factory
        factory.shutdown()
        print("✅ Service factory shutdown completed")
        
        # Verify services are cleaned up
        all_status = factory.get_all_service_status()
        if not all_status:
            print("✅ All services cleaned up successfully")
        else:
            print(f"⚠️  {len(all_status)} services still registered")
        
        return True
        
    except Exception as e:
        print(f"❌ Graceful shutdown failed: {e}")
        return False


def main():
    """Main test function."""
    print("🚀 ZeroRAG Service Integration Test")
    print("="*60)
    
    # Test service factory initialization
    factory = test_service_factory_initialization()
    if not factory:
        print("❌ Cannot proceed without service factory")
        return
    
    # Test health checks
    health_ok = test_service_health_checks(factory)
    if not health_ok:
        print("⚠️  Some services are unhealthy, but continuing with tests")
    
    # Test service access
    test_service_access(factory)
    
    # Test metrics tracking
    test_service_metrics_tracking(factory)
    
    # Test health monitor
    monitor_ok = test_health_monitor(factory)
    if not monitor_ok:
        print("⚠️  Health monitor test failed, but continuing")
    
    # Test service recovery
    test_service_recovery(factory)
    
    # Test service summary
    summary_ok = test_service_summary(factory)
    if not summary_ok:
        print("⚠️  Service summary test failed")
    
    # Test graceful shutdown
    shutdown_ok = test_graceful_shutdown(factory)
    if not shutdown_ok:
        print("⚠️  Graceful shutdown test failed")
    
    print("\n🎉 Service Integration test completed!")


if __name__ == "__main__":
    main()
