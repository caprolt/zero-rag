# ZeroRAG Health Status Page

## Overview

The ZeroRAG Health Status Page is a dedicated monitoring interface that provides comprehensive system diagnostics and health information. This page is designed to be accessed only when needed, improving the performance of the main chat interface.

## Features

### 🏥 System Health Monitoring
- **Real-time API status** - Monitor API connectivity and response times
- **Service health checks** - Individual service status and diagnostics
- **System metrics** - Uptime, version, and performance data
- **Connection diagnostics** - Detailed API endpoint testing

### 🔍 Diagnostic Tools
- **Connection tests** - Test ping, health, and document endpoints
- **Performance metrics** - Load detailed system performance data
- **Troubleshooting guide** - Common issues and solutions
- **Service details** - Expandable service information

### ⚡ Performance Optimized
- **Lazy loading** - Health data only loads when page is accessed
- **Caching** - Health data cached for 10 seconds to reduce API calls
- **Separate page** - Doesn't impact main chat interface performance
- **On-demand diagnostics** - Tests only run when requested

## Accessing the Health Page

### Method 1: Direct URL
```
http://localhost:8501/health_page
```

### Method 2: Navigation Link
From the main chat interface, click the "🏥 Open Health Status" button in the sidebar.

### Method 3: Programmatic Access
```python
import streamlit as st

# Navigate to health page
st.switch_page("src/ui/pages/health_page.py")
```

## Page Sections

### 📊 Overall System Status
- **System Status Card** - Visual status indicator (Healthy/Degraded/Error)
- **Last Updated** - Timestamp of last health check
- **System Metrics** - Uptime, version, service count, last check

### 🔧 Service Status
- **Individual Services** - Status of each system component
- **Service Details** - Expandable detailed information
- **Status Indicators** - Color-coded status dots

### 🔍 Connection Diagnostics
- **API Endpoint Tests** - Test ping, health, and documents endpoints
- **Response Times** - Measure API performance
- **Status Codes** - HTTP response codes
- **Error Messages** - Detailed error information

### 📊 Performance Metrics
- **System Metrics** - Load detailed performance data
- **JSON Output** - Raw metrics data for analysis

### 🛠️ Troubleshooting Guide
- **Common Issues** - API connection, slow responses, service health
- **Solutions** - Step-by-step troubleshooting steps
- **Best Practices** - System maintenance recommendations

## Performance Benefits

### Before (Integrated Health)
- **15-second delay** on main page load
- **Heavy API calls** on every page refresh
- **Complex status checking** in main interface
- **Detailed health data** always loaded

### After (Separate Health Page)
- **2-3 second delay** on main page load
- **Lightweight status check** only (ping endpoint)
- **Simple status display** in main interface
- **Health data loaded** only when needed

## Configuration

### Health Monitor Settings
```python
class HealthMonitor:
    def __init__(self):
        self.cache_duration = 10  # Cache health data for 10 seconds
        self.timeout = 5          # API timeout in seconds
```

### API Endpoints Tested
- `GET /health/ping` - Quick connectivity test (1s timeout)
- `GET /health` - Detailed health check (5s timeout)
- `GET /documents` - Document service test (5s timeout)
- `GET /metrics` - Performance metrics (5s timeout)

## Troubleshooting

### Health Page Not Loading
1. **Check Streamlit** - Ensure Streamlit is running on port 8501
2. **Verify API** - Ensure API server is running on port 8000
3. **Check URL** - Use correct URL: `http://localhost:8501/health_page`

### API Connection Issues
1. **Start API Server** - Run `python start_app.py`
2. **Check Ports** - Verify port 8000 is available
3. **Firewall** - Check firewall settings
4. **Logs** - Check API server logs for errors

### Slow Health Page
1. **API Performance** - Check API server performance
2. **Network** - Verify network connectivity
3. **Cache** - Health data is cached for 10 seconds
4. **Refresh** - Use refresh button to force update

## Development

### Adding New Health Checks
```python
def test_new_endpoint(self) -> Dict[str, Any]:
    """Test a new API endpoint."""
    start_time = time.time()
    try:
        response = requests.get(f"{API_BASE_URL}/new-endpoint", timeout=5)
        response_time = time.time() - start_time
        return {
            "status": "success" if response.status_code == 200 else "error",
            "response_time": response_time,
            "status_code": response.status_code,
            "message": f"Endpoint test result"
        }
    except Exception as e:
        return {
            "status": "error",
            "response_time": None,
            "status_code": None,
            "message": f"Test failed: {str(e)}"
        }
```

### Customizing the Interface
- **CSS Styling** - Modify the custom CSS in the health page
- **Layout** - Adjust the page layout and sections
- **Metrics** - Add new system metrics and displays
- **Tests** - Add custom diagnostic tests

## Best Practices

### For Users
- **Use sparingly** - Only access when troubleshooting
- **Check main page first** - Use simple status in main interface
- **Follow troubleshooting guide** - Use provided solutions
- **Report issues** - Document any persistent problems

### For Developers
- **Keep it lightweight** - Don't add heavy operations
- **Cache appropriately** - Use caching to reduce API calls
- **Handle errors gracefully** - Provide clear error messages
- **Update documentation** - Keep troubleshooting guide current

## Integration with Main App

The health page integrates seamlessly with the main chat interface:

1. **Simple Status** - Main app shows basic connection status
2. **Health Links** - Easy navigation to health page
3. **Error Handling** - Graceful fallback when API is unavailable
4. **Performance** - No impact on main app performance

This separation ensures the main chat interface remains fast and responsive while providing comprehensive health monitoring when needed.
