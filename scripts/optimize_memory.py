#!/usr/bin/env python3
"""
ZeroRAG Memory Optimization Script

This script analyzes memory usage and provides recommendations for optimization.
Enhanced with new memory thresholds and better analysis tools.
"""

import os
import sys
import psutil
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import get_config


class MemoryOptimizer:
    """Memory optimization analyzer and recommender."""
    
    def __init__(self):
        self.config = get_config()
        self.current_memory = self._get_current_memory()
        
    def _get_current_memory(self) -> Dict[str, float]:
        """Get current memory usage."""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "percent": process.memory_percent()
            }
        except Exception as e:
            print(f"Error getting memory info: {e}")
            return {"rss_mb": 0, "vms_mb": 0, "percent": 0}
    
    def analyze_memory_usage(self) -> Dict[str, Any]:
        """Analyze current memory usage and provide recommendations."""
        current_threshold = self.config.api.memory_threshold_mb
        current_critical = self.config.api.memory_critical_threshold_mb
        
        recommendations = []
        status = "normal"
        
        if self.current_memory["rss_mb"] > current_critical:
            status = "critical"
            recommendations.append("🚨 CRITICAL: Memory usage exceeds critical threshold")
            recommendations.append("💡 Immediate action required - consider restarting the application")
        elif self.current_memory["rss_mb"] > current_threshold:
            status = "high"
            recommendations.append("⚠️ HIGH: Memory usage exceeds normal threshold")
            recommendations.append("💡 Consider increasing MEMORY_THRESHOLD_MB to 2000-2500MB")
            recommendations.append("💡 Consider increasing MEMORY_CRITICAL_THRESHOLD_MB to 3000-3500MB")
        elif self.current_memory["rss_mb"] > current_threshold * 0.8:
            status = "approaching"
            recommendations.append("📈 APPROACHING: Memory usage approaching threshold")
            recommendations.append("💡 Monitor closely and consider optimization")
        else:
            status = "normal"
            recommendations.append("✅ NORMAL: Memory usage is within acceptable range")
        
        # System-specific recommendations
        total_ram = psutil.virtual_memory().total / 1024 / 1024
        if total_ram < 4000:  # Less than 4GB RAM
            recommendations.append("💻 LOW RAM SYSTEM: Consider reducing batch sizes and chunk sizes")
            recommendations.append("💡 Set BATCH_SIZE=50 and CHUNK_SIZE=500")
        elif total_ram > 16000:  # More than 16GB RAM
            recommendations.append("💻 HIGH RAM SYSTEM: Can safely increase memory thresholds")
            recommendations.append("💡 Consider MEMORY_THRESHOLD_MB=3000 and MEMORY_CRITICAL_THRESHOLD_MB=4000")
        
        return {
            "status": status,
            "current_memory_mb": self.current_memory["rss_mb"],
            "current_threshold_mb": current_threshold,
            "current_critical_mb": current_critical,
            "total_system_ram_mb": total_ram,
            "recommendations": recommendations
        }
    
    def get_optimized_config(self) -> Dict[str, Any]:
        """Get optimized configuration based on system resources."""
        total_ram = psutil.virtual_memory().total / 1024 / 1024
        
        recommendations = {}
        
        if total_ram < 4000:  # Low RAM system
            recommendations["MEMORY_THRESHOLD_MB"] = 800
            recommendations["MEMORY_CRITICAL_THRESHOLD_MB"] = 1200
            recommendations["BATCH_SIZE"] = 50
            recommendations["CHUNK_SIZE"] = 500
            recommendations["EMBEDDING_BATCH_SIZE"] = 16
        elif total_ram < 8000:  # Medium RAM system
            recommendations["MEMORY_THRESHOLD_MB"] = 1500
            recommendations["MEMORY_CRITICAL_THRESHOLD_MB"] = 2000
            recommendations["BATCH_SIZE"] = 75
            recommendations["CHUNK_SIZE"] = 750
            recommendations["EMBEDDING_BATCH_SIZE"] = 24
        elif total_ram < 16000:  # High RAM system
            recommendations["MEMORY_THRESHOLD_MB"] = 2500
            recommendations["MEMORY_CRITICAL_THRESHOLD_MB"] = 3500
            recommendations["BATCH_SIZE"] = 100
            recommendations["CHUNK_SIZE"] = 1000
            recommendations["EMBEDDING_BATCH_SIZE"] = 32
        else:  # Very high RAM system
            recommendations["MEMORY_THRESHOLD_MB"] = 4000
            recommendations["MEMORY_CRITICAL_THRESHOLD_MB"] = 5000
            recommendations["BATCH_SIZE"] = 150
            recommendations["CHUNK_SIZE"] = 1200
            recommendations["EMBEDDING_BATCH_SIZE"] = 48
        
        return recommendations
    
    def generate_report(self) -> str:
        """Generate a comprehensive memory optimization report."""
        analysis = self.analyze_memory_usage()
        optimized_config = self.get_optimized_config()
        
        report = []
        report.append("=" * 60)
        report.append("ZERO RAG MEMORY OPTIMIZATION REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Current Status
        report.append("📊 CURRENT STATUS:")
        report.append(f"   Memory Usage: {self.current_memory['rss_mb']:.1f}MB")
        report.append(f"   Memory Threshold: {analysis['current_threshold_mb']}MB")
        report.append(f"   Critical Threshold: {analysis['current_critical_mb']}MB")
        report.append(f"   System RAM: {analysis['total_system_ram_mb']:.0f}MB")
        report.append(f"   Status: {analysis['status'].upper()}")
        report.append("")
        
        # Recommendations
        report.append("💡 RECOMMENDATIONS:")
        for rec in analysis['recommendations']:
            report.append(f"   {rec}")
        report.append("")
        
        # Optimized Configuration
        report.append("⚙️ OPTIMIZED CONFIGURATION:")
        for key, value in optimized_config.items():
            report.append(f"   {key}: {value}")
        report.append("")
        
        # Environment Variables
        report.append("🔧 ENVIRONMENT VARIABLES TO SET:")
        for key, value in optimized_config.items():
            report.append(f"   export {key}={value}")
        report.append("")
        
        # Performance Tips
        report.append("🚀 PERFORMANCE TIPS:")
        report.append("   1. Monitor memory usage with: python scripts/optimize_memory.py")
        report.append("   2. Use smaller batch sizes for large documents")
        report.append("   3. Consider using SSD storage for better I/O performance")
        report.append("   4. Restart the application if memory usage becomes critical")
        report.append("   5. Use the health monitoring page to track performance")
        report.append("")
        
        report.append("=" * 60)
        
        return "\n".join(report)
    
    def save_report(self, filename: str = "memory_optimization_report.txt"):
        """Save the optimization report to a file."""
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            f.write(report)
        
        print(f"Report saved to {filename}")
    
    def check_vector_store_memory(self) -> Dict[str, Any]:
        """Check vector store specific memory usage."""
        try:
            from services.vector_store import VectorStoreService
            
            # Create a temporary vector store instance to check memory
            vector_store = VectorStoreService()
            
            # Get memory usage before and after operations
            memory_before = self._get_current_memory()
            
            # Perform a simple operation to check memory impact
            try:
                stats = vector_store.get_collection_stats()
                memory_after = self._get_current_memory()
                
                memory_impact = memory_after["rss_mb"] - memory_before["rss_mb"]
                
                return {
                    "memory_before_mb": memory_before["rss_mb"],
                    "memory_after_mb": memory_after["rss_mb"],
                    "memory_impact_mb": memory_impact,
                    "collection_stats": stats,
                    "status": "healthy" if memory_impact < 100 else "high_memory_usage"
                }
            except Exception as e:
                return {
                    "error": str(e),
                    "status": "error"
                }
                
        except Exception as e:
            return {
                "error": f"Could not check vector store: {e}",
                "status": "error"
            }


def main():
    """Main function to run memory optimization analysis."""
    print("🔍 ZeroRAG Memory Optimization Analysis")
    print("=" * 50)
    
    optimizer = MemoryOptimizer()
    
    # Generate and display report
    report = optimizer.generate_report()
    print(report)
    
    # Check vector store memory
    print("\n🔍 Checking Vector Store Memory Usage...")
    vector_store_info = optimizer.check_vector_store_memory()
    
    if "error" in vector_store_info:
        print(f"❌ Error: {vector_store_info['error']}")
    else:
        print(f"✅ Vector Store Status: {vector_store_info['status']}")
        print(f"   Memory Impact: {vector_store_info['memory_impact_mb']:.1f}MB")
        if "collection_stats" in vector_store_info:
            stats = vector_store_info["collection_stats"]
            print(f"   Total Documents: {getattr(stats, 'total_points', 'N/A')}")
            print(f"   Collection Size: {getattr(stats, 'collection_size', 'N/A')}MB")
    
    # Save report
    optimizer.save_report()
    
    print("\n✅ Analysis complete! Check memory_optimization_report.txt for details.")


if __name__ == "__main__":
    main()
