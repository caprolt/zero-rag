#!/bin/bash

# ZeroRAG Development Setup Script
# This script sets up the development environment for ZeroRAG

set -e

echo "🚀 Setting up ZeroRAG development environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    print_status "Checking Docker installation..."
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    print_success "Docker is installed and running"
}

# Check if Docker Compose is available
check_docker_compose() {
    print_status "Checking Docker Compose..."
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p data/uploads
    mkdir -p data/processed
    mkdir -p data/cache
    mkdir -p logs
    
    print_success "Directories created"
}

# Copy environment file
setup_environment() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f .env ]; then
        if [ -f env.example ]; then
            cp env.example .env
            print_success "Environment file created from template"
        else
            print_warning "No env.example found. Please create .env file manually."
        fi
    else
        print_success "Environment file already exists"
    fi
}

# Start Docker services
start_services() {
    print_status "Starting Docker services (Qdrant and Redis)..."
    
    # Use docker compose if available, otherwise docker-compose
    if docker compose version &> /dev/null; then
        docker compose up -d
    else
        docker-compose up -d
    fi
    
    print_success "Docker services started"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for Qdrant
    print_status "Waiting for Qdrant..."
    until curl -f http://localhost:6333/collections &> /dev/null; do
        sleep 2
    done
    print_success "Qdrant is ready"
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    until docker exec zero-rag-redis redis-cli ping &> /dev/null; do
        sleep 2
    done
    print_success "Redis is ready"
}

# Check Ollama installation
check_ollama() {
    print_status "Checking Ollama installation..."
    
    if ! command -v ollama &> /dev/null; then
        print_warning "Ollama is not installed. Please install Ollama from https://ollama.ai"
        print_status "After installing Ollama, run: ollama pull llama3.2:1b"
        return 1
    fi
    
    # Check if the model is available
    if ! ollama list | grep -q "llama3.2:1b"; then
        print_status "Downloading llama3.2:1b model..."
        ollama pull llama3.2:1b
    fi
    
    print_success "Ollama is ready with llama3.2:1b model"
}

# Install Python dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    print_success "Python dependencies installed"
}

# Run health checks
health_check() {
    print_status "Running health checks..."
    
    # Test Qdrant connection
    if curl -f http://localhost:6333/collections &> /dev/null; then
        print_success "Qdrant health check passed"
    else
        print_error "Qdrant health check failed"
        return 1
    fi
    
    # Test Redis connection
    if docker exec zero-rag-redis redis-cli ping &> /dev/null; then
        print_success "Redis health check passed"
    else
        print_error "Redis health check failed"
        return 1
    fi
    
    # Test Ollama connection
    if command -v ollama &> /dev/null && ollama list &> /dev/null; then
        print_success "Ollama health check passed"
    else
        print_warning "Ollama health check failed (not critical for development)"
    fi
}

# Main execution
main() {
    echo "=========================================="
    echo "ZeroRAG Development Environment Setup"
    echo "=========================================="
    
    check_docker
    check_docker_compose
    create_directories
    setup_environment
    start_services
    wait_for_services
    check_ollama
    install_dependencies
    health_check
    
    echo ""
    echo "=========================================="
    print_success "Setup completed successfully!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Start the API server: python -m src.api.main"
    echo "2. Start the UI: streamlit run src/ui/streamlit_app.py"
    echo "3. Access the application at http://localhost:8501"
    echo ""
    echo "To stop services: docker compose down"
    echo "To view logs: docker compose logs -f"
}

# Run main function
main "$@"
