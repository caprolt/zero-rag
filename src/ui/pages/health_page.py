"""
ZeroRAG Health Status Page

This module provides a dedicated page for monitoring system health, API status,
and service diagnostics. This page is only loaded when explicitly accessed,
improving the performance of the main chat interface.

Features:
- Real-time API status monitoring
- Detailed service health checks
- System metrics and performance data
- Connection diagnostics
- Service uptime tracking
"""

import streamlit as st
import requests
import time
import json
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS for health page
st.markdown("""
<style>
    .health-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .status-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 0.75rem;
        margin-bottom: 1rem;
        border-left: 4px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .status-card.healthy {
        border-left-color: #28a745;
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
    }
    
    .status-card.degraded {
        border-left-color: #ffc107;
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
    }
    
    .status-card.error {
        border-left-color: #dc3545;
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
    }
    
    .status-card.offline {
        border-left-color: #6c757d;
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
    }
    
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1f77b4;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    .service-item {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin-bottom: 0.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    
    .service-name {
        font-weight: 500;
        font-size: 1.1rem;
    }
    
    .service-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .status-indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
    }
    
    .status-indicator.healthy { background-color: #28a745; }
    .status-indicator.degraded { background-color: #ffc107; }
    .status-indicator.error { background-color: #dc3545; }
    .status-indicator.offline { background-color: #6c757d; }
    
    .refresh-button {
        background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 0.5rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .refresh-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .connection-test {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e0e0e0;
        margin: 1rem 0;
    }
    
    .test-result {
        padding: 0.5rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
        font-family: monospace;
        font-size: 0.9rem;
    }
    
    .test-result.success {
        background: #d4edda;
        color: #155724;
        border: 1px solid #c3e6cb;
    }
    
    .test-result.error {
        background: #f8d7da;
        color: #721c24;
        border: 1px solid #f5c6cb;
    }
    
    .test-result.warning {
        background: #fff3cd;
        color: #856404;
        border: 1px solid #ffeaa7;
    }
</style>
""", unsafe_allow_html=True)

