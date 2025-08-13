#!/usr/bin/env python3
"""
ZeroRAG Application Starter

This script starts both the FastAPI backend server and the Streamlit frontend
to ensure they work together properly.

Usage:
    python start_app.py
"""

import subprocess
import sys
import time
import threading
import signal
import os
from pathlib import Path

def start_api_server():
    """Start the FastAPI server in a separate process."""
    print("🚀 Starting ZeroRAG API server...")
    
    # Change to the src directory to run the API server
    api_process = subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "src.api.main:app", 
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--reload"
    ], cwd=Path(__file__).parent)
    
    return api_process

def start_streamlit_app():
    """Start the Streamlit app in a separate process."""
    print("🎨 Starting ZeroRAG Streamlit app...")
    
    # Wait a bit for the API server to start
    time.sleep(3)
    
    streamlit_process = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", 
        "src/ui/streamlit_app.py",
        "--server.port", "8501",
        "--server.address", "localhost"
    ], cwd=Path(__file__).parent)
    
    return streamlit_process

def check_api_health():
    """Check if the API server is healthy."""
    import requests
    try:
        response = requests.get("http://localhost:8000/health/ping", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    """Main function to start both applications."""
    print("🤖 Starting ZeroRAG Application...")
    print("=" * 50)
    
    # Start API server
    api_process = start_api_server()
    
    # Wait for API server to be ready
    print("⏳ Waiting for API server to start...")
    print("💡 Note: The API server typically takes 30-45 seconds to fully start up")
    max_wait = 60  # Increased to 60 seconds to accommodate 30-45 second startup time
    wait_time = 0
    
    while wait_time < max_wait:
        if check_api_health():
            print("✅ API server is ready!")
            break
        time.sleep(1)
        wait_time += 1
        if wait_time % 10 == 0:  # Show progress every 10 seconds
            print(f"⏳ Still waiting... ({wait_time}/{max_wait}s) - API server is starting up...")
        elif wait_time % 5 == 0:  # Show dots every 5 seconds
            print(".", end="", flush=True)
    
    if wait_time >= max_wait:
        print("\n❌ API server failed to start within expected time")
        print("💡 The API server might still be starting up. You can:")
        print("   1. Wait a bit longer and refresh the UI")
        print("   2. Check the API server logs for any errors")
        print("   3. Try starting the API server manually: python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload")
        api_process.terminate()
        sys.exit(1)
    
    # Start Streamlit app
    streamlit_process = start_streamlit_app()
    
    print("=" * 50)
    print("🎉 ZeroRAG is now running!")
    print("📱 Streamlit UI: http://localhost:8501")
    print("🔧 API Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("=" * 50)
    print("Press Ctrl+C to stop both applications")
    
    try:
        # Keep the main process running
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if api_process.poll() is not None:
                print("❌ API server process terminated unexpectedly")
                break
                
            if streamlit_process.poll() is not None:
                print("❌ Streamlit process terminated unexpectedly")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down ZeroRAG...")
        
        # Terminate processes
        if api_process.poll() is None:
            api_process.terminate()
            print("✅ API server stopped")
            
        if streamlit_process.poll() is None:
            streamlit_process.terminate()
            print("✅ Streamlit app stopped")
        
        print("👋 Goodbye!")

if __name__ == "__main__":
    main()
