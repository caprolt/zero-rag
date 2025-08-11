# ZeroRAG Infrastructure Setup Guide

This document provides detailed instructions for setting up the ZeroRAG infrastructure components.

## 🐳 Docker Services

### Prerequisites

1. **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
   - Download from: https://www.docker.com/products/docker-desktop
   - Ensure Docker is running before proceeding

2. **Docker Compose**
   - Usually included with Docker Desktop
   - For Linux: `sudo apt-get install docker-compose`

### Services Overview

The `docker-compose.yml` file sets up two essential services:

#### 1. Qdrant Vector Database
- **Purpose**: Stores document embeddings for similarity search
- **Port**: 6333 (REST API), 6334 (GRPC API)
- **Data Persistence**: `qdrant_data` volume
- **Health Check**: `http://localhost:6333/collections`

#### 2. Redis Cache
- **Purpose**: Caching embeddings and session data
- **Port**: 6379
- **Data Persistence**: `redis_data` volume
- **Memory Limit**: 256MB with LRU eviction
- **Health Check**: Redis PING command

### Quick Start

1. **Start services**:
   ```bash
   docker compose up -d
   ```

2. **Check status**:
   ```bash
   docker compose ps
   ```

3. **View logs**:
   ```bash
   docker compose logs -f
   ```

4. **Stop services**:
   ```bash
   docker compose down
   ```

### Service Management

#### Starting Services
```bash
# Start in background
docker compose up -d

# Start with logs
docker compose up

# Start specific service
docker compose up -d qdrant
```

#### Stopping Services
```bash
# Stop and remove containers
docker compose down

# Stop and remove volumes (⚠️ WARNING: Data loss)
docker compose down -v

# Stop specific service
docker compose stop qdrant
```

#### Monitoring Services
```bash
# View running containers
docker compose ps

# View service logs
docker compose logs -f qdrant
docker compose logs -f redis

# View resource usage
docker stats
```

#### Data Management
```bash
# Backup Qdrant data
docker run --rm -v zero-rag_qdrant_data:/data -v $(pwd):/backup alpine tar czf /backup/qdrant_backup.tar.gz -C /data .

# Restore Qdrant data
docker run --rm -v zero-rag_qdrant_data:/data -v $(pwd):/backup alpine tar xzf /backup/qdrant_backup.tar.gz -C /data
```

## 🤖 Ollama Setup

### Installation

1. **Download Ollama**:
   - Visit: https://ollama.ai
   - Download for your platform (Windows, macOS, Linux)

2. **Install and Start**:
   ```bash
   # Windows/macOS: Run the installer
   # Linux:
   curl -fsSL https://ollama.ai/install.sh | sh
   ollama serve
   ```

### Model Setup

1. **Download the target model**:
   ```bash
   ollama pull llama3.2:1b
   ```

2. **Verify installation**:
   ```bash
   ollama list
   ```

3. **Test the model**:
   ```bash
   ollama run llama3.2:1b "Hello, how are you?"
   ```

### Alternative Models

If `llama3.2:1b` is too large for your system, try these alternatives:

```bash
# Smaller models (faster, less accurate)
ollama pull llama3.2:1b-instruct-q4_0
ollama pull phi3:mini

# Medium models (balanced)
ollama pull llama3.2:3b
ollama pull mistral:7b-instruct

# Update .env file with your chosen model
OLLAMA_MODEL=llama3.2:1b-instruct-q4_0
```

## 🔧 Development Environment

### Automated Setup

#### Windows (PowerShell)
```powershell
# Run the setup script
.\scripts\setup_dev.ps1

# Skip Ollama check if not needed
.\scripts\setup_dev.ps1 -SkipOllama
```

#### Linux/macOS (Bash)
```bash
# Make script executable
chmod +x scripts/setup_dev.sh

# Run the setup script
./scripts/setup_dev.sh
```

### Manual Setup

1. **Create environment file**:
   ```bash
   cp env.example .env
   # Edit .env with your preferences
   ```

2. **Create directories**:
   ```bash
   mkdir -p data/uploads data/processed data/cache logs
   ```

