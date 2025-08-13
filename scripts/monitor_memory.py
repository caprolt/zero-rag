#!/usr/bin/env python3
"""
ZeroRAG Memory Monitor

This script continuously monitors memory usage and provides real-time alerts.
Useful for tracking memory patterns and detecting memory leaks.
"""

import os
import sys
import time
import psutil
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import get_config


class MemoryMonitor:
    """Real-time memory monitoring with alerts."""
    
    def __init__(self):
        self.config = get_config()
        self.memory_history = []
        self.alert_history = []
        self.start_time = datetime.now()
        
    def get_memory_info(self) -> Dict[str, Any]:
        """Get current memory information."""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            system_memory = psutil.virtual_memory()
            
            return {
                "timestamp": datetime.now(),
                "process_rss_mb": memory_info.rss / 1024 / 1024,
                "process_vms_mb": memory_info.vms / 1024 / 1024,
                "process_percent": process.memory_percent(),
                "system_total_mb": system_memory.total / 1024 / 1024,
                "system_available_mb": system_memory.available / 1024 / 1024,
                "system_percent": system_memory.percent
            }
        except Exception as e:
            return {"error": str(e)}
    
    def check_alerts(self, memory_info: Dict[str, Any]) -> List[str]:
        """Check for memory alerts based on current usage."""
        alerts = []
        
        if "error" in memory_info:
            alerts.append(f"❌ ERROR: {memory_info['error']}")
            return alerts
        
        process_mb = memory_info["process_rss_mb"]
        system_percent = memory_info["system_percent"]
        
        # Process memory alerts
        if process_mb > self.config.api.memory_critical_threshold_mb:
            alerts.append(f"🚨 CRITICAL: Process memory {process_mb:.1f}MB exceeds critical threshold {self.config.api.memory_critical_threshold_mb}MB")
        elif process_mb > self.config.api.memory_threshold_mb:
            alerts.append(f"⚠️ HIGH: Process memory {process_mb:.1f}MB exceeds normal threshold {self.config.api.memory_threshold_mb}MB")
        elif process_mb > self.config.api.memory_threshold_mb * 0.8:
            alerts.append(f"📈 APPROACHING: Process memory {process_mb:.1f}MB approaching threshold {self.config.api.memory_threshold_mb}MB")
        
        # System memory alerts
        if system_percent > 90:
            alerts.append(f"🚨 CRITICAL: System memory usage {system_percent:.1f}%")
        elif system_percent > 80:
            alerts.append(f"⚠️ HIGH: System memory usage {system_percent:.1f}%")
        
        return alerts
    
    def detect_memory_leak(self) -> Dict[str, Any]:
        """Detect potential memory leaks by analyzing history."""
        if len(self.memory_history) < 20:
            return {"detected": False, "reason": "Insufficient data"}
        
        # Get last 20 measurements
        recent_memory = [entry["process_rss_mb"] for entry in self.memory_history[-20:]]
        
        # Check for consistent increase
        increasing_count = sum(1 for i in range(len(recent_memory)-1) if recent_memory[i] <= recent_memory[i+1])
        
        if increasing_count >= 15:  # 75% of measurements show increase
            total_increase = recent_memory[-1] - recent_memory[0]
            if total_increase > 200:  # 200MB increase
                return {
                    "detected": True,
                    "increase_mb": total_increase,
                    "measurements": len(recent_memory),
                    "increasing_percentage": (increasing_count / (len(recent_memory)-1)) * 100
                }
        
        return {"detected": False, "reason": "No significant increase detected"}
    
    def print_status(self, memory_info: Dict[str, Any], alerts: List[str]):
        """Print current memory status."""
        if "error" in memory_info:
            print(f"❌ {memory_info['error']}")
            return
        
        # Clear screen (works on most terminals)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print("🔍 ZeroRAG Memory Monitor")
        print("=" * 50)
        print(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Current: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Runtime: {datetime.now() - self.start_time}")
        print()
        
        # Process Memory
        print("🔄 PROCESS MEMORY:")
        print(f"   RSS: {memory_info['process_rss_mb']:.1f}MB")
        print(f"   VMS: {memory_info['process_vms_mb']:.1f}MB")
        print(f"   Percent: {memory_info['process_percent']:.1f}%")
        print()
        
        # System Memory
        print("💻 SYSTEM MEMORY:")
        print(f"   Total: {memory_info['system_total_mb']:.0f}MB")
        print(f"   Available: {memory_info['system_available_mb']:.0f}MB")
        print(f"   Used: {memory_info['system_percent']:.1f}%")
        print()
        
        # Thresholds
        print("⚙️ THRESHOLDS:")
        print(f"   Normal: {self.config.api.memory_threshold_mb}MB")
        print(f"   Critical: {self.config.api.memory_critical_threshold_mb}MB")
        print()
        
        # Alerts
        if alerts:
            print("🚨 ALERTS:")
            for alert in alerts:
                print(f"   {alert}")
            print()
        
        # Memory leak detection
        leak_info = self.detect_memory_leak()
        if leak_info["detected"]:
            print("🔍 MEMORY LEAK DETECTED:")
            print(f"   Increase: {leak_info['increase_mb']:.1f}MB")
            print(f"   Measurements: {leak_info['measurements']}")
            print(f"   Increasing: {leak_info['increasing_percentage']:.1f}%")
            print()
        
        # History summary
        if self.memory_history:
            memory_values = [entry["process_rss_mb"] for entry in self.memory_history]
            print("📊 HISTORY:")
            print(f"   Average: {sum(memory_values) / len(memory_values):.1f}MB")
            print(f"   Min: {min(memory_values):.1f}MB")
            print(f"   Max: {max(memory_values):.1f}MB")
            print(f"   Range: {max(memory_values) - min(memory_values):.1f}MB")
            print()
        
        print("Press Ctrl+C to stop monitoring")
    
    def monitor(self, interval_seconds: int = 5, max_history: int = 100):
        """Start continuous memory monitoring."""
        print(f"🔍 Starting memory monitoring (interval: {interval_seconds}s)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                # Get memory info
                memory_info = self.get_memory_info()
                
                # Store in history
                self.memory_history.append(memory_info)
                if len(self.memory_history) > max_history:
                    self.memory_history = self.memory_history[-max_history:]
                
                # Check for alerts
                alerts = self.check_alerts(memory_info)
                if alerts:
                    self.alert_history.extend(alerts)
                    if len(self.alert_history) > 50:
                        self.alert_history = self.alert_history[-50:]
                
                # Print status
                self.print_status(memory_info, alerts)
                
                # Wait for next check
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n⏹️ Monitoring stopped by user")
            self.save_report()
    
    def save_report(self, filename: str = "memory_monitor_report.json"):
        """Save monitoring report to file."""
        if not self.memory_history:
            print("No data to save")
            return
        
        report = {
            "start_time": self.start_time.isoformat(),
            "end_time": datetime.now().isoformat(),
            "duration_seconds": (datetime.now() - self.start_time).total_seconds(),
            "memory_history": [
                {
                    "timestamp": entry["timestamp"].isoformat(),
                    "process_rss_mb": entry["process_rss_mb"],
                    "process_vms_mb": entry["process_vms_mb"],
                    "process_percent": entry["process_percent"],
                    "system_percent": entry["system_percent"]
                }
                for entry in self.memory_history
            ],
            "alerts": self.alert_history,
            "leak_detection": self.detect_memory_leak()
        }
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report saved to {filename}")


def main():
    """Main function for memory monitoring."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ZeroRAG Memory Monitor")
    parser.add_argument("--interval", "-i", type=int, default=5, 
                       help="Monitoring interval in seconds (default: 5)")
    parser.add_argument("--max-history", "-m", type=int, default=100,
                       help="Maximum history entries to keep (default: 100)")
    
    args = parser.parse_args()
    
    monitor = MemoryMonitor()
    monitor.monitor(interval_seconds=args.interval, max_history=args.max_history)


if __name__ == "__main__":
    main()
