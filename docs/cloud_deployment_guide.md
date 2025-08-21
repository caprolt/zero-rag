# 🌐 ZeroRAG Cloud Deployment Guide

This guide provides comprehensive instructions for deploying ZeroRAG to various cloud platforms.

## 📋 Prerequisites

Before deploying, ensure you have:
- Docker and Docker Compose installed locally
- A cloud provider account (AWS, GCP, Azure, etc.)
- Basic knowledge of cloud services
- Your application tested locally

## 🎯 Quick Deployment Options

### Option 1: Railway (Easiest - 10 minutes)

**Best for**: Quick deployment, minimal configuration

1. **Sign up for Railway**
   ```bash
   # Visit https://railway.app and create account
   ```

2. **Deploy from GitHub**
   - Connect your GitHub repository
   - Railway will auto-detect Docker Compose
   - Set environment variables in Railway dashboard

3. **Environment Variables**
   ```env
   QDRANT_HOST=your-railway-qdrant-url
   REDIS_HOST=your-railway-redis-url
   API_HOST=0.0.0.0
   API_PORT=8000
   ```

4. **Cost**: $5-20/month

### Option 2: Render (Simple - 15 minutes)

**Best for**: Free tier available, easy scaling

1. **Create Render Account**
   ```bash
   # Visit https://render.com and sign up
   ```

2. **Deploy Services**
   - **Web Service**: Your FastAPI app
   - **Redis**: Managed Redis service
   - **Background Worker**: For document processing

3. **Dockerfile for Render**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   EXPOSE 8000
   
   CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

4. **Cost**: $0-50/month (free tier available)

## 🏗️ Production Deployment (AWS)

### Step 1: Prepare Your Application

