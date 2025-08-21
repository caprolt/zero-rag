#!/bin/bash

# ZeroRAG Cloud Deployment Script
# This script automates deployment to various cloud platforms

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="zerorag"
DOCKER_REGISTRY=""
IMAGE_TAG="latest"

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

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        cp env.example .env
    fi
    
    print_success "Prerequisites check completed"
}

# Function to build Docker images
build_images() {
    print_status "Building Docker images..."
    
    # Build production image
    docker build -f Dockerfile.prod -t ${PROJECT_NAME}:${IMAGE_TAG} .
    
    print_success "Docker images built successfully"
}

# Function to deploy to local Docker
deploy_local() {
    print_status "Deploying to local Docker environment..."
    
    # Stop existing containers
    docker-compose -f docker-compose.prod.yml down
    
    # Start services
    docker-compose -f docker-compose.prod.yml up -d
    
    print_success "Local deployment completed"
    print_status "Services available at:"
    print_status "  - API: http://localhost:8000"
    print_status "  - Streamlit UI: http://localhost:8501"
    print_status "  - Qdrant: http://localhost:6333"
    print_status "  - Redis: localhost:6379"
}

# Function to deploy to AWS EC2
deploy_aws() {
    print_status "Deploying to AWS EC2..."
    
    # Check if AWS CLI is installed
    if ! command -v aws &> /dev/null; then
        print_error "AWS CLI is not installed. Please install AWS CLI first."
        exit 1
    fi
    
    # Check if EC2 instance IP is provided
    if [ -z "$EC2_IP" ]; then
        print_error "EC2_IP environment variable is required for AWS deployment"
        print_status "Usage: EC2_IP=your-ec2-ip ./deploy_cloud.sh aws"
        exit 1
    fi
    
    # Check if SSH key is provided
    if [ -z "$SSH_KEY" ]; then
        print_error "SSH_KEY environment variable is required for AWS deployment"
        print_status "Usage: SSH_KEY=path/to/key.pem ./deploy_cloud.sh aws"
        exit 1
    fi
    
    print_status "Deploying to EC2 instance: $EC2_IP"
    
    # Copy files to EC2
    scp -i $SSH_KEY -r . ubuntu@$EC2_IP:/home/ubuntu/$PROJECT_NAME
    
    # Execute deployment commands on EC2
    ssh -i $SSH_KEY ubuntu@$EC2_IP << 'EOF'
        cd /home/ubuntu/zerorag
        
        # Install Docker if not installed
        if ! command -v docker &> /dev/null; then
            sudo apt update
            sudo apt install -y docker.io docker-compose
            sudo usermod -aG docker ubuntu
            newgrp docker
        fi
        
        # Build and deploy
        docker-compose -f docker-compose.prod.yml down
        docker-compose -f docker-compose.prod.yml up -d --build
        
        # Set up firewall
        sudo ufw allow 80
        sudo ufw allow 443
        sudo ufw allow 8000
        sudo ufw allow 8501
        sudo ufw --force enable
    EOF
    
    print_success "AWS deployment completed"
    print_status "Services available at:"
    print_status "  - API: http://$EC2_IP:8000"
    print_status "  - Streamlit UI: http://$EC2_IP:8501"
}

# Function to deploy to Railway
deploy_railway() {
    print_status "Deploying to Railway..."
    
    # Check if Railway CLI is installed
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI is not installed. Please install Railway CLI first."
        print_status "Install with: npm install -g @railway/cli"
        exit 1
    fi
    
    # Login to Railway
    railway login
    
    # Initialize Railway project
    railway init
    
    # Deploy
    railway up
    
    print_success "Railway deployment completed"
}

# Function to deploy to Render
deploy_render() {
    print_status "Deploying to Render..."
    
    print_status "Please follow these steps to deploy to Render:"
    print_status "1. Go to https://render.com and create an account"
    print_status "2. Create a new Web Service"
    print_status "3. Connect your GitHub repository"
    print_status "4. Set the following environment variables:"
    print_status "   - QDRANT_HOST: your-qdrant-host"
    print_status "   - REDIS_HOST: your-redis-host"
    print_status "   - API_HOST: 0.0.0.0"
    print_status "   - API_PORT: 8000"
    print_status "5. Set build command: docker build -f Dockerfile.prod -t zerorag ."
    print_status "6. Set start command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000"
    print_status "7. Deploy!"
    
    print_success "Render deployment instructions provided"
}

# Function to show deployment status
show_status() {
    print_status "Checking deployment status..."
    
    # Check if containers are running
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        print_success "Services are running"
        docker-compose -f docker-compose.prod.yml ps
    else
        print_warning "No services are currently running"
    fi
    
    # Check service health
    print_status "Checking service health..."
    
    # Check API health
    if curl -f http://localhost:8000/health &> /dev/null; then
        print_success "API is healthy"
    else
        print_error "API health check failed"
    fi
    
    # Check Streamlit health
    if curl -f http://localhost:8501 &> /dev/null; then
        print_success "Streamlit UI is healthy"
    else
        print_error "Streamlit UI health check failed"
    fi
}

# Function to show logs
show_logs() {
    print_status "Showing application logs..."
    docker-compose -f docker-compose.prod.yml logs -f
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    docker-compose -f docker-compose.prod.yml down
    print_success "Services stopped"
}

# Function to show help
show_help() {
    echo "ZeroRAG Cloud Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  local     Deploy to local Docker environment"
    echo "  aws       Deploy to AWS EC2 (requires EC2_IP and SSH_KEY env vars)"
    echo "  railway   Deploy to Railway"
    echo "  render    Show instructions for Render deployment"
    echo "  status    Show deployment status"
    echo "  logs      Show application logs"
    echo "  stop      Stop all services"
    echo "  build     Build Docker images"
    echo "  help      Show this help message"
    echo ""
    echo "Environment Variables:"
    echo "  EC2_IP    EC2 instance IP address (for AWS deployment)"
    echo "  SSH_KEY   Path to SSH key file (for AWS deployment)"
    echo ""
    echo "Examples:"
    echo "  $0 local"
    echo "  EC2_IP=1.2.3.4 SSH_KEY=key.pem $0 aws"
    echo "  $0 railway"
}

# Main script logic
case "${1:-help}" in
    "local")
        check_prerequisites
        build_images
        deploy_local
        ;;
    "aws")
        check_prerequisites
        build_images
        deploy_aws
        ;;
    "railway")
        check_prerequisites
        deploy_railway
        ;;
    "render")
        deploy_render
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs
        ;;
    "stop")
        stop_services
        ;;
    "build")
        check_prerequisites
        build_images
        ;;
    "help"|*)
        show_help
        ;;
esac
