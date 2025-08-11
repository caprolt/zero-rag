# ZeroRAG Configuration Guide

This document provides a comprehensive guide to configuring the ZeroRAG system.

## Overview

ZeroRAG uses a centralized configuration system based on Pydantic settings management. All configuration is loaded from environment variables with sensible defaults, making it easy to deploy in different environments.

## Quick Start

1. Copy the example environment file:
   ```bash
   cp env.example .env
   ```

2. Edit `.env` with your specific settings

3. Validate your configuration:
   ```bash
   python scripts/validate_config.py
   ```

## Configuration Sections

### Database Configuration

Controls connections to Qdrant vector database and Redis cache.

| Variable | Default | Description |
|----------|---------|-------------|
| `QDRANT_HOST` | `localhost` | Qdrant server hostname |
| `QDRANT_PORT` | `6333` | Qdrant server port |
| `QDRANT_API_KEY` | (empty) | Qdrant API key (optional) |
| `QDRANT_COLLECTION_NAME` | `zero_rag_documents` | Name of the vector collection |
| `QDRANT_VECTOR_SIZE` | `384` | Dimension of embedding vectors |
| `REDIS_HOST` | `localhost` | Redis server hostname |
| `REDIS_PORT` | `6379` | Redis server port |
| `REDIS_PASSWORD` | (empty) | Redis password (optional) |
| `REDIS_DB` | `0` | Redis database number |
| `REDIS_CACHE_TTL` | `3600` | Cache TTL in seconds |

### AI Model Configuration

Controls the AI models used for embeddings and text generation.

#### Ollama Settings
| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2:1b` | Ollama model name |
| `OLLAMA_TIMEOUT` | `30` | Request timeout in seconds |
| `OLLAMA_MAX_TOKENS` | `2048` | Maximum tokens per response |
| `OLLAMA_TEMPERATURE` | `0.7` | Generation temperature (0.0-2.0) |

#### HuggingFace Fallback Settings
| Variable | Default | Description |
|----------|---------|-------------|
| `HF_MODEL_NAME` | `TheBloke/Llama-3.2-1B-Chat-GGUF` | HuggingFace model name |
| `HF_MODEL_FILE` | `llama-3.2-1b-chat.Q4_K_M.gguf` | Model file name |
| `HF_DEVICE` | `cpu` | Device for model inference |
| `HF_MAX_LENGTH` | `2048` | Maximum sequence length |

#### Embedding Model Settings
| Variable | Default | Description |
|----------|---------|-------------|
| `EMBEDDING_MODEL_NAME` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model name |
| `EMBEDDING_DEVICE` | `cpu` | Device for embeddings |
| `EMBEDDING_BATCH_SIZE` | `32` | Batch size for embedding generation |
| `EMBEDDING_MAX_LENGTH` | `512` | Maximum text length for embeddings |

### API Configuration

Controls the FastAPI server settings and security.

| Variable | Default | Description |
|----------|---------|-------------|
| `API_HOST` | `0.0.0.0` | API server host |
| `API_PORT` | `8000` | API server port |
| `API_WORKERS` | `1` | Number of worker processes |
| `API_RELOAD` | `true` | Enable auto-reload for development |
| `API_LOG_LEVEL` | `info` | API log level |
| `ENABLE_CORS` | `true` | Enable CORS support |
| `CORS_ORIGINS` | `["http://localhost:8501", "http://127.0.0.1:8501"]` | Allowed CORS origins |
| `API_KEY` | (empty) | API key for authentication |
| `RATE_LIMIT_PER_MINUTE` | `60` | Rate limit per minute |

### Document Processing Configuration

Controls how documents are processed and chunked.

| Variable | Default | Description |
|----------|---------|-------------|
| `MAX_FILE_SIZE` | `50MB` | Maximum file size for uploads |
| `SUPPORTED_FORMATS` | `txt,csv,md` | Comma-separated list of supported formats |
| `CHUNK_SIZE` | `1000` | Number of characters per chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between chunks |
| `MAX_CHUNKS_PER_DOCUMENT` | `1000` | Maximum chunks per document |

### RAG Pipeline Configuration

Controls the RAG (Retrieval-Augmented Generation) pipeline behavior.

| Variable | Default | Description |
|----------|---------|-------------|
| `TOP_K_RESULTS` | `5` | Number of top results to retrieve |
| `SIMILARITY_THRESHOLD` | `0.7` | Minimum similarity score (0.0-1.0) |
| `MAX_CONTEXT_LENGTH` | `4000` | Maximum context length for LLM |
| `ENABLE_STREAMING` | `true` | Enable streaming responses |

### Performance Configuration

Controls caching and performance settings.

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_CACHING` | `true` | Enable response caching |
| `CACHE_TTL` | `3600` | Cache TTL in seconds |
| `BATCH_SIZE` | `10` | Batch size for operations |
| `MAX_CONCURRENT_REQUESTS` | `5` | Maximum concurrent requests |

### Logging Configuration