1. **Create Production Dockerfile**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   # Install system dependencies
   RUN apt-get update && apt-get install -y \
       curl \
       && rm -rf /var/lib/apt/lists/*
   
   # Install Python dependencies
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   # Copy application code
   COPY . .
   
   # Create non-root user
   RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
   USER appuser
   
   EXPOSE 8000
   
   CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
   ```

2. **Create docker-compose.prod.yml**
   ```yaml
   version: '3.8'
   
   services:
     app:
       build: .
       ports:
         - "8000:8000"
       environment:
         - QDRANT_HOST=${QDRANT_HOST}
         - REDIS_HOST=${REDIS_HOST}
         - API_HOST=0.0.0.0
         - API_PORT=8000
       depends_on:
         - qdrant
         - redis
       restart: unless-stopped
   
     qdrant:
       image: qdrant/qdrant:latest
       ports:
         - "6333:6333"
       volumes:
         - qdrant_data:/qdrant/storage
       environment:
         - QDRANT__SERVICE__HTTP_PORT=6333
       restart: unless-stopped
   
     redis:
       image: redis:7-alpine
       ports:
         - "6379:6379"
       volumes:
         - redis_data:/data
       command: redis-server --appendonly yes
       restart: unless-stopped
   
   volumes:
     qdrant_data:
     redis_data:
   ```

### Step 2: AWS Deployment

1. **Create EC2 Instance**
   ```bash
   # Launch Ubuntu 22.04 LTS instance
   # Instance type: t3.medium (2 vCPU, 4GB RAM)
   # Storage: 20GB GP3
   ```

2. **Install Docker on EC2**
   ```bash
   # SSH into your EC2 instance
   ssh -i your-key.pem ubuntu@your-ec2-ip
   
   # Install Docker
   sudo apt update
   sudo apt install -y docker.io docker-compose
   sudo usermod -aG docker ubuntu
   ```

3. **Deploy Application**
   ```bash
   # Clone your repository
   git clone https://github.com/yourusername/zero-rag.git
   cd zero-rag
   
   # Create .env file
   cat > .env << EOF
   QDRANT_HOST=localhost
   REDIS_HOST=localhost
   API_HOST=0.0.0.0
   API_PORT=8000
   EOF
   
   # Build and run
   docker-compose -f docker-compose.prod.yml up -d
   ```

4. **Set up Domain and SSL**
   ```bash
   # Install Nginx
   sudo apt install -y nginx certbot python3-certbot-nginx
   
   # Configure Nginx
   sudo nano /etc/nginx/sites-available/zerorag
   ```

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
   
       location / {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   
       location /streamlit {
           proxy_pass http://localhost:8501;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

   ```bash
   # Enable site and get SSL
   sudo ln -s /etc/nginx/sites-available/zerorag /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl reload nginx
   sudo certbot --nginx -d your-domain.com
   ```

### Step 3: Managed Services (Optional)

1. **ElastiCache for Redis**
   ```bash
   # Create Redis cluster in AWS Console
   # Update .env with ElastiCache endpoint
   REDIS_HOST=your-elasticache-endpoint.amazonaws.com
   ```

2. **S3 for Document Storage**
   ```python
   # Add to requirements.txt
   boto3==1.34.0
   
   # Update document processor to use S3
   import boto3
   
   s3_client = boto3.client('s3')
   ```

## 🔧 Environment Configuration

### Production Environment Variables

```env
# Database Configuration
QDRANT_HOST=your-qdrant-host
QDRANT_PORT=6333
QDRANT_API_KEY=your-api-key
QDRANT_COLLECTION_NAME=zero_rag_documents

# Redis Configuration
REDIS_HOST=your-redis-host
REDIS_PORT=6379
REDIS_PASSWORD=your-redis-password
REDIS_CACHE_TTL=3600

# AI Model Configuration
OLLAMA_HOST=http://your-ollama-host:11434
OLLAMA_MODEL=llama3.2:1b
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4
API_LOG_LEVEL=info
ENABLE_CORS=true
CORS_ORIGINS=["https://your-domain.com"]

# Security
API_KEY=your-secure-api-key
RATE_LIMIT_PER_MINUTE=60

# Storage
DOCUMENT_STORAGE_PATH=/app/data/documents
CACHE_STORAGE_PATH=/app/data/cache
```

## 📊 Monitoring and Logging

### 1. Application Monitoring

```python
# Add to src/services/health_monitor.py
import logging
from datetime import datetime

class HealthMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def log_health_check(self):
        self.logger.info(f"Health check at {datetime.now()}")
    
    def log_error(self, error):
        self.logger.error(f"Error: {error}")
```

### 2. CloudWatch Integration (AWS)

```python
# Add to requirements.txt
watchtower==3.0.1

# Configure logging
import watchtower
import logging

logger = logging.getLogger()
logger.addHandler(watchtower.CloudWatchLogHandler(
    log_group_name="zerorag-logs",
    stream_name="application"
))
```

## 🔒 Security Best Practices

### 1. Network Security

```bash
# Configure security groups (AWS)
# Allow only necessary ports:
# - 80 (HTTP)
# - 443 (HTTPS)
# - 22 (SSH) - restrict to your IP
```

### 2. Application Security

```python
# Add rate limiting
from fastapi import HTTPException, Depends
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/query")
@limiter.limit("60/minute")
async def query_documents(request: Request):
    # Your query logic
    pass
```

### 3. Environment Security

```bash
# Use AWS Secrets Manager
aws secretsmanager create-secret \
    --name "zerorag-secrets" \
    --description "ZeroRAG application secrets" \
    --secret-string '{"API_KEY":"your-key","REDIS_PASSWORD":"your-password"}'
```

## 💰 Cost Optimization

### 1. Instance Sizing

| Use Case | Instance Type | RAM | Cost/Month |
|----------|---------------|-----|------------|
| Development | t3.micro | 1GB | $8 |
| Small Production | t3.small | 2GB | $16 |
| Medium Production | t3.medium | 4GB | $32 |
| Large Production | t3.large | 8GB | $64 |

### 2. Storage Optimization

```bash
# Use EBS GP3 for better performance/cost ratio
# Enable compression for document storage
# Implement document cleanup policies
```

### 3. Auto Scaling

```yaml
# docker-compose with auto-scaling
version: '3.8'
services:
  app:
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

## 🚀 Deployment Checklist

- [ ] Application tested locally
- [ ] Docker images built and tested
- [ ] Environment variables configured
- [ ] Database migrations completed
- [ ] SSL certificates installed
- [ ] Monitoring configured
- [ ] Backup strategy implemented
- [ ] Security groups configured
- [ ] Load testing completed
- [ ] Documentation updated

## 🆘 Troubleshooting

### Common Issues

1. **Memory Issues**
   ```bash
   # Monitor memory usage
   docker stats
   
   # Increase swap if needed
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

2. **Connection Issues**
   ```bash
   # Check service connectivity
   docker-compose ps
   docker-compose logs app
   
   # Test database connections
   curl http://localhost:6333/collections
   redis-cli ping
   ```

3. **Performance Issues**
   ```bash
   # Monitor resource usage
   htop
   iotop
   
   # Check application logs
   docker-compose logs -f app
   ```

## 📞 Support

For deployment issues:
1. Check the logs: `docker-compose logs`
2. Verify environment variables
3. Test connectivity between services
4. Review security group configurations
5. Check resource usage and limits

---

**Next Steps**: Choose your preferred deployment option and follow the step-by-step instructions above. For production deployments, we recommend starting with AWS or GCP for their managed services and reliability.
