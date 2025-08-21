#!/usr/bin/env python3
"""
Railway startup script for ZeroRAG
Handles environment setup and application startup
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Set up environment variables for Railway"""
    # Set default values for Railway
    os.environ.setdefault('API_HOST', '0.0.0.0')
    os.environ.setdefault('API_PORT', os.environ.get('PORT', '8000'))
    os.environ.setdefault('API_WORKERS', '1')  # Railway works better with single worker
    os.environ.setdefault('API_LOG_LEVEL', 'info')
    os.environ.setdefault('ENABLE_CORS', 'true')
    os.environ.setdefault('CORS_ORIGINS', '["*"]')
    
    # Set default database hosts (will be overridden by Railway environment variables)
    os.environ.setdefault('QDRANT_HOST', 'localhost')
    os.environ.setdefault('REDIS_HOST', 'localhost')
    
    logger.info("Environment variables configured")

def check_dependencies():
    """Check if required dependencies are available"""
    try:
        import fastapi
        import uvicorn
        import sentence_transformers
        logger.info("All required dependencies are available")
        return True
    except ImportError as e:
        logger.error(f"Missing dependency: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = [
        'data/documents',
        'data/cache',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {directory}")

def start_application():
    """Start the FastAPI application"""
    port = os.environ.get('PORT', '8000')
    host = os.environ.get('API_HOST', '0.0.0.0')
    
    logger.info(f"Starting ZeroRAG on {host}:{port}")
    
    # Start uvicorn
    cmd = [
        sys.executable, '-m', 'uvicorn',
        'src.api.main:app',
        '--host', host,
        '--port', port,
        '--workers', '1'
    ]
    
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
        sys.exit(0)

def main():
    """Main startup function"""
    logger.info("Starting ZeroRAG Railway deployment...")
    
    # Setup
    setup_environment()
    create_directories()
    
    if not check_dependencies():
        logger.error("Dependency check failed")
        sys.exit(1)
    
    # Start application
    start_application()

if __name__ == "__main__":
    main()