3. **Install Python dependencies**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   
   pip install -r requirements.txt
   ```

4. **Start Docker services**:
   ```bash
   docker compose up -d
   ```

5. **Test services**:
   ```bash
   python scripts/test_services.py
   ```

## 🧪 Testing Infrastructure

### Service Health Checks

Run the comprehensive test suite:

```bash
python scripts/test_services.py
```

This will test:
- ✅ Qdrant connectivity and API
- ✅ Redis connectivity and operations
- ✅ Ollama connectivity and model availability
- ✅ Environment variable configuration

### Manual Testing

#### Test Qdrant
```bash
# Health check (collections endpoint)
curl http://localhost:6333/collections

# List collections (same as above)
curl http://localhost:6333/collections
```

#### Test Redis
```bash
# Connect to Redis CLI
docker exec -it zero-rag-redis redis-cli

# Test commands
ping
set test "hello"
get test
del test
```

#### Test Ollama
```bash
# List models
curl http://localhost:11434/api/tags

# Test generation
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{"model": "llama3.2:1b", "prompt": "Hello!"}'
```

## 🔍 Troubleshooting

### Common Issues

#### Docker Services Not Starting
```bash
# Check Docker status
docker info

# Check available ports
netstat -an | grep 6333
netstat -an | grep 6379

# Restart Docker Desktop (Windows/macOS)
# or restart Docker service (Linux)
sudo systemctl restart docker
```

#### Qdrant Connection Issues
```bash
# Check Qdrant logs
docker compose logs qdrant

# Check if port is in use
lsof -i :6333

# Restart Qdrant service
docker compose restart qdrant
```

#### Redis Connection Issues
```bash
# Check Redis logs
docker compose logs redis

# Test Redis directly
docker exec -it zero-rag-redis redis-cli ping

# Check memory usage
docker exec -it zero-rag-redis redis-cli info memory
```

#### Ollama Issues
```bash
# Check Ollama status
ollama list

# Restart Ollama service
# Windows/macOS: Restart from system tray
# Linux: systemctl restart ollama

# Check model download
ollama pull llama3.2:1b --verbose
```

### Performance Optimization

#### Memory Usage
- **Qdrant**: Monitor with `docker stats zero-rag-qdrant`
- **Redis**: Limited to 256MB, adjust in docker-compose.yml
- **Ollama**: Model size varies, monitor system memory

#### Storage
- **Qdrant data**: Stored in Docker volume `qdrant_data`
- **Redis data**: Stored in Docker volume `redis_data`
- **Model files**: Stored in Ollama's default location

#### Network
- **Local development**: All services on localhost
- **Production**: Configure external access and security

## 📊 Monitoring

### Service Metrics

#### Qdrant Metrics
```bash
# Collection statistics
curl http://localhost:6333/collections/zero_rag_documents

# Cluster info
curl http://localhost:6333/cluster
```

#### Redis Metrics
```bash
# Redis info
docker exec -it zero-rag-redis redis-cli info

# Memory usage
docker exec -it zero-rag-redis redis-cli info memory

# Connected clients
docker exec -it zero-rag-redis redis-cli client list
```

#### Ollama Metrics
```bash
# Model information
ollama show llama3.2:1b

# Running processes
ollama ps
```

### Log Management

#### View Logs
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f qdrant

# Last 100 lines
docker compose logs --tail=100 qdrant
```

#### Log Rotation
Add to docker-compose.yml for production:
```yaml
services:
  qdrant:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 🔒 Security Considerations

### Development Environment
- Services run on localhost only
- No authentication required
- CORS enabled for development

### Production Environment
- Configure external access with proper authentication
- Use environment variables for sensitive data
- Enable TLS for Qdrant and Redis
- Implement API key authentication
- Configure firewall rules

## 📚 Next Steps

After completing the infrastructure setup:

1. **Proceed to Phase 1.3**: Configuration System
2. **Test the setup**: Run `python scripts/test_services.py`
3. **Start development**: Begin implementing the core services
4. **Monitor performance**: Use the provided monitoring tools

For additional help, refer to:
- [Docker Documentation](https://docs.docker.com/)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Redis Documentation](https://redis.io/documentation)
- [Ollama Documentation](https://ollama.ai/library)
