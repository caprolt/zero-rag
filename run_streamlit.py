#!/usr/bin/env python3
"""
ZeroRAG Streamlit Runner

This script runs the Streamlit UI for the ZeroRAG system.
It provides a convenient way to start the frontend during development.

Usage:
    python run_streamlit.py
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Run the Streamlit application."""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    
    # Change to project root
    os.chdir(project_root)
    
    # Check if streamlit is available
    try:
        import streamlit
        print("✅ Streamlit is available")
    except ImportError:
        print("❌ Streamlit not found. Please install it with: pip install streamlit")
        sys.exit(1)
    
    # Run streamlit
    print("🚀 Starting ZeroRAG Streamlit UI...")
    print("📱 The UI will be available at: http://localhost:8501")
    print("🔗 Make sure the ZeroRAG API is running at: http://localhost:8000")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            "src/ui/streamlit_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ], check=True)
    except KeyboardInterrupt:
        print("\n👋 Streamlit server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
