#!/usr/bin/env python3
"""
ZeroRAG Full Application Startup Script

This script starts both the FastAPI backend and Next.js frontend
for the complete ZeroRAG application.
"""

import os
import sys
import time
import signal
import subprocess
import threading
from pathlib import Path
import requests
from typing import Optional

class ZeroRAGStarter:
    def __init__(self):
        self.backend_process: Optional[subprocess.Popen] = None
        self.frontend_process: Optional[subprocess.Popen] = None
        self.running = True
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print("\n🛑 Shutting down ZeroRAG...")
        self.running = False
        self.stop_services()
        sys.exit(0)
    
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        print("🔍 Checking dependencies...")
        
        # Check if Node.js and pnpm are available
        try:
            subprocess.run(["node", "--version"], check=True, capture_output=True)
            print("✅ Node.js is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ Node.js is not installed. Please install Node.js first.")
            return False
        
        try:
            subprocess.run(["pnpm", "--version"], check=True, capture_output=True)
            print("✅ pnpm is available")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("❌ pnpm is not installed. Installing pnpm...")
            try:
                subprocess.run(["npm", "install", "-g", "pnpm"], check=True)
                print("✅ pnpm installed successfully")
            except subprocess.CalledProcessError:
                print("❌ Failed to install pnpm. Please install it manually: npm install -g pnpm")
                return False
        
        # Check if Python dependencies are installed
        try:
            import fastapi
            import uvicorn
            print("✅ Python dependencies are available")
        except ImportError:
            print("❌ Python dependencies are missing. Installing...")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
                print("✅ Python dependencies installed")
            except subprocess.CalledProcessError:
                print("❌ Failed to install Python dependencies")
                return False
        
        return True
    
    def install_frontend_dependencies(self):
        """Install frontend dependencies if needed"""
        print("📦 Installing frontend dependencies...")
        try:
            subprocess.run(["pnpm", "install"], check=True)
            print("✅ Frontend dependencies installed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install frontend dependencies")
            return False
    
    def start_backend(self):
        """Start the FastAPI backend"""
        print("🚀 Starting FastAPI backend...")
        
        # Check if backend is already running
        try:
            response = requests.get("http://localhost:8000/health", timeout=5)
            if response.status_code == 200:
                print("✅ Backend is already running on port 8000")
                return True
        except requests.RequestException:
            pass
        
        # Start the backend
        try:
            self.backend_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "src.api.main:app",
                "--reload", "--host", "127.0.0.1", "--port", "8000"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for backend to start
            for i in range(30):  # Wait up to 30 seconds
                try:
                    response = requests.get("http://localhost:8000/health", timeout=2)
                    if response.status_code == 200:
                        print("✅ Backend started successfully on http://localhost:8000")
                        return True
                except requests.RequestException:
                    pass
                time.sleep(1)
            
            print("❌ Backend failed to start within 30 seconds")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def start_frontend(self):
        """Start the Next.js frontend"""
        print("🎨 Starting Next.js frontend...")
        
        # Check if frontend is already running
        try:
            response = requests.get("http://localhost:3000", timeout=5)
            if response.status_code == 200:
                print("✅ Frontend is already running on port 3000")
                return True
        except requests.RequestException:
            pass
        
        # Start the frontend
        try:
            self.frontend_process = subprocess.Popen([
                "pnpm", "dev"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Wait for frontend to start
            for i in range(30):  # Wait up to 30 seconds
                try:
                    response = requests.get("http://localhost:3000", timeout=2)
                    if response.status_code == 200:
                        print("✅ Frontend started successfully on http://localhost:3000")
                        return True
                except requests.RequestException:
                    pass
                time.sleep(1)
            
            print("❌ Frontend failed to start within 30 seconds")
            return False
            
        except Exception as e:
            print(f"❌ Failed to start frontend: {e}")
            return False
    
    def stop_services(self):
        """Stop all running services"""
        print("🛑 Stopping services...")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
            print("✅ Frontend stopped")
        
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
            print("✅ Backend stopped")
    
    def run(self):
        """Main run method"""
        print("🚀 ZeroRAG Full Application Starter")
        print("=" * 50)
        
        # Check dependencies
        if not self.check_dependencies():
            print("❌ Dependency check failed. Please install missing dependencies.")
            return False
        
        # Install frontend dependencies
        if not self.install_frontend_dependencies():
            print("❌ Frontend dependency installation failed.")
            return False
        
        # Start backend
        if not self.start_backend():
            print("❌ Backend startup failed.")
            return False
        
        # Start frontend
        if not self.start_frontend():
            print("❌ Frontend startup failed.")
            return False
        
        print("\n🎉 ZeroRAG is now running!")
        print("📱 Modern UI: http://localhost:3000")
        print("🐍 Legacy UI: http://localhost:8501")
        print("📚 API Docs: http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop all services")
        
        # Keep the script running
        try:
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        return True

def main():
    """Main entry point"""
    starter = ZeroRAGStarter()
    success = starter.run()
    
    if not success:
        print("\n❌ Failed to start ZeroRAG. Please check the error messages above.")
        sys.exit(1)
    
    print("\n👋 ZeroRAG stopped. Goodbye!")

if __name__ == "__main__":
    main()
