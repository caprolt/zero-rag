#!/usr/bin/env python3
"""
ZeroRAG LLM Service Test Script

This script tests the LLM service functionality including:
- Ollama integration
- HuggingFace fallback
- Streaming responses
- Health checks
- Performance metrics
- Error handling

Usage:
    python scripts/test_llm_service.py
"""

import sys
import time
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from models.llm import LLMService, LLMProvider
from config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_llm_service_initialization():
    """Test LLM service initialization."""
    print("\n" + "="*60)
    print("TESTING LLM SERVICE INITIALIZATION")
    print("="*60)
    
    try:
        # Initialize service
        start_time = time.time()
        service = LLMService()
        init_time = time.time() - start_time
        
        print(f"✅ LLM Service initialized successfully in {init_time:.2f}s")
        print(f"   Current provider: {service.current_provider}")
        
        # Check available providers
        available = service.get_available_providers()
        print(f"   Available providers: {[p.value for p in available]}")
        
        return service
        
    except Exception as e:
        print(f"❌ LLM Service initialization failed: {e}")
        return None


def test_health_check(service):
    """Test health check functionality."""
    print("\n" + "="*60)
    print("TESTING HEALTH CHECK")
    print("="*60)
    
    try:
        health = service.health_check()
        
        print(f"✅ Health check completed")
        print(f"   Overall status: {health['status']}")
        print(f"   Current provider: {health['current_provider']}")
        
        # Provider details
        for provider_name, provider_health in health['providers'].items():
            print(f"   {provider_name}: {provider_health['status']}")
            if provider_health['status'] == 'healthy':
                if 'model_name' in provider_health:
                    print(f"     Model: {provider_health['model_name']}")
                if 'available_models' in provider_health:
                    print(f"     Available models: {provider_health['available_models']}")
            else:
                print(f"     Error: {provider_health.get('error', 'Unknown error')}")
        
        # Metrics
        metrics = health['metrics']
        print(f"   Metrics:")
        print(f"     Total requests: {metrics['total_requests']}")
        print(f"     Error count: {metrics['error_count']}")
        print(f"     Error rate: {metrics['error_rate']:.2%}")
        print(f"     Avg response time: {metrics['average_response_time']:.3f}s")
        
        return health['status'] == 'healthy'
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def test_text_generation(service):
    """Test regular text generation."""
    print("\n" + "="*60)
    print("TESTING TEXT GENERATION")
    print("="*60)
    
    test_prompts = [
        "Hello, how are you?",
        "What is the capital of France?",
        "Explain quantum computing in simple terms.",
        "Write a short poem about technology."
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n--- Test {i}: {prompt[:50]}{'...' if len(prompt) > 50 else ''} ---")
        
        try:
            start_time = time.time()
            response = service.generate(prompt, max_tokens=100, temperature=0.7)
            generation_time = time.time() - start_time
            
            print(f"✅ Generation successful in {generation_time:.2f}s")
            print(f"   Provider: {response.provider.value}")
            print(f"   Model: {response.model_name}")
            print(f"   Response time: {response.response_time:.3f}s")
            if response.tokens_used:
                print(f"   Tokens used: {response.tokens_used}")
            
            # Show response preview
            response_preview = response.text[:100] + "..." if len(response.text) > 100 else response.text
            print(f"   Response: {response_preview}")
            
        except Exception as e:
            print(f"❌ Generation failed: {e}")


def test_streaming_generation(service):
    """Test streaming text generation."""
    print("\n" + "="*60)
    print("TESTING STREAMING GENERATION")
    print("="*60)
    
    test_prompt = "Write a short story about a robot learning to paint."
    
    print(f"Prompt: {test_prompt}")
    print("Streaming response:")
    print("-" * 40)
    
    try:
        start_time = time.time()
        chunks = []
        
        for chunk in service.generate_streaming(test_prompt, max_tokens=150, temperature=0.8):
            print(chunk, end='', flush=True)
            chunks.append(chunk)
        
        streaming_time = time.time() - start_time
        full_response = ''.join(chunks)
        
        print(f"\n\n✅ Streaming completed in {streaming_time:.2f}s")
        print(f"   Total chunks: {len(chunks)}")
        print(f"   Total characters: {len(full_response)}")
        print(f"   Average chunk size: {len(full_response)/len(chunks):.1f} chars")
        
    except Exception as e:
        print(f"\n❌ Streaming failed: {e}")


def test_provider_switching(service):
    """Test provider switching functionality."""
    print("\n" + "="*60)
    print("TESTING PROVIDER SWITCHING")
    print("="*60)
    
    available = service.get_available_providers()
    
    if len(available) < 2:
        print("⚠️  Only one provider available, skipping switching test")
        return
    
    current_provider = service.current_provider
    print(f"Current provider: {current_provider.value}")
    
    # Try switching to other provider
    for provider in available:
        if provider != current_provider:
            print(f"\nAttempting to switch to {provider.value}...")
            
            success = service.switch_provider(provider)
            if success:
                print(f"✅ Successfully switched to {provider.value}")
                
                # Test generation with new provider
                try:
                    response = service.generate("Quick test after switching", max_tokens=50)
                    print(f"   Test generation successful with {response.provider.value}")
                except Exception as e:
                    print(f"   Test generation failed: {e}")
                
                # Switch back
                service.switch_provider(current_provider)
                print(f"   Switched back to {current_provider.value}")
            else:
                print(f"❌ Failed to switch to {provider.value}")


def test_error_handling(service):
    """Test error handling scenarios."""
    print("\n" + "="*60)
    print("TESTING ERROR HANDLING")
    print("="*60)
    
    # Test with empty prompt
    print("\n--- Test: Empty prompt ---")
    try:
        response = service.generate("", max_tokens=10)
        print(f"✅ Empty prompt handled: {len(response.text)} chars")
    except Exception as e:
        print(f"❌ Empty prompt failed: {e}")
    
    # Test with very long prompt
    print("\n--- Test: Very long prompt ---")
    long_prompt = "This is a very long prompt. " * 1000
    try:
        response = service.generate(long_prompt, max_tokens=10)
        print(f"✅ Long prompt handled: {len(response.text)} chars")
    except Exception as e:
        print(f"❌ Long prompt failed: {e}")
    
    # Test with invalid parameters
    print("\n--- Test: Invalid parameters ---")
    try:
        response = service.generate("Test", temperature=2.5, max_tokens=-1)
        print(f"✅ Invalid parameters handled gracefully")
    except Exception as e:
        print(f"❌ Invalid parameters failed: {e}")


def test_performance_benchmark(service):
    """Test performance with multiple requests."""
    print("\n" + "="*60)
    print("PERFORMANCE BENCHMARK")
    print("="*60)
    
    test_prompt = "Generate a creative response to this prompt."
    num_requests = 5
    
    print(f"Running {num_requests} requests...")
    
    start_time = time.time()
    successful_requests = 0
    total_response_time = 0
    
    for i in range(num_requests):
        try:
            request_start = time.time()
            response = service.generate(test_prompt, max_tokens=50, temperature=0.7)
            request_time = time.time() - request_start
            
            successful_requests += 1
            total_response_time += request_time
            
            print(f"   Request {i+1}: {request_time:.3f}s ({response.provider.value})")
            
        except Exception as e:
            print(f"   Request {i+1}: Failed - {e}")
    
    total_time = time.time() - start_time
    avg_response_time = total_response_time / successful_requests if successful_requests > 0 else 0
    
    print(f"\n📊 Performance Summary:")
    print(f"   Total time: {total_time:.2f}s")
    print(f"   Successful requests: {successful_requests}/{num_requests}")
    print(f"   Success rate: {successful_requests/num_requests:.1%}")
    print(f"   Average response time: {avg_response_time:.3f}s")
    print(f"   Requests per second: {successful_requests/total_time:.2f}")


def main():
    """Main test function."""
    print("🚀 ZeroRAG LLM Service Test")
    print("="*60)
    
    # Test initialization
    service = test_llm_service_initialization()
    if not service:
        print("❌ Cannot proceed without LLM service")
        return
    
    # Test health check
    health_ok = test_health_check(service)
    if not health_ok:
        print("⚠️  Service health check failed, but continuing with tests")
    
    # Test text generation
    test_text_generation(service)
    
    # Test streaming generation
    test_streaming_generation(service)
    
    # Test provider switching
    test_provider_switching(service)
    
    # Test error handling
    test_error_handling(service)
    
    # Performance benchmark
    test_performance_benchmark(service)
    
    # Final health check
    print("\n" + "="*60)
    print("FINAL HEALTH CHECK")
    print("="*60)
    
    final_health = service.health_check()
    final_metrics = final_health['metrics']
    
    print(f"✅ Final status: {final_health['status']}")
    print(f"   Total requests: {final_metrics['total_requests']}")
    print(f"   Error rate: {final_metrics['error_rate']:.1%}")
    print(f"   Average response time: {final_metrics['average_response_time']:.3f}s")
    
    print("\n🎉 LLM Service test completed successfully!")


if __name__ == "__main__":
    main()
