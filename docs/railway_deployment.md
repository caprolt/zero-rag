# 🚂 Railway Deployment Guide for ZeroRAG

This guide provides step-by-step instructions for deploying ZeroRAG to Railway.

## 🎯 Quick Start (5 minutes)

### Step 1: Prepare Your Repository

Ensure your repository has these files:
- `railway.json` - Railway configuration
- `nixpacks.toml` - Build configuration
- `Procfile` - Start command
- `start_railway.py` - Startup script
- `requirements-railway.txt` - Optimized dependencies

### Step 2: Deploy to Railway

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **Login to Railway**
   ```bash
   railway login
   ```

3. **Initialize Project**
   ```bash
   railway init
   ```

4. **Deploy**
   ```bash
   railway up
   ```

## 🔧 Configuration Files

### railway.json
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python start_railway.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### nixpacks.toml
```toml
[phases.setup]
nixPkgs = ["python3", "gcc", "g++", "curl"]

[phases.install]
cmds = [
  "python -m venv --copies /opt/venv",
  ". /opt/venv/bin/activate && pip install --no-cache-dir -r requirements-railway.txt"
]

[phases.build]
cmds = [
  ". /opt/venv/bin/activate && python -c \"from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')\""
]

[start]
cmd = "python start_railway.py"
```

### Procfile
```
web: python start_railway.py
```

## 🌍 Environment Variables

Set these in your Railway dashboard:

### Required Variables
```env
# Database Configuration
QDRANT_HOST=your-qdrant-host
REDIS_HOST=your-redis-host

# API Configuration
API_HOST=0.0.0.0
API_PORT=$PORT
API_WORKERS=1
API_LOG_LEVEL=info

# CORS Configuration
ENABLE_CORS=true
CORS_ORIGINS=["*"]
```

### Optional Variables
```env
# AI Model Configuration
OLLAMA_HOST=http://your-ollama-host:11434
OLLAMA_MODEL=llama3.2:1b
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2

# Security
API_KEY=your-secure-api-key
RATE_LIMIT_PER_MINUTE=60
```

## 🗄️ Database Setup

### Option 1: Railway Managed Services

1. **Add Redis Service**
   - Go to Railway dashboard
   - Click "New Service" → "Database" → "Redis"
   - Copy the connection URL to `REDIS_HOST`

2. **Add PostgreSQL (for Qdrant)**
   - Go to Railway dashboard
   - Click "New Service" → "Database" → "PostgreSQL"
   - Use this for Qdrant storage

### Option 2: External Services

1. **Redis Cloud**
   - Sign up at [redis.com](https://redis.com)
   - Create a free database
   - Copy connection details

2. **Qdrant Cloud**
   - Sign up at [qdrant.tech](https://qdrant.tech)
   - Create a cluster
   - Copy API endpoint

## 🚀 Deployment Steps

### 1. Connect Repository
```bash
# Link your GitHub repository
railway link
```

### 2. Set Environment Variables
```bash
# Set required variables
railway variables set QDRANT_HOST=your-qdrant-host
railway variables set REDIS_HOST=your-redis-host
railway variables set API_HOST=0.0.0.0
railway variables set API_WORKERS=1
```

### 3. Deploy
```bash
# Deploy to Railway
railway up
```

### 4. Check Status
```bash
# View deployment status
railway status

# View logs
railway logs
```

## 🔍 Troubleshooting

### Common Issues

1. **Build Fails - No Start Command**
   ```
   Error: No start command could be found
   ```
   **Solution**: Ensure you have `railway.json`, `nixpacks.toml`, or `Procfile` with a start command.

2. **Memory Issues**
   ```
   Error: Process exited with code 137 (out of memory)
   ```
   **Solution**: 
   - Upgrade to a larger Railway plan
   - Use CPU-only PyTorch: `torch==2.8.0+cpu`
   - Reduce model size

3. **Dependency Installation Fails**
   ```
   Error: Failed to install requirements
   ```
   **Solution**:
   - Use `requirements-railway.txt` instead of `requirements.txt`
   - Check for version conflicts
   - Use CPU-only versions for large packages

4. **Health Check Fails**
   ```
   Error: Health check failed
   ```
   **Solution**:
   - Ensure `/health` endpoint exists
   - Check application logs
   - Verify environment variables

### Debug Commands

```bash
# View detailed logs
railway logs --tail

# Check service status
railway status

# View environment variables
railway variables

# Connect to service shell
railway shell

# Restart service
railway service restart
```

## 📊 Monitoring

### Railway Dashboard
- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time application logs
- **Deployments**: Deployment history and status

### Health Checks
- **Endpoint**: `/health`
- **Timeout**: 300 seconds
- **Frequency**: Every 30 seconds

## 💰 Cost Optimization

### Free Tier Limits
- **Build Time**: 500 minutes/month
- **Deployments**: Unlimited
- **Bandwidth**: 100GB/month

### Paid Plans
- **Starter**: $5/month
- **Developer**: $20/month
- **Team**: $20/user/month

## 🔄 Continuous Deployment

### Automatic Deployments
Railway automatically deploys when you push to your main branch:

```bash
# Push changes to trigger deployment
git add .
git commit -m "Update application"
git push origin main
```

### Manual Deployments
```bash
# Deploy specific branch
railway up --service=your-service-name

# Deploy from specific commit
railway up --commit=abc123
```

## 🎉 Success!

Once deployed, your ZeroRAG will be available at:
- **URL**: `https://your-app-name.railway.app`
- **Health Check**: `https://your-app-name.railway.app/health`
- **API Docs**: `https://your-app-name.railway.app/docs`

## 📈 Next Steps

1. **Set up custom domain**
   - Go to Railway dashboard
   - Navigate to your service
   - Click "Settings" → "Domains"
   - Add your custom domain

2. **Configure SSL**
   - Railway provides automatic SSL certificates
   - No additional configuration needed

3. **Set up monitoring**
   - Enable Railway monitoring
   - Set up alerts for downtime

4. **Scale up**
   - Monitor resource usage
   - Upgrade plan if needed

---

**Need help?** Check the Railway documentation or open an issue on GitHub!
