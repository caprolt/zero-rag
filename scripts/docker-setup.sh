#!/bin/bash

# ZeroRAG Docker Setup Script
# This script helps you set up and run ZeroRAG with Docker

set -e

echo "🚀 ZeroRAG Docker Setup"
echo "========================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "   Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/documents data/cache data/uploads logs

# Set proper permissions
chmod 755 data logs

echo "🔧 Building and starting ZeroRAG services..."
echo "   This may take several minutes on first run..."

# Build and start all services
docker-compose -f docker-compose.full.yml up --build -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 30

# Check service health
echo "🔍 Checking service health..."

# Check Qdrant
if curl -f http://localhost:6333/collections > /dev/null 2>&1; then
    echo "✅ Qdrant is running on http://localhost:6333"
else
    echo "⚠️  Qdrant is starting up..."
fi

# Check Redis
if docker exec zero-rag-redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running on localhost:6379"
else
    echo "⚠️  Redis is starting up..."
fi

# Check Ollama
if curl -f http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama is running on http://localhost:11434"
else
    echo "⚠️  Ollama is starting up..."
fi

# Check Backend
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is running on http://localhost:8000"
else
    echo "⚠️  Backend API is starting up..."
fi

# Check Frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running on http://localhost:3000"
else
    echo "⚠️  Frontend is starting up..."
fi

echo ""
echo "🎉 ZeroRAG is starting up!"
echo ""
echo "📱 Access your application:"
echo "   Frontend (Next.js): http://localhost:3000"
echo "   Backend API:        http://localhost:8000"
echo "   API Documentation:  http://localhost:8000/docs"
echo ""
echo "🔧 Management commands:"
echo "   View logs:          docker-compose -f docker-compose.full.yml logs -f"
echo "   Stop services:      docker-compose -f docker-compose.full.yml down"
echo "   Restart services:   docker-compose -f docker-compose.full.yml restart"
echo ""
echo "📚 Next steps:"
echo "   1. Wait a few minutes for all services to fully start"
echo "   2. Open http://localhost:3000 in your browser"
echo "   3. Upload some documents to get started"
echo ""
echo "⚠️  Note: On first run, Ollama will download the LLM model (~1GB)"
echo "   This may take several minutes depending on your internet connection."
