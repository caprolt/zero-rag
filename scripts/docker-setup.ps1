# ZeroRAG Docker Setup Script for Windows
# This script helps you set up and run ZeroRAG with Docker

Write-Host "🚀 ZeroRAG Docker Setup" -ForegroundColor Green
Write-Host "========================" -ForegroundColor Green

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    Write-Host "   Visit: https://docs.docker.com/desktop/install/windows/" -ForegroundColor Yellow
    exit 1
}

# Check if Docker Compose is installed
try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not installed. Please install Docker Compose first." -ForegroundColor Red
    Write-Host "   Visit: https://docs.docker.com/compose/install/" -ForegroundColor Yellow
    exit 1
}

# Create necessary directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Blue
New-Item -ItemType Directory -Force -Path "data\documents" | Out-Null
New-Item -ItemType Directory -Force -Path "data\cache" | Out-Null
New-Item -ItemType Directory -Force -Path "data\uploads" | Out-Null
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

Write-Host "🔧 Building and starting ZeroRAG services..." -ForegroundColor Blue
Write-Host "   This may take several minutes on first run..." -ForegroundColor Yellow

# Build and start all services
docker-compose -f docker-compose.full.yml up --build -d

Write-Host ""
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

# Check service health
Write-Host "🔍 Checking service health..." -ForegroundColor Blue

# Check Qdrant
try {
    Invoke-WebRequest -Uri "http://localhost:6333/collections" -UseBasicParsing | Out-Null
    Write-Host "✅ Qdrant is running on http://localhost:6333" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Qdrant is starting up..." -ForegroundColor Yellow
}

# Check Redis
try {
    docker exec zero-rag-redis redis-cli ping | Out-Null
    Write-Host "✅ Redis is running on localhost:6379" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Redis is starting up..." -ForegroundColor Yellow
}

# Check Ollama
try {
    Invoke-WebRequest -Uri "http://localhost:11434/api/tags" -UseBasicParsing | Out-Null
    Write-Host "✅ Ollama is running on http://localhost:11434" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Ollama is starting up..." -ForegroundColor Yellow
}

# Check Backend
try {
    Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing | Out-Null
    Write-Host "✅ Backend API is running on http://localhost:8000" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Backend API is starting up..." -ForegroundColor Yellow
}

# Check Frontend
try {
    Invoke-WebRequest -Uri "http://localhost:3000" -UseBasicParsing | Out-Null
    Write-Host "✅ Frontend is running on http://localhost:3000" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Frontend is starting up..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 ZeroRAG is starting up!" -ForegroundColor Green
Write-Host ""
Write-Host "📱 Access your application:" -ForegroundColor Cyan
Write-Host "   Frontend (Next.js): http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API:        http://localhost:8000" -ForegroundColor White
Write-Host "   API Documentation:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "🔧 Management commands:" -ForegroundColor Cyan
Write-Host "   View logs:          docker-compose -f docker-compose.full.yml logs -f" -ForegroundColor White
Write-Host "   Stop services:      docker-compose -f docker-compose.full.yml down" -ForegroundColor White
Write-Host "   Restart services:   docker-compose -f docker-compose.full.yml restart" -ForegroundColor White
Write-Host ""
Write-Host "📚 Next steps:" -ForegroundColor Cyan
Write-Host "   1. Wait a few minutes for all services to fully start" -ForegroundColor White
Write-Host "   2. Open http://localhost:3000 in your browser" -ForegroundColor White
Write-Host "   3. Upload some documents to get started" -ForegroundColor White
Write-Host ""
Write-Host "⚠️  Note: On first run, Ollama will download the LLM model (~1GB)" -ForegroundColor Yellow
Write-Host "   This may take several minutes depending on your internet connection." -ForegroundColor Yellow