Controls logging behavior and output.

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |
| `LOG_FORMAT` | `json` | Log format (json or text) |
| `LOG_FILE` | `logs/zero_rag.log` | Log file path |
| `ENABLE_DEBUG` | `false` | Enable debug mode |

### Monitoring Configuration

Controls monitoring and metrics collection.

| Variable | Default | Description |
|----------|---------|-------------|
| `ENABLE_METRICS` | `true` | Enable metrics collection |
| `METRICS_PORT` | `9090` | Metrics server port |
| `HEALTH_CHECK_INTERVAL` | `30` | Health check interval in seconds |

### Development Configuration

Controls development-specific settings.

| Variable | Default | Description |
|----------|---------|-------------|
| `DEBUG` | `true` | Enable debug mode |
| `ENVIRONMENT` | `development` | Environment (development, staging, production) |
| `ENABLE_HOT_RELOAD` | `true` | Enable hot reload for development |
| `TEST_MODE` | `false` | Enable test mode |

### Storage Configuration

Controls file storage locations.

| Variable | Default | Description |
|----------|---------|-------------|
| `DATA_DIR` | `./data` | Base data directory |
| `UPLOAD_DIR` | `./data/uploads` | Upload directory |
| `PROCESSED_DIR` | `./data/processed` | Processed documents directory |
| `CACHE_DIR` | `./data/cache` | Cache directory |

## Environment-Specific Configurations

### Development Environment

For local development, use these recommended settings:

```bash
# Development settings
DEBUG=true
ENVIRONMENT=development
ENABLE_HOT_RELOAD=true
API_RELOAD=true
LOG_LEVEL=DEBUG
ENABLE_DEBUG=true

# Local services
QDRANT_HOST=localhost
REDIS_HOST=localhost
OLLAMA_HOST=http://localhost:11434
```

### Production Environment

For production deployment, use these security-focused settings:

```bash
# Production settings
DEBUG=false
ENVIRONMENT=production
ENABLE_HOT_RELOAD=false
API_RELOAD=false
LOG_LEVEL=WARNING
ENABLE_DEBUG=false

# Security
API_KEY=your-secure-api-key
ENABLE_CORS=false
RATE_LIMIT_PER_MINUTE=30

# Performance
BATCH_SIZE=50
MAX_CONCURRENT_REQUESTS=10
```

### Docker Environment

When running in Docker containers:

```bash
# Docker settings
API_HOST=0.0.0.0
QDRANT_HOST=qdrant
REDIS_HOST=redis
OLLAMA_HOST=http://ollama:11434

# Volume mounts
DATA_DIR=/app/data
UPLOAD_DIR=/app/data/uploads
PROCESSED_DIR=/app/data/processed
CACHE_DIR=/app/data/cache
LOG_FILE=/app/logs/zero_rag.log
```

## Configuration Validation

The configuration system includes built-in validation to ensure all settings are valid:

- **Port numbers**: Must be between 1 and 65535
- **Temperature**: Must be between 0.0 and 2.0
- **Similarity threshold**: Must be between 0.0 and 1.0
- **File sizes**: Must be positive values
- **Chunk overlap**: Must be less than chunk size

### Running Validation

```bash
# Validate current configuration
python scripts/validate_config.py

# Validate with custom environment file
python scripts/validate_config.py --env-file .env.production

# Export configuration to JSON
python scripts/validate_config.py --export config.json
```

## Configuration Management

### Loading Configuration in Code

```python
from src.config import get_config

# Get the global configuration instance
config = get_config()

# Access specific settings
qdrant_host = config.database.qdrant_host
api_port = config.api.port
model_name = config.ai_model.ollama_model
```

### Reloading Configuration

```python
from src.config import reload_config

# Reload configuration from environment
config = reload_config()
```

### Configuration Serialization

```python
# Convert configuration to dictionary
config_dict = config.to_dict()

# Get connection strings
connections = config.get_connection_strings()
```

## Troubleshooting

### Common Issues

1. **Configuration not loading**: Ensure `.env` file exists and is in the correct location
2. **Validation errors**: Check that all values are within valid ranges
3. **Directory permissions**: Ensure the application has write permissions to data directories
4. **Service connections**: Verify that Qdrant and Redis are running and accessible

### Debug Mode

Enable debug mode for detailed logging:

```bash
LOG_LEVEL=DEBUG
ENABLE_DEBUG=true
```

### Testing Configuration

Run the test suite to verify configuration:

```bash
python -m pytest tests/test_config.py -v
```

## Best Practices

1. **Environment separation**: Use different `.env` files for different environments
2. **Security**: Never commit sensitive values like API keys to version control
3. **Validation**: Always validate configuration before deployment
4. **Documentation**: Document any custom configuration changes
5. **Backup**: Keep backups of production configuration files

## Migration Guide

When updating configuration:

1. Backup current configuration
2. Update environment variables
3. Run validation script
4. Test in development environment
5. Deploy to production

For major version updates, check the changelog for breaking changes in configuration options.
