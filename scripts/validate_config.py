#!/usr/bin/env python3
"""
ZeroRAG Configuration Validation Script

This script validates the configuration system and ensures all settings are correct.
Run this script to verify your configuration before starting the application.
"""

import os
import sys
import json
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import Config, get_config


def validate_configuration():
    """Validate the complete configuration system."""
    print("🔧 ZeroRAG Configuration Validation")
    print("=" * 50)
    
    try:
        # Load configuration
        print("📋 Loading configuration...")
        config = get_config()
        
        # Validate configuration
        print("✅ Validating configuration...")
        if not config.validate():
            print("❌ Configuration validation failed!")
            return False
        
        print("✅ Configuration validation passed!")
        
        # Display configuration summary
        print("\n📊 Configuration Summary:")
        print("-" * 30)
        
        # Database configuration
        print(f"🗄️  Database:")
        print(f"   Qdrant: {config.database.qdrant_host}:{config.database.qdrant_port}")
        print(f"   Redis: {config.database.redis_host}:{config.database.redis_port}")
        print(f"   Vector Size: {config.database.qdrant_vector_size}")
        
        # AI Model configuration
        print(f"\n🤖 AI Models:")
        print(f"   Ollama: {config.ai_model.ollama_host}")
        print(f"   Model: {config.ai_model.ollama_model}")
        print(f"   Embeddings: {config.ai_model.embedding_model_name}")
        print(f"   Device: {config.ai_model.embedding_device}")
        
        # API configuration
        print(f"\n🌐 API:")
        print(f"   Host: {config.api.host}")
        print(f"   Port: {config.api.port}")
        print(f"   CORS: {'Enabled' if config.api.enable_cors else 'Disabled'}")
        print(f"   Rate Limit: {config.api.rate_limit_per_minute}/min")
        
        # Document processing
        print(f"\n📄 Document Processing:")
        print(f"   Max File Size: {config.document.max_file_size}")
        print(f"   Supported Formats: {', '.join(config.document.supported_formats)}")
        print(f"   Chunk Size: {config.document.chunk_size}")
        print(f"   Chunk Overlap: {config.document.chunk_overlap}")
        
        # RAG configuration
        print(f"\n🔍 RAG Pipeline:")
        print(f"   Top K Results: {config.rag.top_k_results}")
        print(f"   Similarity Threshold: {config.rag.similarity_threshold}")
        print(f"   Max Context Length: {config.rag.max_context_length}")
        print(f"   Streaming: {'Enabled' if config.rag.enable_streaming else 'Disabled'}")
        
        # Performance configuration
        print(f"\n⚡ Performance:")
        print(f"   Caching: {'Enabled' if config.performance.enable_caching else 'Disabled'}")
        print(f"   Cache TTL: {config.performance.cache_ttl}s")
        print(f"   Batch Size: {config.performance.batch_size}")
        print(f"   Max Concurrent Requests: {config.performance.max_concurrent_requests}")
        
        # Logging configuration
        print(f"\n📝 Logging:")
        print(f"   Level: {config.logging.level}")
        print(f"   Format: {config.logging.format}")
        print(f"   Log File: {config.logging.log_file}")
        print(f"   Debug Mode: {'Enabled' if config.logging.enable_debug else 'Disabled'}")
        
        # Development configuration
        print(f"\n🛠️  Development:")
        print(f"   Environment: {config.development.environment}")
        print(f"   Debug Mode: {'Enabled' if config.development.debug else 'Disabled'}")
        print(f"   Hot Reload: {'Enabled' if config.development.enable_hot_reload else 'Disabled'}")
        print(f"   Test Mode: {'Enabled' if config.development.test_mode else 'Disabled'}")
        
        # Storage configuration
        print(f"\n💾 Storage:")
        print(f"   Data Directory: {config.storage.data_dir}")
        print(f"   Upload Directory: {config.storage.upload_dir}")
        print(f"   Processed Directory: {config.storage.processed_dir}")
        print(f"   Cache Directory: {config.storage.cache_dir}")
        
        # Connection strings
        print(f"\n🔗 Connection Strings:")
        connections = config.get_connection_strings()
        for service, connection in connections.items():
            print(f"   {service.title()}: {connection}")
        
        # Check directory existence
        print(f"\n📁 Directory Status:")
        directories = [
            config.storage.data_dir,
            config.storage.upload_dir,
            config.storage.processed_dir,
            config.storage.cache_dir,
            os.path.dirname(config.logging.log_file) if config.logging.log_file else None
        ]
        
        for directory in directories:
            if directory:
                if os.path.exists(directory):
                    print(f"   ✅ {directory}")
                else:
                    print(f"   ❌ {directory} (will be created)")
        
        # Environment-specific recommendations
        print(f"\n💡 Recommendations:")
        if config.development.environment == "development":
            print("   - Development mode is enabled")
            print("   - Consider setting DEBUG=false for production")
        elif config.development.environment == "production":
            print("   - Production mode detected")
            print("   - Ensure all security settings are configured")
            print("   - Consider enabling API key authentication")
        
        if not config.api.api_key:
            print("   - No API key configured (optional for development)")
        
        if config.logging.enable_debug:
            print("   - Debug logging is enabled (consider disabling for production)")
        
        print("\n✅ Configuration validation completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")
        return False


def export_configuration(output_file: str = None):
    """Export configuration to JSON file."""
    try:
        config = get_config()
        config_dict = config.to_dict()
        
        if output_file:
            with open(output_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            print(f"✅ Configuration exported to {output_file}")
        else:
            print(json.dumps(config_dict, indent=2))
        
        return True
    except Exception as e:
        print(f"❌ Failed to export configuration: {e}")
        return False


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ZeroRAG Configuration Validation")
    parser.add_argument("--export", "-e", help="Export configuration to JSON file")
    parser.add_argument("--env-file", help="Path to environment file")
    
    args = parser.parse_args()
    
    # Set environment file if provided
    if args.env_file:
        os.environ["ENV_FILE"] = args.env_file
    
    # Validate configuration
    success = validate_configuration()
    
    # Export if requested
    if args.export:
        export_configuration(args.export)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
