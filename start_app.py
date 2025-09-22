#!/usr/bin/env python3
"""
ZeroRAG Application Starter

This script starts both the FastAPI backend server and the Streamlit frontend
to ensure they work together properly. It also restarts Ollama to ensure
fresh LLM service initialization.

Usage:
    python start_app.py
"""

import subprocess
import sys
import time
import threading
import signal
import os
import platform
from pathlib import Path

def restart_ollama():
    """Restart Ollama service to ensure it's running and fresh."""
    print("🔄 Restarting Ollama...")
    
    try:
        system = platform.system().lower()
        
        if system == "windows":
            # On Windows, try to stop and start Ollama service
            try:
                # Try to stop Ollama if it's running
                print("⏹️  Stopping Ollama service...")
                subprocess.run(["taskkill", "/F", "/IM", "ollama.exe"], 
                             capture_output=True, check=False)
                time.sleep(2)
            except Exception as e:
                print(f"   Note: Could not stop Ollama process: {e}")
            
            try:
                # Start Ollama service
                print("▶️  Starting Ollama service...")
                # Try different common Ollama installation paths
                ollama_paths = [
                    "ollama",  # If in PATH
                    r"C:\Users\%USERNAME%\AppData\Local\Programs\Ollama\ollama.exe",
                    r"C:\Program Files\Ollama\ollama.exe",
                    r"C:\Program Files (x86)\Ollama\ollama.exe"
                ]
                
                ollama_started = False
                for ollama_path in ollama_paths:
                    try:
                        # Expand environment variables
                        expanded_path = os.path.expandvars(ollama_path)
                        if ollama_path == "ollama" or os.path.exists(expanded_path):
                            subprocess.Popen([expanded_path, "serve"], 
                                           creationflags=subprocess.CREATE_NO_WINDOW)
                            ollama_started = True
                            print(f"✅ Ollama started using: {ollama_path}")
                            break
                    except Exception as e:
                        continue
                
                if not ollama_started:
                    print("⚠️  Could not start Ollama automatically. Please ensure Ollama is installed and running.")
                    print("   You can start it manually by running 'ollama serve' in a terminal.")
                    return False
            except Exception as e:
                print(f"⚠️  Error starting Ollama: {e}")
                return False
                        
        else:
            # On Linux/macOS, try to restart Ollama
            try:
                print("⏹️  Stopping Ollama...")
                subprocess.run(["pkill", "-f", "ollama"], capture_output=True, check=False)
                time.sleep(2)
            except Exception:
                pass
            
            try:
                print("▶️  Starting Ollama...")
                subprocess.Popen(["ollama", "serve"], 
                               stdout=subprocess.DEVNULL, 
                               stderr=subprocess.DEVNULL)
                print("✅ Ollama service started")
            except Exception as e:
                print(f"⚠️  Could not start Ollama: {e}")
                return False
        
        # Wait for Ollama to be ready
        print("⏳ Waiting for Ollama to be ready...")
        max_wait = 30
        wait_time = 0
        
        while wait_time < max_wait:
            if check_ollama_health():
                print("✅ Ollama is ready!")
                return True
            time.sleep(1)
            wait_time += 1
            if wait_time % 5 == 0:
                print(f"   Still waiting... ({wait_time}/{max_wait}s)")
        
        print("⚠️  Ollama did not become ready within 30 seconds")
        return False
        
    except Exception as e:
        print(f"❌ Error restarting Ollama: {e}")
        return False

def check_ollama_health():
    """Check if Ollama is running and accessible."""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        return response.status_code == 200
    except Exception:
        return False

def restart_llm_service():
    """Restart the LLM service to detect Ollama after restart."""
    print("🔄 Restarting LLM service to detect Ollama...")
    
    try:
        # Run the restart script we created earlier
        restart_script = Path(__file__).parent / "restart_llm_service.py"
        if restart_script.exists():
            result = subprocess.run([
                sys.executable, str(restart_script)
            ], capture_output=True, text=True, cwd=Path(__file__).parent)
            
            if result.returncode == 0:
                print("✅ LLM service restarted successfully!")
                return True
            else:
                print(f"⚠️  LLM service restart had issues: {result.stderr}")
                return False
        else:
            print("⚠️  LLM restart script not found, skipping...")
            return True
            
    except Exception as e:
        print(f"❌ Error restarting LLM service: {e}")
        return False

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
    
    # Step 1: Restart Ollama to ensure fresh start
    ollama_success = restart_ollama()
    if not ollama_success:
        print("⚠️  Ollama restart failed, but continuing anyway...")
        print("   The application may fall back to HuggingFace models.")
    
    # Step 2: Restart LLM service to detect Ollama
    if ollama_success:
        llm_restart_success = restart_llm_service()
        if not llm_restart_success:
            print("⚠️  LLM service restart failed, but continuing anyway...")
    
    print("=" * 50)
    
    # Step 3: Start API server
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
