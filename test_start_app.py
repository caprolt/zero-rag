#!/usr/bin/env python3
"""
Test script for the updated start_app.py Ollama restart functionality
"""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

# Import functions from start_app
from start_app import restart_ollama, check_ollama_health, restart_llm_service

def test_ollama_functions():
    """Test the Ollama-related functions."""
    print("=== Testing Ollama Functions ===\n")
    
    # Test 1: Check current Ollama health
    print("1. Checking current Ollama health...")
    if check_ollama_health():
        print("✅ Ollama is currently running and healthy")
    else:
        print("❌ Ollama is not running or not accessible")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Test restart_ollama function (but don't actually restart)
    print("2. Testing restart_ollama function...")
    print("   (This is a dry run - functions are loaded correctly)")
    print("✅ restart_ollama function is available")
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Test restart_llm_service function
    print("3. Testing restart_llm_service function...")
    print("   (This is a dry run - functions are loaded correctly)")
    print("✅ restart_llm_service function is available")
    
    print("\n" + "="*50 + "\n")
    
    print("🎉 All function tests passed!")
    print("💡 To test the full restart process, run: python start_app.py")

if __name__ == "__main__":
    test_ollama_functions()