# 🚀 Quick Cloud Deployment Guide

Get ZeroRAG running in the cloud in under 15 minutes!

## 🎯 Fastest Options (Ranked by Speed)

### 1. Railway (5 minutes) ⚡
**Best for**: Quick deployment, automatic scaling

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login and deploy
railway login
railway init
railway up
```

**Cost**: $5-20/month
**Pros**: Auto-detects Docker Compose, easy scaling
**Cons**: Limited free tier

### 2. Render (10 minutes) 🎨
**Best for**: Free tier, simple setup

1. Go to [render.com](https://render.com)
2. Connect your GitHub repo
3. Create a new Web Service
4. Set environment variables
5. Deploy!

**Cost**: $0-50/month (free tier available)
**Pros**: Generous free tier, easy UI
**Cons**: Slower cold starts

### 3. DigitalOcean App Platform (12 minutes) 💧
**Best for**: Simple, reliable, good pricing

1. Go to [digitalocean.com](https://digitalocean.com)
2. Create App Platform
3. Connect GitHub repo
4. Configure services
5. Deploy!

**Cost**: $12-50/month
**Pros**: Reliable, good documentation
**Cons**: Less managed services

## 🏗️ Production Options

### AWS (30 minutes) ☁️
**Best for**: Enterprise, scalability, managed services

```bash
# Use our deployment script
EC2_IP=your-ec2-ip SSH_KEY=key.pem ./scripts/deploy_cloud.sh aws
```

**Cost**: $20-200/month
**Pros**: Most comprehensive, managed services
**Cons**: Complex, expensive

### Google Cloud (25 minutes) 🔍
**Best for**: AI/ML workloads, managed Kubernetes

1. Create GKE cluster
2. Deploy with Helm
3. Configure Cloud Storage
4. Set up monitoring

**Cost**: $30-150/month
**Pros**: Great for AI workloads
**Cons**: Learning curve

## 📋 Pre-Deployment Checklist

Before deploying, ensure:

- [ ] Your code is in a GitHub repository
- [ ] Docker Compose works locally
- [ ] Environment variables are configured
- [ ] You have a cloud provider account
- [ ] Domain name (optional but recommended)

## 🔧 Environment Variables

Set these in your cloud platform:

```env
# Required
QDRANT_HOST=your-qdrant-host
REDIS_HOST=your-redis-host
API_HOST=0.0.0.0
API_PORT=8000

# Optional
API_WORKERS=4
API_LOG_LEVEL=info
ENABLE_CORS=true
CORS_ORIGINS=["https://your-domain.com"]
```

## 🚀 One-Click Deploy

### Railway One-Click
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/new?template=https://github.com/yourusername/zero-rag)

### Render One-Click
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

## 📊 Cost Comparison

| Platform | Setup Time | Monthly Cost | Free Tier | Best For |
|----------|------------|--------------|-----------|----------|
| Railway | 5 min | $5-20 | ❌ | Quick deployment |
| Render | 10 min | $0-50 | ✅ | Free tier users |
| DigitalOcean | 12 min | $12-50 | ❌ | Simple production |
| AWS | 30 min | $20-200 | ✅ | Enterprise |
| GCP | 25 min | $30-150 | ✅ | AI workloads |

## 🆘 Troubleshooting

### Common Issues

1. **Port conflicts**
   ```bash
   # Check what's using port 8000
   lsof -i :8000
   ```

2. **Memory issues**
   ```bash
   # Increase swap space
   sudo fallocate -l 4G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   ```

3. **Docker build fails**
   ```bash
   # Clear Docker cache
   docker system prune -a
   ```

### Getting Help

- Check logs: `docker-compose logs`
- Verify environment variables
- Test locally first
- Check cloud provider documentation

## 🎉 Success!

Once deployed, your ZeroRAG will be available at:
- **API**: `https://your-domain.com`
- **Streamlit UI**: `https://your-domain.com:8501`
- **Health Check**: `https://your-domain.com/health`

## 📈 Next Steps

After deployment:
1. Set up a custom domain
2. Configure SSL certificates
3. Set up monitoring
4. Implement backup strategy
5. Configure auto-scaling

---

**Need help?** Check the full deployment guide in `docs/cloud_deployment_guide.md` or open an issue on GitHub!
