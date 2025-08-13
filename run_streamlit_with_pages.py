#!/usr/bin/env python3
"""
ZeroRAG Streamlit Startup Script with Pages

This script starts Streamlit with the main application and enables
the health status page as a separate navigation item.

Usage:
    python run_streamlit_with_pages.py
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Start Streamlit with pages configuration."""
    
    # Get the current directory
    current_dir = Path.cwd()
    
    # Check if we're in the right directory
    if not (current_dir / "src" / "ui" / "streamlit_app.py").exists():
        print("❌ Error: Please run this script from the ZeroRAG project root directory")
        print(f"Current directory: {current_dir}")
        print("Expected to find: src/ui/streamlit_app.py")
        sys.exit(1)
    
    # Set up environment variables for Streamlit
    env = os.environ.copy()
    env["STREAMLIT_SERVER_PORT"] = "8501"
    env["STREAMLIT_SERVER_ADDRESS"] = "localhost"
    env["STREAMLIT_SERVER_HEADLESS"] = "true"
    env["STREAMLIT_SERVER_ENABLE_CORS"] = "false"
    env["STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION"] = "false"
    
    print("🚀 Starting ZeroRAG Streamlit Application...")
    print("📱 Main Chat Interface: http://localhost:8501")
    print("🏥 Health Status Page: http://localhost:8501/health_page")
    print("📊 API Documentation: http://localhost:8000/docs")
    print("")
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        # Start Streamlit with the main app
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            str(current_dir / "src" / "ui" / "streamlit_app.py"),
            "--server.port", "8501",
            "--server.address", "localhost",
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false",
            "--browser.gatherUsageStats", "false"
        ]
        
        subprocess.run(cmd, env=env, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Streamlit server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting Streamlit: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