class HealthMonitor:
    """Comprehensive health monitoring system."""
    
    def __init__(self):
        self.last_check = 0
        self.cache_duration = 10  # Cache health data for 10 seconds
        self.health_cache = {}
        
    def get_overall_health(self) -> Dict[str, Any]:
        """Get comprehensive health status with caching."""
        current_time = time.time()
        
        if current_time - self.last_check < self.cache_duration and self.health_cache:
            return self.health_cache
        
        try:
            # Get detailed health from API
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                self.health_cache = health_data
                self.last_check = current_time
                return health_data
            else:
                return {"error": f"Health check returned {response.status_code}"}
        except requests.RequestException as e:
            return {"error": f"Health check failed: {str(e)}"}
    
    def test_api_connection(self) -> Dict[str, Any]:
        """Test API connectivity with detailed diagnostics."""
        results = {}
        
        # Test ping endpoint
        start_time = time.time()
        try:
            response = requests.get(f"{API_BASE_URL}/health/ping", timeout=1)
            ping_time = time.time() - start_time
            results["ping"] = {
                "status": "success" if response.status_code == 200 else "error",
                "response_time": ping_time,
                "status_code": response.status_code,
                "message": f"Ping successful in {ping_time:.3f}s" if response.status_code == 200 else f"Ping failed with status {response.status_code}"
            }
        except Exception as e:
            results["ping"] = {
                "status": "error",
                "response_time": None,
                "status_code": None,
                "message": f"Ping failed: {str(e)}"
            }
        
        # Test health endpoint
        start_time = time.time()
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            health_time = time.time() - start_time
            results["health"] = {
                "status": "success" if response.status_code == 200 else "error",
                "response_time": health_time,
                "status_code": response.status_code,
                "message": f"Health check successful in {health_time:.3f}s" if response.status_code == 200 else f"Health check failed with status {response.status_code}"
            }
        except Exception as e:
            results["health"] = {
                "status": "error",
                "response_time": None,
                "status_code": None,
                "message": f"Health check failed: {str(e)}"
            }
        
        # Test documents endpoint
        start_time = time.time()
        try:
            response = requests.get(f"{API_BASE_URL}/documents", timeout=5)
            docs_time = time.time() - start_time
            results["documents"] = {
                "status": "success" if response.status_code == 200 else "error",
                "response_time": docs_time,
                "status_code": response.status_code,
                "message": f"Documents endpoint successful in {docs_time:.3f}s" if response.status_code == 200 else f"Documents endpoint failed with status {response.status_code}"
            }
        except Exception as e:
            results["documents"] = {
                "status": "error",
                "response_time": None,
                "status_code": None,
                "message": f"Documents endpoint failed: {str(e)}"
            }
        
        return results
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics."""
        try:
            response = requests.get(f"{API_BASE_URL}/metrics", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Metrics endpoint returned {response.status_code}"}
        except requests.RequestException as e:
            return {"error": f"Metrics endpoint failed: {str(e)}"}

def format_uptime(seconds: float) -> str:
    """Format uptime in human-readable format."""
    if seconds < 60:
        return f"{seconds:.0f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    elif seconds < 86400:
        hours = seconds / 3600
        return f"{hours:.1f}h"
    else:
        days = seconds / 86400
        return f"{days:.1f}d"

def get_status_color(status: str) -> str:
    """Get color for status."""
    colors = {
        "healthy": "#28a745",
        "degraded": "#ffc107", 
        "error": "#dc3545",
        "offline": "#6c757d"
    }
    return colors.get(status, "#6c757d")

def main():
    """Main health status page."""
    
    # Page configuration
    st.set_page_config(
        page_title="ZeroRAG - Health Status",
        page_icon="🏥",
        layout="wide"
    )
    
    # Header
    st.markdown('<h1 class="health-header">🏥 ZeroRAG Health Status</h1>', unsafe_allow_html=True)
    
    # Initialize health monitor
    health_monitor = HealthMonitor()
    
    # Refresh button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🔄 Refresh Health Status", use_container_width=True, key="refresh_health"):
            health_monitor.last_check = 0  # Force refresh
            st.rerun()
    
    # Overall System Status
    st.markdown("## 📊 Overall System Status")
    
    health_data = health_monitor.get_overall_health()
    
    if "error" in health_data:
        st.markdown(f"""
        <div class="status-card error">
            <h3>❌ System Unavailable</h3>
            <p><strong>Error:</strong> {health_data['error']}</p>
            <p>Please check if the API server is running.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Overall status
        overall_status = health_data.get('status', 'unknown')
        status_class = overall_status
        status_icon = "🟢" if overall_status == "healthy" else "🟡" if overall_status == "degraded" else "🔴"
        
        st.markdown(f"""
        <div class="status-card {status_class}">
            <h3>{status_icon} System Status: {overall_status.title()}</h3>
            <p>Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # System metrics
        uptime = health_data.get("uptime", 0)
        st.markdown("### 📈 System Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{format_uptime(uptime)}</div>
                <div class="metric-label">Uptime</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{health_data.get('version', 'N/A')}</div>
                <div class="metric-label">Version</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(health_data.get('services', {}))}</div>
                <div class="metric-label">Services</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{health_data.get('timestamp', 'N/A')}</div>
                <div class="metric-label">Last Check</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Service Status
        st.markdown("### 🔧 Service Status")
        services = health_data.get("services", {})
        
        if services:
            for service_name, service_info in services.items():
                status = service_info.get("status", "unknown")
                status_icon = "🟢" if status == "healthy" else "🟡" if status == "degraded" else "🔴"
                
                st.markdown(f"""
                <div class="service-item">
                    <div class="service-name">{service_name.replace('_', ' ').title()}</div>
                    <div class="service-status">
                        <span class="status-indicator {status}"></span>
                        <span>{status_icon} {status.title()}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Show service details if available
                if service_info.get("details"):
                    with st.expander(f"Details for {service_name}"):
                        st.json(service_info["details"])
        else:
            st.info("No service information available")
    
    # Connection Diagnostics
    st.markdown("## 🔍 Connection Diagnostics")
    
    if st.button("🧪 Run Connection Tests", key="run_tests"):
        with st.spinner("Running connection tests..."):
            test_results = health_monitor.test_api_connection()
            
            for endpoint, result in test_results.items():
                status_class = result["status"]
                icon = "✅" if status_class == "success" else "❌"
                
                st.markdown(f"""
                <div class="connection-test">
                    <h4>{icon} {endpoint.title()} Endpoint</h4>
                    <div class="test-result {status_class}">
                        <strong>Status:</strong> {result['status'].title()}<br>
                        <strong>Response Time:</strong> {result['response_time']:.3f}s if result['response_time'] else 'N/A'<br>
                        <strong>Status Code:</strong> {result['status_code'] if result['status_code'] else 'N/A'}<br>
                        <strong>Message:</strong> {result['message']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    # System Metrics (if available)
    st.markdown("## 📊 Performance Metrics")
    
    if st.button("📈 Load Performance Metrics", key="load_metrics"):
        with st.spinner("Loading performance metrics..."):
            metrics = health_monitor.get_system_metrics()
            
            if "error" in metrics:
                st.error(f"Could not load metrics: {metrics['error']}")
            else:
                st.json(metrics)
    
    # Troubleshooting Guide
    st.markdown("## 🛠️ Troubleshooting Guide")
    
    with st.expander("Common Issues and Solutions"):
        st.markdown("""
        ### API Connection Issues
        
        **Problem:** Cannot connect to API server
        **Solutions:**
        1. Ensure the API server is running: `python start_app.py`
        2. Check if port 8000 is available
        3. Verify firewall settings
        4. Check API server logs for errors
        
        ### Slow Response Times
        
        **Problem:** API responses are slow
        **Solutions:**
        1. Check system resources (CPU, memory)
        2. Verify vector database performance
        3. Check for large document processing
        4. Monitor network connectivity
        
        ### Service Health Issues
        
        **Problem:** Individual services showing degraded/error status
        **Solutions:**
        1. Restart the specific service
        2. Check service logs
        3. Verify dependencies are available
        4. Check configuration settings
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem;">
        ZeroRAG Health Monitor | Last updated: {}
    </div>
    """.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
