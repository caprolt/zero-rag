# ZeroRAG Development Setup Script for Windows
# This script sets up the development environment with proper dependency handling

Write-Host "🚀 Setting up ZeroRAG development environment..." -ForegroundColor Green

# Check if Python is installed
try {
    $pythonVersion = python --version
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
if (Test-Path "venv") {
    Write-Host "📁 Virtual environment already exists. Activating..." -ForegroundColor Yellow
} else {
    Write-Host "🔧 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "🔧 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Upgrade pip and install build tools
Write-Host "🔧 Upgrading pip and installing build tools..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install --upgrade setuptools wheel

# Install numpy and pandas first (with compatible versions)
Write-Host "📦 Installing core numerical libraries..." -ForegroundColor Yellow
python -m pip install "numpy>=1.21.0"
python -m pip install "pandas>=1.5.0"

# Install PyTorch (CPU version for Windows)
Write-Host "🔥 Installing PyTorch..." -ForegroundColor Yellow
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install remaining requirements
Write-Host "📦 Installing remaining dependencies..." -ForegroundColor Yellow
python -m pip install -r requirements.txt

# Create necessary directories
Write-Host "📁 Creating necessary directories..." -ForegroundColor Yellow
$directories = @(
    "data/documents",
    "data/processed", 
    "data/uploads",
    "data/cache",
    "logs"
)

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force
        Write-Host "  ✅ Created: $dir" -ForegroundColor Green
    }
}

# Copy environment file if it doesn't exist
if (!(Test-Path ".env") -and (Test-Path "env.example")) {
    Copy-Item "env.example" ".env"
    Write-Host "✅ Created .env file from template" -ForegroundColor Green
}

Write-Host "🎉 Setup complete! To activate the environment, run:" -ForegroundColor Green
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host ""
Write-Host "To run the application:" -ForegroundColor Green
Write-Host "  python run_streamlit.py" -ForegroundColor Cyan
