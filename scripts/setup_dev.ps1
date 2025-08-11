# ZeroRAG Development Setup Script for Windows
# This script sets up the development environment for ZeroRAG

param(
    [switch]$SkipOllama
)

# Stop on first error
$ErrorActionPreference = "Stop"

Write-Host "🚀 Setting up ZeroRAG development environment..." -ForegroundColor Cyan

# Function to print colored output
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

function Write-Success {
    param([string]$Message)
    Write-Host "[SUCCESS] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if Docker is installed
function Test-Docker {
    Write-Status "Checking Docker installation..."
    
    try {
        $null = docker --version
        $null = docker info
        Write-Success "Docker is installed and running"
    }
    catch {
        Write-Error "Docker is not installed or not running. Please install Docker Desktop first."
        exit 1
    }
}

# Check if Docker Compose is available
function Test-DockerCompose {
    Write-Status "Checking Docker Compose..."
    
    try {
        $null = docker compose version
        Write-Success "Docker Compose is available"
    }
    catch {
        Write-Error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    }
}

# Create necessary directories
function New-Directories {
    Write-Status "Creating necessary directories..."
    
    $directories = @(
        "data/uploads",
        "data/processed", 
        "data/cache",
        "logs"
    )
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }
    
    Write-Success "Directories created"
}

# Copy environment file
function Set-Environment {
    Write-Status "Setting up environment configuration..."
    
    if (!(Test-Path ".env")) {
        if (Test-Path "env.example") {
            Copy-Item "env.example" ".env"
            Write-Success "Environment file created from template"
        }
        else {
            Write-Warning "No env.example found. Please create .env file manually."
        }
    }
    else {
        Write-Success "Environment file already exists"
    }
}

# Start Docker services
function Start-Services {
    Write-Status "Starting Docker services (Qdrant and Redis)..."
    
    try {
        docker compose up -d
        Write-Success "Docker services started"
    }
    catch {
        Write-Error "Failed to start Docker services"
        exit 1
    }
}

# Wait for services to be ready
function Wait-Services {
    Write-Status "Waiting for services to be ready..."
    
    # Wait for Qdrant
    Write-Status "Waiting for Qdrant..."
    $qdrantReady = $false
    $attempts = 0
    $maxAttempts = 30
    
    while (!$qdrantReady -and $attempts -lt $maxAttempts) {
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:6333/collections" -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -eq 200) {
                $qdrantReady = $true
                Write-Success "Qdrant is ready"
            }
        }
        catch {
            $attempts++
            Start-Sleep -Seconds 2
        }
    }
    
    if (!$qdrantReady) {
        Write-Error "Qdrant failed to start within expected time"
        exit 1
    }
    
    # Wait for Redis
    Write-Status "Waiting for Redis..."
    $redisReady = $false
    $attempts = 0
    
    while (!$redisReady -and $attempts -lt $maxAttempts) {
        try {
            $null = docker exec zero-rag-redis redis-cli ping
            $redisReady = $true
            Write-Success "Redis is ready"
        }
        catch {
            $attempts++
            Start-Sleep -Seconds 2
        }
    }
    
    if (!$redisReady) {
        Write-Error "Redis failed to start within expected time"
        exit 1
    }
}

# Check Ollama installation
function Test-Ollama {
    if ($SkipOllama) {
        Write-Warning "Skipping Ollama check as requested"
        return
    }
    
    Write-Status "Checking Ollama installation..."
    
    try {
        $null = ollama --version
        Write-Success "Ollama is installed"
        
        # Check if the model is available
        $models = ollama list
        if ($models -notmatch "llama3.2:1b") {
            Write-Status "Downloading llama3.2:1b model..."
            ollama pull llama3.2:1b
        }
        
        Write-Success "Ollama is ready with llama3.2:1b model"
    }
    catch {
        Write-Warning "Ollama is not installed. Please install Ollama from https://ollama.ai"
        Write-Status "After installing Ollama, run: ollama pull llama3.2:1b"
    }
}

# Install Python dependencies
function Install-Dependencies {
    Write-Status "Installing Python dependencies..."
    
    if (!(Test-Path "venv")) {
        Write-Status "Creating virtual environment..."
        python -m venv venv
    }
    
    # Activate virtual environment
    & "venv\Scripts\Activate.ps1"
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    Write-Success "Python dependencies installed"
}

# Run health checks
function Test-Health {
    Write-Status "Running health checks..."
    
    # Test Qdrant connection
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:6333/collections" -UseBasicParsing -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Success "Qdrant health check passed"
        }
        else {
            Write-Error "Qdrant health check failed"
            return $false
        }
    }
    catch {
        Write-Error "Qdrant health check failed"
        return $false
    }
    
    # Test Redis connection
    try {
        $null = docker exec zero-rag-redis redis-cli ping
        Write-Success "Redis health check passed"
    }
    catch {
        Write-Error "Redis health check failed"
        return $false
    }
    
    # Test Ollama connection
    if (!$SkipOllama) {
        try {
            $null = ollama list
            Write-Success "Ollama health check passed"
        }
        catch {
            Write-Warning "Ollama health check failed (not critical for development)"
        }
    }
    
    return $true
}

# Main execution
function Main {
    Write-Host "==========================================" -ForegroundColor Cyan
    Write-Host "ZeroRAG Development Environment Setup" -ForegroundColor Cyan
    Write-Host "==========================================" -ForegroundColor Cyan
    
    Test-Docker
    Test-DockerCompose
    New-Directories
    Set-Environment
    Start-Services
    Wait-Services
    Test-Ollama
    Install-Dependencies
    
    if (Test-Health) {
        Write-Host ""
        Write-Host "==========================================" -ForegroundColor Green
        Write-Success "Setup completed successfully!"
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Next steps:" -ForegroundColor Yellow
        Write-Host "1. Activate virtual environment: venv\Scripts\Activate.ps1" -ForegroundColor White
        Write-Host "2. Start the API server: python -m src.api.main" -ForegroundColor White
        Write-Host "3. Start the UI: streamlit run src/ui/streamlit_app.py" -ForegroundColor White
        Write-Host "4. Access the application at http://localhost:8501" -ForegroundColor White
        Write-Host ""
        Write-Host "To stop services: docker compose down" -ForegroundColor White
        Write-Host "To view logs: docker compose logs -f" -ForegroundColor White
    }
    else {
        Write-Error "Setup failed during health checks"
        exit 1
    }
}

# Run main function
Main
