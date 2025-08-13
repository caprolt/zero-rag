#!/usr/bin/env python3
"""
Script to restart the ZeroRAG API server and wait for it to be ready.
"""

import subprocess
import time
import requests
import signal
import os
import sys

API_BASE_URL = "http://localhost:8000"

def wait_for_api_ready(max_wait_time=60):
    """Wait for the API to be ready, checking health endpoint."""
    print("🔄 Waiting for API server to start up...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get(f"{API_BASE_URL}/health/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy':
                    print(f"✅ API is ready! (took {time.time() - start_time:.1f} seconds)")
                    return True
        except requests.RequestException:
            pass
        
        print(f"⏳ Still waiting... ({time.time() - start_time:.1f}s elapsed)")
        time.sleep(5)
    
    print(f"❌ API did not become ready within {max_wait_time} seconds")
    return False

def kill_existing_processes():
    """Kill any existing processes on port 8000."""
    try:
        # On Windows, use netstat to find processes
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        for line in lines:
            if ':8000' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    print(f"🔄 Killing process {pid} on port 8000")
                    subprocess.run(['taskkill', '/PID', pid, '/F'], capture_output=True)
                    time.sleep(2)
                    break
    except Exception as e:
        print(f"⚠️ Could not kill existing processes: {e}")

def start_api_server():
    """Start the API server."""
    print("🚀 Starting ZeroRAG API server...")
    
    # Kill any existing processes
    kill_existing_processes()
    
    # Start the server
    try:
        cmd = [
            sys.executable, '-c',
            'import uvicorn; from src.api.main import app; uvicorn.run(app, host="0.0.0.0", port=8000)'
        ]
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print(f"✅ API server process started (PID: {process.pid})")
        return process
        
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None

def main():
    """Main function to restart the API server."""
    print("🔄 ZeroRAG API Server Restart")
    print("=" * 40)
    
    # Start the server
    process = start_api_server()
    if not process:
        return
    
    # Wait for it to be ready
    if wait_for_api_ready():
        print("\n🎉 API server is ready for use!")
        print("\n📝 You can now:")
        print("• Run: python test_specific_queries.py")
        print("• Use the Streamlit UI: python run_streamlit.py")
        print("• Make direct API calls to http://localhost:8000")
        
        # Keep the process running
        try:
            print("\n⏹️ Press Ctrl+C to stop the server")
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping API server...")
            process.terminate()
            process.wait()
            print("✅ API server stopped")
    else:
        print("\n❌ Failed to start API server properly")
        process.terminate()

if __name__ == "__main__":
    main()
