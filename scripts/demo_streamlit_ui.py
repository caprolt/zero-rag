#!/usr/bin/env python3
"""
ZeroRAG Streamlit UI Demo

This script demonstrates how to run the ZeroRAG Streamlit UI.
It provides instructions and checks for the required components.

Usage:
    python scripts/demo_streamlit_ui.py
"""

import sys
import subprocess
import os
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_streamlit():
    """Check if Streamlit is available."""
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} is available")
        return True
    except ImportError:
        print("❌ Streamlit is not installed")
        print("   Install with: pip install streamlit")
        return False

def check_ui_module():
    """Check if the UI module can be imported."""
    try:
        from src.ui import streamlit_app
        print("✅ ZeroRAG UI module is available")
        return True
    except ImportError as e:
        print(f"❌ UI module import failed: {e}")
        return False

def check_api_server():
    """Check if the API server is running."""
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ ZeroRAG API server is running")
            return True
        else:
            print("⚠️  API server responded but not healthy")
            return False
    except requests.RequestException:
        print("❌ ZeroRAG API server is not running")
        print("   Start it with: python -m uvicorn src.api.main:app --reload --port 8000")
        return False

def show_instructions():
    """Show instructions for running the UI."""
    print("\n" + "="*60)
    print("🚀 ZeroRAG Streamlit UI Demo")
    print("="*60)
    
    print("\n📋 Prerequisites:")
    print("   1. Python 3.8+ installed")
    print("   2. Streamlit installed (pip install streamlit)")
    print("   3. ZeroRAG API server running on port 8000")
    print("   4. All project dependencies installed")
    
    print("\n🔧 Setup Instructions:")
    print("   1. Install dependencies:")
    print("      pip install -r requirements.txt")
    print("   2. Start the API server:")
    print("      python -m uvicorn src.api.main:app --reload --port 8000")
    print("   3. In a new terminal, run the Streamlit UI:")
    print("      python run_streamlit.py")
    print("      OR")
    print("      streamlit run src/ui/streamlit_app.py --server.port 8501")
    
    print("\n🌐 Access Points:")
    print("   - Streamlit UI: http://localhost:8501")
    print("   - API Server: http://localhost:8000")
    print("   - API Docs: http://localhost:8000/docs")
    
    print("\n📁 File Structure:")
    print("   - Main UI: src/ui/streamlit_app.py")
    print("   - Runner: run_streamlit.py")
    print("   - Tests: scripts/test_phase_7_1_streamlit.py")
    
    print("\n🎯 Features Available:")
    print("   ✅ Document upload with validation")
    print("   ✅ Upload progress tracking")
    print("   ✅ Chat interface")
    print("   ✅ Source document display")
    print("   ✅ System health monitoring")
    print("   ✅ File management")

def run_streamlit_demo():
    """Run the Streamlit demo if possible."""
    print("\n🎬 Running Streamlit Demo...")
    
    # Check if we can run Streamlit
    if not check_streamlit() or not check_ui_module():
        print("❌ Cannot run demo - missing dependencies")
        return False
    
    # Check API server
    api_available = check_api_server()
    
    if api_available:
        print("\n✅ All systems ready! Starting Streamlit...")
        print("📱 Opening browser at: http://localhost:8501")
        print("⏹️  Press Ctrl+C to stop")
        
        try:
            subprocess.run([
                sys.executable, "-m", "streamlit", "run",
                "src/ui/streamlit_app.py",
                "--server.port", "8501",
                "--server.address", "localhost",
                "--browser.gatherUsageStats", "false"
            ], check=True)
        except KeyboardInterrupt:
            print("\n👋 Demo stopped by user")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running Streamlit: {e}")
            return False
    else:
        print("\n⚠️  API server not available - UI will work in limited mode")
        print("   You can still test the UI structure and upload interface")
        print("   Start the API server to enable full functionality")
        
        response = input("\n🤔 Run Streamlit anyway? (y/N): ")
        if response.lower() in ['y', 'yes']:
            try:
                subprocess.run([
                    sys.executable, "-m", "streamlit", "run",
                    "src/ui/streamlit_app.py",
                    "--server.port", "8501",
                    "--server.address", "localhost",
                    "--browser.gatherUsageStats", "false"
                ], check=True)
            except KeyboardInterrupt:
                print("\n👋 Demo stopped by user")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error running Streamlit: {e}")
                return False
    
    return True

def main():
    """Main demo function."""
    print("🤖 ZeroRAG Streamlit UI Demo")
    print("="*40)
    
    # Check components
    streamlit_ok = check_streamlit()
    ui_ok = check_ui_module()
    api_ok = check_api_server()
    
    print(f"\n📊 Component Status:")
    print(f"   Streamlit: {'✅' if streamlit_ok else '❌'}")
    print(f"   UI Module: {'✅' if ui_ok else '❌'}")
    print(f"   API Server: {'✅' if api_ok else '❌'}")
    
    # Show instructions
    show_instructions()
    
    # Ask if user wants to run the demo
    print("\n" + "="*60)
    response = input("🎬 Would you like to run the Streamlit demo now? (y/N): ")
    
    if response.lower() in ['y', 'yes']:
        run_streamlit_demo()
    else:
        print("\n📚 Demo skipped. Use the instructions above to run manually.")
        print("   Quick start: python run_streamlit.py")

if __name__ == "__main__":
    main()
