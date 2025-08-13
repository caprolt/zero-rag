"""
ZeroRAG FastAPI Backend

This module provides the main FastAPI application with REST API endpoints for
document upload, query processing, health monitoring, and streaming responses.

Phase 6.1 Implementation:
- Complete REST API with streaming support
- Document upload with validation
- Query endpoint with Server-Sent Events
- Health check and monitoring endpoints
- CORS and middleware configuration

Phase 6.2 Implementation:
- Enhanced file upload handling with progress tracking
- Advanced file validation and preprocessing
- Streaming responses with connection management
- Cleanup mechanisms and storage management

Phase 6.3 Implementation:
- Comprehensive API documentation with OpenAPI/Swagger
- Interactive API documentation with examples
- Error documentation and troubleshooting guides
- Rate limiting and security documentation
"""

import logging
import time
from typing import Dict, Any
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from ..config import get_config
from ..services.service_factory import ServiceFactory
from .advanced_features import stream_manager
from .models import ErrorResponse, APIInfo
from .routes import health_router, documents_router, query_router, metrics_router, advanced_router

logger = logging.getLogger(__name__)

# Initialize configuration
config = get_config()


# Create FastAPI application with comprehensive documentation
app = FastAPI(
    title="ZeroRAG API",
    description="""
# ZeroRAG API Documentation

A production-ready Retrieval-Augmented Generation (RAG) system built with free and open-source components.

## 🚀 Features

- **Document Processing**: Upload and process various document formats (PDF, TXT, MD, CSV)
- **Vector Search**: Semantic search using embeddings and vector similarity
- **AI Generation**: Generate answers using local LLMs (Llama2, Mistral, etc.)
- **Streaming Responses**: Real-time streaming with Server-Sent Events (SSE)
- **Health Monitoring**: Comprehensive system health checks and metrics
- **File Validation**: Advanced file validation and preprocessing
- **Progress Tracking**: Real-time upload and processing progress
- **Cleanup Tools**: Document and file cleanup mechanisms

## 📚 API Endpoints

### Health & Monitoring
- `GET /health` - System health check
- `GET /health/services/{service}` - Individual service health
- `GET /metrics` - System metrics and performance data

### Documents
- `POST /documents/upload` - Upload and process documents
- `GET /documents` - List all documents
- `GET /documents/{document_id}` - Get document details
- `DELETE /documents/{document_id}` - Delete document
- `POST /documents/validate` - Validate file before upload
- `GET /documents/upload/{document_id}/progress` - Upload progress tracking

### Query Processing
- `POST /query` - Process RAG queries with streaming support
- `GET /query/stream` - Streaming query endpoint (SSE)

### Advanced Features
- `GET /advanced/connections` - List active streaming connections
- `DELETE /advanced/connections/{connection_id}` - Close streaming connection
- `POST /advanced/cleanup` - Document and file cleanup
- `GET /advanced/storage/stats` - Storage statistics

## 🔧 Configuration

The API can be configured through environment variables or configuration files. See the configuration documentation for details.

## 🛡️ Security

- File validation and security checks
- Content type validation
- Malicious file detection
- Rate limiting (configurable)
- CORS configuration

## 📊 Monitoring

- Real-time health monitoring
- Performance metrics
- Error tracking and reporting
- Service status monitoring

## 🚀 Getting Started

1. **Health Check**: Start by checking system health at `/health`
2. **Upload Documents**: Use `/documents/upload` to add documents to the knowledge base
3. **Query**: Use `/query` to ask questions and get AI-generated answers
4. **Monitor**: Use `/metrics` to monitor system performance

## 📖 Examples

See the interactive documentation at `/docs` for detailed examples and testing.

## 🔗 Related Links

- [Interactive API Documentation](/docs)
- [Alternative Documentation](/redoc)
- [OpenAPI Schema](/openapi.json)
- [Health Check](/health)
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    contact={
        "name": "ZeroRAG API Support",
        "url": "https://github.com/your-repo/zero-rag",
        "email": "support@zerorag.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.zerorag.com",
            "description": "Production server"
        }
    ],
    tags=[
        {
            "name": "Health",
            "description": "Health monitoring and system status endpoints"
        },
        {
            "name": "Documents", 
            "description": "Document upload, management, and processing endpoints"
        },
        {
            "name": "Query",
            "description": "RAG query processing and streaming endpoints"
        },
        {
            "name": "Metrics",
            "description": "System metrics and performance monitoring"
        },
        {
            "name": "Advanced Features",
            "description": "Advanced features including cleanup, connection management, and storage"
        }
    ]
)

# Configure CORS
if config.api.enable_cors:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Mount static files for documentation (commented out for now)
# app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(health_router)
app.include_router(documents_router)
app.include_router(query_router)
app.include_router(metrics_router)
app.include_router(advanced_router)


# Root endpoint
@app.get("/", response_model=APIInfo, tags=["Root"])
async def root():
    """
    Root endpoint providing API information and links.
    
    Returns basic information about the ZeroRAG API including version,
    description, and links to documentation and health endpoints.
    """
    return APIInfo(
        name="ZeroRAG API",
        version="1.0.0",
        description="Production-ready RAG system using free/open-source components",
        docs="/docs",
        health="/health"
    )


# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """
    Handle HTTP exceptions with standardized error responses.
    
    Converts FastAPI HTTPException to standardized ErrorResponse format
    with proper error details and request tracking.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            timestamp=time.time(),
            request_id=getattr(request, 'request_id', None)
        ).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """
    Handle general exceptions with error logging and standardized responses.
    
    Catches all unhandled exceptions, logs them for debugging, and returns
    a standardized error response without exposing internal details.
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            timestamp=time.time(),
            request_id=getattr(request, 'request_id', None)
        ).model_dump()
    )


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """
    Application startup event handler.
    
    Initializes the application, logs configuration, and starts background tasks
    including streaming connection cleanup.
    """
    logger.info("Starting ZeroRAG FastAPI application...")
    logger.info(f"API configuration: {config.api.model_dump()}")
    
    # Start streaming connection cleanup task
    await stream_manager.start_cleanup_task()
    logger.info("Started streaming connection cleanup task")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event handler.
    
    Gracefully shuts down the application, cancels background tasks,
    and cleans up resources.
    """
    logger.info("Shutting down ZeroRAG FastAPI application...")
    
    # Clean up streaming connections
    if stream_manager._cleanup_task and not stream_manager._cleanup_task.done():
        stream_manager._cleanup_task.cancel()
        logger.info("Cancelled streaming connection cleanup task")


# Main entry point
if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=config.api.host,
        port=config.api.port,
        reload=config.api.reload,
        workers=config.api.workers,
        log_level=config.api.log_level
    )
