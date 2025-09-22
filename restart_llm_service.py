#!/usr/bin/env python3
"""
Script to restart the LLM service and force re-detection of available providers
"""

import sys
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from src.services.service_factory import get_service_factory
from src.models.llm import reset_llm_service

def main():
    print("=== ZeroRAG LLM Service Restart ===\n")
    
    try:
        # Get the service factory
        service_factory = get_service_factory()
        print("Service factory retrieved")
        
        # Check current status
        print("\n=== Current Status ===")
        llm_service = service_factory.get_llm_service()
        if llm_service:
            print(f"Current provider: {llm_service.current_provider}")
            print(f"Available providers: {llm_service.get_available_providers()}")
            
            # Show health status
            health = llm_service.health_check()
            print(f"Health status: {health.get('status')}")
            for provider, provider_health in health.get('provider_health', {}).items():
                print(f"  {provider}: {provider_health.get('status')} - {provider_health.get('error') or 'OK'}")
        
        # Reset the global LLM service
        print("\n=== Resetting LLM Service ===")
        reset_llm_service()
        print("Global LLM service reset")
        
        # Restart the LLM service through service factory
        print("\n=== Restarting LLM Service ===")
        success = service_factory.restart_service("llm")
        if success:
            print("[SUCCESS] LLM service restarted successfully!")
        else:
            print("[ERROR] LLM service restart failed")
            return False
        
        # Check new status
        print("\n=== New Status ===")
        # Force a health check to update service status
        service_factory.perform_health_check()
        llm_service = service_factory.get_llm_service()
        if llm_service:
            print(f"Current provider: {llm_service.current_provider}")
            print(f"Available providers: {llm_service.get_available_providers()}")
            
            # Show health status
            health = llm_service.health_check()
            print(f"Health status: {health.get('status')}")
            for provider, provider_health in health.get('provider_health', {}).items():
                print(f"  {provider}: {provider_health.get('status')} - {provider_health.get('error') or 'OK'}")
            
            # Test generation
            print("\n=== Testing Generation ===")
            response = llm_service.generate("Hello", max_tokens=10)
            print(f"Provider used: {response.provider}")
            print(f"Response: {response.text}")
            if response.error:
                print(f"Error: {response.error}")
            else:
                print("[SUCCESS] Generation test successful!")
        else:
            print("[ERROR] LLM service not available after restart")
            return False
        
        return True
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)