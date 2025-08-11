"""
ZeroRAG Health Monitor

This module provides continuous health monitoring for all AI services
with configurable intervals, alerting, and performance tracking.
"""

import logging
import threading
import time
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from .service_factory import ServiceFactory, ServiceStatus

logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    """Alert level enumeration."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class HealthAlert:
    """Health alert container."""
    level: AlertLevel
    service_name: str
    message: str
    timestamp: float
    details: Dict[str, Any]


class HealthMonitor:
    """
    Continuous health monitoring for ZeroRAG services.
    
    Features:
    - Continuous health monitoring with configurable intervals
    - Alert generation and management
    - Performance trend analysis
    - Automatic service recovery attempts
    - Health history tracking
    """
    
    def __init__(self, 
                 service_factory: ServiceFactory,
                 check_interval: int = 30,
                 alert_threshold: int = 3,
                 enable_auto_recovery: bool = True):
        """Initialize the health monitor."""
        self.service_factory = service_factory
        self.check_interval = check_interval
        self.alert_threshold = alert_threshold
        self.enable_auto_recovery = enable_auto_recovery
        
        # Monitoring state
        self.is_running = False
        self.monitor_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # Health tracking
        self.health_history: List[Dict[str, Any]] = []
        self.alerts: List[HealthAlert] = []
        self.service_failure_counts: Dict[str, int] = {}
        
        # Alert callbacks
        self.alert_callbacks: List[Callable[[HealthAlert], None]] = []
        
        # Performance tracking
        self.start_time = time.time()
        self.total_checks = 0
        self.failed_checks = 0
        
        logger.info(f"Health monitor initialized with {check_interval}s interval")
    
    def start_monitoring(self):
        """Start continuous health monitoring."""
        if self.is_running:
            logger.warning("Health monitor is already running")
            return
        
        logger.info("Starting health monitor...")
        self.is_running = True
        self.stop_event.clear()
        
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            daemon=True,
            name="HealthMonitor"
        )
        self.monitor_thread.start()
        
        logger.info("Health monitor started successfully")
    
    def stop_monitoring(self):
        """Stop continuous health monitoring."""
        if not self.is_running:
            logger.warning("Health monitor is not running")
            return
        
        logger.info("Stopping health monitor...")
        self.is_running = False
        self.stop_event.set()
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        logger.info("Health monitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        logger.info("Health monitor loop started")
        
        while self.is_running and not self.stop_event.is_set():
            try:
                self._perform_health_check()
                self._process_alerts()
                
                # Wait for next check or stop signal
                self.stop_event.wait(self.check_interval)
                
            except Exception as e:
                logger.error(f"Error in health monitor loop: {e}")
                self.failed_checks += 1
                time.sleep(1)  # Brief pause before retry
        
        logger.info("Health monitor loop ended")
    
    def _perform_health_check(self):
        """Perform a health check and record results."""
        self.total_checks += 1
        
        try:
            # Get health status from service factory
            health_status = self.service_factory.perform_health_check()
            
            # Record in history
            health_record = {
                "timestamp": time.time(),
                "overall_status": health_status["overall_status"],
                "services": health_status["services"],
                "metrics": health_status["metrics"],
                "healthy_services": health_status["healthy_services"]
            }
            
            self.health_history.append(health_record)
            
            # Keep only last 1000 records
            if len(self.health_history) > 1000:
                self.health_history = self.health_history[-1000:]
            
            # Check for service issues
            self._check_service_health(health_status)
            
            logger.debug(f"Health check completed: {health_status['overall_status']}")
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            self.failed_checks += 1
    
    def _check_service_health(self, health_status: Dict[str, Any]):
        """Check individual service health and generate alerts."""
        for service_name, service_info in health_status["services"].items():
            status = service_info["status"]
            
            if status == "healthy":
                # Reset failure count if service is healthy
                self.service_failure_counts[service_name] = 0
                
            elif status in ["unhealthy", "error"]:
                # Increment failure count
                self.service_failure_counts[service_name] = (
                    self.service_failure_counts.get(service_name, 0) + 1
                )
                
                failure_count = self.service_failure_counts[service_name]
                
                # Generate alert based on failure count
                if failure_count == 1:
                    self._create_alert(
                        AlertLevel.WARNING,
                        service_name,
                        f"Service {service_name} is {status}",
                        service_info
                    )
                
                elif failure_count >= self.alert_threshold:
                    self._create_alert(
                        AlertLevel.ERROR,
                        service_name,
                        f"Service {service_name} has been {status} for {failure_count} checks",
                        service_info
                    )
                    
                    # Attempt auto-recovery
                    if self.enable_auto_recovery:
                        self._attempt_service_recovery(service_name)
    
    def _create_alert(self, level: AlertLevel, service_name: str, message: str, details: Dict[str, Any]):
        """Create and store a health alert."""
        alert = HealthAlert(
            level=level,
            service_name=service_name,
            message=message,
            timestamp=time.time(),
            details=details
        )
        
        self.alerts.append(alert)
        
        # Keep only last 100 alerts
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
        
        # Log alert
        log_level = {
            AlertLevel.INFO: logging.INFO,
            AlertLevel.WARNING: logging.WARNING,
            AlertLevel.ERROR: logging.ERROR,
            AlertLevel.CRITICAL: logging.CRITICAL
        }[level]
        
        logger.log(log_level, f"Health Alert [{level.value.upper()}] {service_name}: {message}")
        
        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
    
    def _attempt_service_recovery(self, service_name: str):
        """Attempt to recover a failed service."""
        logger.info(f"Attempting to recover service: {service_name}")
        
        try:
            success = self.service_factory.restart_service(service_name)
            
            if success:
                self._create_alert(
                    AlertLevel.INFO,
                    service_name,
                    f"Service {service_name} recovered successfully",
                    {"recovery_attempt": True}
                )
                # Reset failure count
                self.service_failure_counts[service_name] = 0
            else:
                self._create_alert(
                    AlertLevel.CRITICAL,
                    service_name,
                    f"Service {service_name} recovery failed",
                    {"recovery_attempt": False}
                )
                
        except Exception as e:
            logger.error(f"Service recovery failed: {e}")
            self._create_alert(
                AlertLevel.CRITICAL,
                service_name,
                f"Service {service_name} recovery error: {e}",
                {"recovery_error": str(e)}
            )
    
    def _process_alerts(self):
        """Process and clean up old alerts."""
        current_time = time.time()
        cutoff_time = current_time - (24 * 60 * 60)  # 24 hours
        
        # Remove old alerts
        self.alerts = [
            alert for alert in self.alerts
            if alert.timestamp > cutoff_time
        ]
    
    def add_alert_callback(self, callback: Callable[[HealthAlert], None]):
        """Add an alert callback function."""
        self.alert_callbacks.append(callback)
        logger.info("Alert callback added")
    
    def remove_alert_callback(self, callback: Callable[[HealthAlert], None]):
        """Remove an alert callback function."""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)
            logger.info("Alert callback removed")
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get a comprehensive health summary."""
        current_time = time.time()
        
        # Calculate uptime
        uptime = current_time - self.start_time
        
        # Calculate success rate
        success_rate = (
            (self.total_checks - self.failed_checks) / self.total_checks 
            if self.total_checks > 0 else 1.0
        )
        
        # Get current health status
        current_health = self.service_factory.perform_health_check()
        
        # Get recent alerts
        recent_alerts = [
            {
                "level": alert.level.value,
                "service": alert.service_name,
                "message": alert.message,
                "timestamp": alert.timestamp
            }
            for alert in self.alerts[-10:]  # Last 10 alerts
        ]
        
        # Get health trends
        health_trend = self._calculate_health_trend()
        
        return {
            "monitor_status": {
                "is_running": self.is_running,
                "uptime": uptime,
                "total_checks": self.total_checks,
                "failed_checks": self.failed_checks,
                "success_rate": success_rate,
                "check_interval": self.check_interval
            },
            "current_health": current_health,
            "service_failures": self.service_failure_counts,
            "recent_alerts": recent_alerts,
            "health_trend": health_trend,
            "timestamp": current_time
        }
    
    def _calculate_health_trend(self) -> Dict[str, Any]:
        """Calculate health trends over time."""
        if len(self.health_history) < 2:
            return {"trend": "insufficient_data"}
        
        # Get last 10 health checks
        recent_checks = self.health_history[-10:]
        
        # Count healthy vs unhealthy checks
        healthy_count = sum(
            1 for check in recent_checks
            if check["overall_status"] == "healthy"
        )
        
        unhealthy_count = len(recent_checks) - healthy_count
        
        # Determine trend
        if healthy_count == len(recent_checks):
            trend = "stable_healthy"
        elif unhealthy_count == len(recent_checks):
            trend = "stable_unhealthy"
        elif healthy_count > unhealthy_count:
            trend = "improving"
        else:
            trend = "declining"
        
        return {
            "trend": trend,
            "healthy_checks": healthy_count,
            "unhealthy_checks": unhealthy_count,
            "total_checks": len(recent_checks)
        }
    
    def get_alerts(self, 
                   level: Optional[AlertLevel] = None,
                   service_name: Optional[str] = None,
                   hours: int = 24) -> List[HealthAlert]:
        """Get filtered alerts."""
        current_time = time.time()
        cutoff_time = current_time - (hours * 60 * 60)
        
        filtered_alerts = [
            alert for alert in self.alerts
            if alert.timestamp >= cutoff_time
        ]
        
        if level:
            filtered_alerts = [
                alert for alert in filtered_alerts
                if alert.level == level
            ]
        
        if service_name:
            filtered_alerts = [
                alert for alert in filtered_alerts
                if alert.service_name == service_name
            ]
        
        return filtered_alerts
    
    def get_health_history(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get health history for the specified time period."""
        current_time = time.time()
        cutoff_time = current_time - (hours * 60 * 60)
        
        return [
            record for record in self.health_history
            if record["timestamp"] >= cutoff_time
        ]
    
    def clear_alerts(self):
        """Clear all stored alerts."""
        self.alerts.clear()
        logger.info("All alerts cleared")
    
    def clear_health_history(self):
        """Clear health history."""
        self.health_history.clear()
        logger.info("Health history cleared")
    
    def update_config(self, 
                     check_interval: Optional[int] = None,
                     alert_threshold: Optional[int] = None,
                     enable_auto_recovery: Optional[bool] = None):
        """Update monitor configuration."""
        if check_interval is not None:
            self.check_interval = check_interval
            logger.info(f"Check interval updated to {check_interval}s")
        
        if alert_threshold is not None:
            self.alert_threshold = alert_threshold
            logger.info(f"Alert threshold updated to {alert_threshold}")
        
        if enable_auto_recovery is not None:
            self.enable_auto_recovery = enable_auto_recovery
            logger.info(f"Auto recovery {'enabled' if enable_auto_recovery else 'disabled'}")


# Global health monitor instance
_health_monitor: Optional[HealthMonitor] = None


def get_health_monitor(service_factory: Optional[ServiceFactory] = None) -> HealthMonitor:
    """Get the global health monitor instance."""
    global _health_monitor
    
    if _health_monitor is None:
        if service_factory is None:
            from .service_factory import get_service_factory
            service_factory = get_service_factory()
        
        _health_monitor = HealthMonitor(service_factory)
    
    return _health_monitor


def shutdown_health_monitor():
    """Shutdown the global health monitor."""
    global _health_monitor
    
    if _health_monitor:
        _health_monitor.stop_monitoring()
        _health_monitor = None
