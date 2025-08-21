# Docker Deployment Guide

This guide covers how to deploy ZeroRAG using Docker containers for both development and production environments.

## 🐳 Overview

ZeroRAG can be deployed using Docker containers that include:

- **Frontend**: Next.js 15 application with TypeScript and Tailwind CSS
- **Backend**: FastAPI Python application
- **Vector Database**: Qdrant for document embeddings
- **Cache**: Redis for session management and caching
- **AI Models**: Ollama for local LLM inference

## 📋 Prerequisites

- Docker Desktop (Windows/macOS) or Docker Engine (Linux)
- Docker Compose
- At least 8GB RAM (for local AI models)
- 10GB+ free disk space

## 🚀 Quick Start

### Production Deployment

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/zero-rag.git
   cd zero-rag
   ```

2. **Run the setup script**
   ```bash
   # Windows (PowerShell):
   .\scripts\docker-setup.ps1
   
   # macOS/Linux:
   ./scripts/docker-setup.sh
   ```

3. **Or run manually**
   ```bash
   docker-compose -f docker-compose.full.yml up --build -d
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Development Deployment

For development with hot reloading:

```bash
docker-compose -f docker-compose.dev.yml up --build -d
```

## 📁 File Structure

```
zero-rag/
├── docker-compose.full.yml      # Production deployment
├── docker-compose.dev.yml       # Development deployment
├── docker-compose.yml           # Infrastructure only
├── Dockerfile.prod              # Production backend
├── Dockerfile.frontend          # Production frontend
├── Dockerfile.backend.dev       # Development backend
├── Dockerfile.frontend.dev      # Development frontend
├── .dockerignore                # Docker build exclusions
├── env.docker                   # Docker environment variables
└── scripts/
    ├── docker-setup.sh          # Linux/macOS setup script
    └── docker-setup.ps1         # Windows setup script
```

## 🔧 Configuration

### Environment Variables

The Docker deployment uses the `env.docker` file with the following key configurations:

```bash
# Database Configuration
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# Ollama Configuration
OLLAMA_HOST=ollama
OLLAMA_PORT=11434
OLLAMA_MODEL=llama3.2:1b

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:3000", "http://frontend:3000"]
```

### Custom Configuration

To customize the deployment:

1. **Copy and modify the environment file**
   ```bash
   cp env.docker .env
   # Edit .env with your settings
   ```

2. **Update Docker Compose**
   ```yaml
   # In docker-compose.full.yml
   backend:
     env_file:
       - .env
   ```

## 🛠️ Management Commands

### View Logs
```bash
# All services
docker-compose -f docker-compose.full.yml logs -f

# Specific service
docker-compose -f docker-compose.full.yml logs -f backend
docker-compose -f docker-compose.full.yml logs -f frontend
```

### Stop Services
```bash
docker-compose -f docker-compose.full.yml down
```

### Restart Services
```bash
docker-compose -f docker-compose.full.yml restart
```

### Update and Rebuild
```bash
# Pull latest changes and rebuild
git pull
docker-compose -f docker-compose.full.yml up --build -d
```

### Clean Up
```bash
# Remove containers and volumes
docker-compose -f docker-compose.full.yml down -v

# Remove all images
docker-compose -f docker-compose.full.yml down --rmi all
```

## 🔍 Health Checks

The Docker setup includes health checks for all services:

- **Qdrant**: Checks collection endpoint
- **Redis**: Pings Redis server
- **Ollama**: Checks API tags endpoint
- **Backend**: Checks health endpoint
- **Frontend**: Checks web server response

Monitor health status:
```bash
docker-compose -f docker-compose.full.yml ps
```

## 📊 Resource Requirements

### Minimum Requirements
- **CPU**: 2 cores
- **RAM**: 8GB
- **Storage**: 10GB
- **Network**: Stable internet connection

### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 16GB+
- **Storage**: 20GB+ SSD
- **Network**: High-speed internet

### Resource Usage Breakdown
- **Ollama**: 4-8GB RAM (model dependent)
- **Qdrant**: 1-2GB RAM
- **Redis**: 256MB RAM
- **Backend**: 1-2GB RAM
- **Frontend**: 512MB RAM

## 🔒 Security Considerations

### Production Security
1. **Use secrets management**
   ```yaml
   # In docker-compose.full.yml
   backend:
     secrets:
       - db_password
       - api_key
   ```

2. **Enable TLS/SSL**
   ```yaml
   # Configure reverse proxy (nginx/traefik)
   # Use Let's Encrypt for certificates
   ```

3. **Network isolation**
   ```yaml
   # Use custom networks
   networks:
     frontend:
       driver: bridge
     backend:
       internal: true
   ```

### Development Security
- Services are exposed for easy debugging
- Use `.env` files for local configuration
- Avoid committing sensitive data

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts**
   ```bash
   # Check what's using the ports
   netstat -tulpn | grep :3000
   netstat -tulpn | grep :8000
   
   # Change ports in docker-compose.yml
   ports:
     - "3001:3000"  # Use different host port
   ```

2. **Memory issues**
   ```bash
   # Check memory usage
   docker stats
   
   # Increase Docker memory limit in Docker Desktop
   ```

3. **Model download issues**
   ```bash
   # Check Ollama logs
   docker-compose -f docker-compose.full.yml logs ollama
   
   # Pull model manually
   docker exec zero-rag-ollama ollama pull llama3.2:1b
   ```

4. **Permission issues**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER data/
   sudo chmod -R 755 data/
   ```

### Debug Mode

Enable debug logging:
```yaml
# In docker-compose.full.yml
backend:
  environment:
    - LOG_LEVEL=DEBUG
    - DEBUG=true
```

### Service Recovery

If a service fails to start:
```bash
# Check service status
docker-compose -f docker-compose.full.yml ps

# Restart specific service
docker-compose -f docker-compose.full.yml restart backend

# Rebuild and restart
docker-compose -f docker-compose.full.yml up --build -d backend
```

## 📈 Scaling

### Horizontal Scaling
```yaml
# Scale backend services
docker-compose -f docker-compose.full.yml up --scale backend=3 -d
```

### Load Balancing
Use a reverse proxy (nginx/traefik) for load balancing:
```yaml
# Example nginx configuration
upstream backend {
    server backend:8000;
    server backend:8001;
    server backend:8002;
}
```

## 🔄 Updates and Maintenance

### Regular Updates
1. **Pull latest code**
   ```bash
   git pull origin main
   ```

2. **Rebuild containers**
   ```bash
   docker-compose -f docker-compose.full.yml up --build -d
   ```

3. **Clean up old images**
   ```bash
   docker image prune -f
   ```

### Backup Strategy
```bash
# Backup data volumes
docker run --rm -v zero-rag_qdrant_data:/data -v $(pwd):/backup alpine tar czf /backup/qdrant_backup.tar.gz -C /data .

# Backup Redis data
docker run --rm -v zero-rag_redis_data:/data -v $(pwd):/backup alpine tar czf /backup/redis_backup.tar.gz -C /data .
```

## 📞 Support

For issues with Docker deployment:

1. Check the logs: `docker-compose -f docker-compose.full.yml logs -f`
2. Verify system requirements
3. Check network connectivity
4. Review the troubleshooting section above
5. Open an issue on GitHub with logs and system information
