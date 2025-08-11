#!/usr/bin/env python3
"""
ZeroRAG Service Test Script
Tests the connectivity and functionality of Qdrant and Redis services
"""

import os
import sys
import time
import requests
import redis
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_qdrant_connection() -> Dict[str, Any]:
    """Test Qdrant vector database connection"""
    print("🔍 Testing Qdrant connection...")
    
    try:
        # Test collections endpoint (Qdrant doesn't have a /health endpoint)
        response = requests.get("http://localhost:6333/collections", timeout=10)
        if response.status_code == 200:
            collections = response.json()
            print("✅ Qdrant collections endpoint working")
            print(f"✅ Found {len(collections.get('result', {}).get('collections', []))} collections")
            return {"status": "success", "collections": collections}
        else:
            print(f"❌ Qdrant collections endpoint failed with status {response.status_code}")
            return {"status": "failed", "error": f"Collections endpoint failed: {response.status_code}"}
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Qdrant. Is it running on localhost:6333?")
        return {"status": "failed", "error": "Connection refused"}
    except requests.exceptions.Timeout:
        print("❌ Qdrant connection timeout")
        return {"status": "failed", "error": "Connection timeout"}
    except Exception as e:
        print(f"❌ Qdrant test failed: {str(e)}")
        return {"status": "failed", "error": str(e)}

def test_redis_connection() -> Dict[str, Any]:
    """Test Redis connection"""
    print("🔍 Testing Redis connection...")
    
    try:
        # Connect to Redis
        r = redis.Redis(host='localhost', port=6379, db=0, socket_timeout=5)
        
        # Test basic operations
        r.set('test_key', 'test_value')
        value = r.get('test_key')
        
        if value and value.decode('utf-8') == 'test_value':
            print("✅ Redis basic operations working")
            
            # Test ping
            pong = r.ping()
            if pong:
                print("✅ Redis ping successful")
                
                # Clean up test data
                r.delete('test_key')
                
                # Get Redis info
                info = r.info()
                print(f"✅ Redis info retrieved (version: {info.get('redis_version', 'unknown')})")
                
                return {"status": "success", "info": info}
            else:
                print("❌ Redis ping failed")
                return {"status": "failed", "error": "Ping failed"}
        else:
            print("❌ Redis basic operations failed")
            return {"status": "failed", "error": "Basic operations failed"}
            
    except redis.ConnectionError:
        print("❌ Cannot connect to Redis. Is it running on localhost:6379?")
        return {"status": "failed", "error": "Connection refused"}
    except Exception as e:
        print(f"❌ Redis test failed: {str(e)}")
        return {"status": "failed", "error": str(e)}

def test_ollama_connection() -> Dict[str, Any]:
    """Test Ollama connection (optional)"""
    print("🔍 Testing Ollama connection...")
    
    try:
        # Test Ollama API
        response = requests.get("http://localhost:11434/api/tags", timeout=10)
        if response.status_code == 200:
            models = response.json()
            model_names = [model['name'] for model in models.get('models', [])]
            print(f"✅ Ollama connection successful (found {len(model_names)} models)")
            
            # Check for our target model
            if 'llama3.2:1b' in model_names:
                print("✅ Target model 'llama3.2:1b' is available")
                return {"status": "success", "models": model_names, "target_model_available": True}
            else:
                print("⚠️  Target model 'llama3.2:1b' not found")
                return {"status": "partial", "models": model_names, "target_model_available": False}
        else:
            print(f"❌ Ollama API failed with status {response.status_code}")
            return {"status": "failed", "error": f"API failed: {response.status_code}"}
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Cannot connect to Ollama. Is it installed and running?")
        return {"status": "failed", "error": "Connection refused"}
    except requests.exceptions.Timeout:
        print("❌ Ollama connection timeout")
        return {"status": "failed", "error": "Connection timeout"}
    except Exception as e:
        print(f"❌ Ollama test failed: {str(e)}")
        return {"status": "failed", "error": str(e)}

def test_environment_variables() -> Dict[str, Any]:
    """Test environment variable configuration"""
    print("🔍 Testing environment configuration...")
    
    required_vars = [
        'QDRANT_HOST',
        'QDRANT_PORT', 
        'REDIS_HOST',
        'REDIS_PORT',
        'OLLAMA_HOST',
        'OLLAMA_MODEL'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        return {"status": "partial", "missing_vars": missing_vars}
    else:
        print("✅ All required environment variables are set")
        return {"status": "success"}

def main():
    """Run all service tests"""
    print("=" * 50)
    print("ZeroRAG Service Test Suite")
    print("=" * 50)
    
    results = {}
    
    # Test environment variables
    results['environment'] = test_environment_variables()
    print()
    
    # Test Qdrant
    results['qdrant'] = test_qdrant_connection()
    print()
    
    # Test Redis
    results['redis'] = test_redis_connection()
    print()
    
    # Test Ollama (optional)
    results['ollama'] = test_ollama_connection()
    print()
    
    # Summary
    print("=" * 50)
    print("Test Summary")
    print("=" * 50)
    
    critical_services = ['qdrant', 'redis']
    optional_services = ['ollama']
    
    all_critical_passed = True
    for service in critical_services:
        status = results[service]['status']
        if status == 'success':
            print(f"✅ {service.upper()}: PASSED")
        elif status == 'partial':
            print(f"⚠️  {service.upper()}: PARTIAL")
            all_critical_passed = False
        else:
            print(f"❌ {service.upper()}: FAILED")
            all_critical_passed = False
    
    for service in optional_services:
        status = results[service]['status']
        if status == 'success':
            print(f"✅ {service.upper()}: PASSED (optional)")
        elif status == 'partial':
            print(f"⚠️  {service.upper()}: PARTIAL (optional)")
        else:
            print(f"❌ {service.upper()}: FAILED (optional)")
    
    print()
    
    if all_critical_passed:
        print("🎉 All critical services are working!")
        print("You can now proceed with the ZeroRAG application.")
    else:
        print("❌ Some critical services failed.")
        print("Please check the Docker containers and try again.")
        print("Run: docker compose logs -f to view service logs")
    
    return all_critical_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
