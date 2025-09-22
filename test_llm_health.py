#!/usr/bin/env python3
"""
Test script to check LLM service health and configuration
"""

import sys
import json
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.llm import get_llm_service, reset_llm_service
from src.config import get_config

def main():
    print("=== ZeroRAG LLM Service Health Check ===\n")
    
    # Reset and get fresh service
    reset_llm_service()
    
    try:
        # Get configuration
        config = get_config()
        print("Configuration loaded successfully")
        print(f"Ollama Host: {config.ai_model.ollama_host}")
        print(f"Ollama Model: {config.ai_model.ollama_model}")
        print()
        
        # Get LLM service
        llm_service = get_llm_service(config)
        print("LLM Service initialized")
        print(f"Current Provider: {llm_service.current_provider}")
        print(f"Available Providers: {llm_service.get_available_providers()}")
        print()
        
        # Perform health check
        health = llm_service.health_check()
        print("=== Health Check Results ===")
        print(json.dumps(health, indent=2, default=str))
        print()
        
        # Test generation with primary provider if available
        if llm_service.current_provider:
            print(f"=== Testing Generation with {llm_service.current_provider} ===")
            try:
                response = llm_service.generate("Hello, how are you?", max_tokens=50)
                print(f"Provider: {response.provider}")
                print(f"Model: {response.model_name}")
                print(f"Response: {response.text}")
                print(f"Tokens Used: {response.tokens_used}")
                print(f"Response Time: {response.response_time:.2f}s")
                if response.error:
                    print(f"Error: {response.error}")
            except Exception as e:
                print(f"Generation failed: {e}")
        
        # Print metrics
        print("\n=== Performance Metrics ===")
        metrics = llm_service.get_performance_metrics()
        print(json.dumps(metrics, indent=2))
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()