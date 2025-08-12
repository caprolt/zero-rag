"""
ZeroRAG API Models

This module contains all Pydantic models used by the FastAPI endpoints for
request/response validation and serialization.

All models include comprehensive documentation, examples, and validation rules
for optimal OpenAPI documentation generation.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class UploadStatus(str, Enum):
    """Upload status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StreamChunkType(str, Enum):
    """Streaming chunk type enumeration."""
    CONTENT = "content"
    SOURCES = "sources"
    PROGRESS = "progress"
    ERROR = "error"
    END = "end"


class HealthResponse(BaseModel):
    """Health check response model.
    
    Provides comprehensive system health information including individual service status,
    uptime, and overall system health.
    """
    status: str = Field(
        description="Overall system status",
        example="healthy",
        enum=["healthy", "degraded", "unhealthy"]
    )
    timestamp: float = Field(
        description="Health check timestamp (Unix timestamp)",
        example=1703123456.789
    )
    services: Dict[str, Dict[str, Any]] = Field(
        description="Individual service status information",
        example={
            "document_processor": {
                "status": "healthy",
                "last_check": 1703123456.789,
                "error_count": 0,
                "health_data": {"queue_size": 0}
            },
            "vector_store": {
                "status": "healthy", 
                "last_check": 1703123456.789,
                "error_count": 0,
                "health_data": {"document_count": 150}
            }
        }
    )
    uptime: float = Field(
        description="System uptime in seconds",
        example=3600.5
    )
    version: str = Field(
        default="1.0.0",
        description="API version",
        example="1.0.0"
    )

    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": 1703123456.789,
                "services": {
                    "document_processor": {
                        "status": "healthy",
                        "last_check": 1703123456.789,
                        "error_count": 0,
                        "health_data": {"queue_size": 0}
                    },
                    "vector_store": {
                        "status": "healthy",
                        "last_check": 1703123456.789,
                        "error_count": 0,
                        "health_data": {"document_count": 150}
                    },
                    "llm_service": {
                        "status": "healthy",
                        "last_check": 1703123456.789,
                        "error_count": 0,
                        "health_data": {"model_loaded": True}
                    }
                },
                "uptime": 3600.5,
                "version": "1.0.0"
            }
        }


class QueryRequest(BaseModel):
    """Query request model.
    
    Defines the parameters for RAG query processing including search configuration,
    response generation settings, and safety controls.
    """
    query: str = Field(
        ...,
        description="User query text to process",
        min_length=1,
        max_length=1000,
        example="What are the key features of our product?"
    )
    top_k: int = Field(
        default=5,
        description="Number of most relevant documents to retrieve",
        ge=1,
        le=20,
        example=5
    )
    score_threshold: float = Field(
        default=0.7,
        description="Minimum similarity score for document retrieval (0.0-1.0)",
        ge=0.0,
        le=1.0,
        example=0.7
    )
    max_context_length: int = Field(
        default=4000,
        description="Maximum context length for LLM processing",
        ge=1000,
        le=8000,
        example=4000
    )
    temperature: float = Field(
        default=0.7,
        description="Response creativity/randomness (0.0-2.0, higher = more creative)",
        ge=0.0,
        le=2.0,
        example=0.7
    )
    max_tokens: int = Field(
        default=1024,
        description="Maximum number of tokens in response",
        ge=100,
        le=4096,
        example=1024
    )
    include_sources: bool = Field(
        default=True,
        description="Include source documents in response",
        example=True
    )
    response_format: Optional[str] = Field(
        default="text",
        description="Response format preference",
        example="text",
        enum=["text", "json", "bullet_points", "table"]
    )
    safety_level: str = Field(
        default="standard",
        description="Content safety filtering level",
        example="standard",
        enum=["standard", "conservative", "permissive"]
    )

    class Config:
        schema_extra = {
            "example": {
                "query": "What are the key features of our product?",
                "top_k": 5,
                "score_threshold": 0.7,
                "max_context_length": 4000,
                "temperature": 0.7,
                "max_tokens": 1024,
                "include_sources": True,
                "response_format": "text",
                "safety_level": "standard"
            }
        }


class QueryResponse(BaseModel):
    """Query response model.
    
    Contains the generated answer, source documents, and processing metadata.
    """
    answer: str = Field(
        description="Generated answer to the query",
        example="Our product offers several key features including..."
    )
    sources: List[Dict[str, Any]] = Field(
        description="Source documents used for answer generation",
        example=[
            {
                "document_id": "doc_123",
                "filename": "product_manual.pdf",
                "content": "The product features include...",
                "score": 0.95,
                "page": 5
            }
        ]
    )
    response_time: float = Field(
        description="Total response time in seconds",
        example=2.34
    )
    tokens_used: Optional[int] = Field(
        description="Number of tokens used in generation",
        example=450
    )
    metadata: Dict[str, Any] = Field(
        description="Additional processing metadata",
        example={
            "documents_retrieved": 5,
            "context_length": 3200,
            "model_used": "llama2-7b"
        }
    )

    class Config:
        schema_extra = {
            "example": {
                "answer": "Our product offers several key features including advanced AI capabilities, real-time processing, and comprehensive analytics. The system is designed for scalability and ease of use.",
                "sources": [
                    {
                        "document_id": "doc_123",
                        "filename": "product_manual.pdf",
                        "content": "The product features include advanced AI capabilities...",
                        "score": 0.95,
                        "page": 5
                    },
                    {
                        "document_id": "doc_124",
                        "filename": "technical_specs.pdf",
                        "content": "Real-time processing capabilities...",
                        "score": 0.87,
                        "page": 12
                    }
                ],
                "response_time": 2.34,
                "tokens_used": 450,
                "metadata": {
                    "documents_retrieved": 5,
                    "context_length": 3200,
                    "model_used": "llama2-7b"
                }
            }
        }


class DocumentUploadResponse(BaseModel):
    """Document upload response model.
    
    Provides information about the uploaded document including processing results
    and metadata.
    """
    document_id: str = Field(
        description="Unique document identifier",
        example="doc_abc123def456"
    )
    filename: str = Field(
        description="Original filename",
        example="product_manual.pdf"
    )
    file_size: int = Field(
        description="File size in bytes",
        example=2048576
    )
    chunks_created: int = Field(
        description="Number of text chunks created during processing",
        example=25
    )
    processing_time: float = Field(
        description="Total processing time in seconds",
        example=3.45
    )
    status: str = Field(
        description="Processing status",
        example="completed",
        enum=["pending", "processing", "completed", "failed", "cancelled"]
    )
    metadata: Dict[str, Any] = Field(
        description="Document metadata and processing information",
        example={
            "file_type": "pdf",
            "pages": 15,
            "language": "en",
            "processing_steps": ["upload", "validation", "parsing", "chunking", "embedding", "storage"]
        }
    )

    class Config:
        schema_extra = {
            "example": {
                "document_id": "doc_abc123def456",
                "filename": "product_manual.pdf",
                "file_size": 2048576,
                "chunks_created": 25,
                "processing_time": 3.45,
                "status": "completed",
                "metadata": {
                    "file_type": "pdf",
                    "pages": 15,
                    "language": "en",
                    "processing_steps": ["upload", "validation", "parsing", "chunking", "embedding", "storage"]
                }
            }
        }


class UploadProgressResponse(BaseModel):
    """Upload progress response model.
    
    Provides real-time progress information for document upload and processing.
    """
    document_id: str = Field(
        description="Unique document identifier",
        example="doc_abc123def456"
    )
    status: UploadStatus = Field(
        description="Current upload status",
        example="processing"
    )
    progress: float = Field(
        description="Progress percentage (0-100)",
        ge=0.0,
        le=100.0,
        example=75.5
    )
    current_step: str = Field(
        description="Current processing step",
        example="embedding"
    )
    estimated_time_remaining: Optional[float] = Field(
        description="Estimated time remaining in seconds",
        example=15.2
    )
    error_message: Optional[str] = Field(
        description="Error message if processing failed",
        example=None
    )
    metadata: Dict[str, Any] = Field(
        description="Additional progress metadata",
        example={
            "steps_completed": ["upload", "validation", "parsing", "chunking"],
            "current_step_progress": 60.0,
            "total_steps": 6
        }
    )

    class Config:
        schema_extra = {
            "example": {
                "document_id": "doc_abc123def456",
                "status": "processing",
                "progress": 75.5,
                "current_step": "embedding",
                "estimated_time_remaining": 15.2,
                "error_message": None,
                "metadata": {
                    "steps_completed": ["upload", "validation", "parsing", "chunking"],
                    "current_step_progress": 60.0,
                    "total_steps": 6
                }
            }
        }


class FileValidationRequest(BaseModel):
    """File validation request model.
    
    Used to validate files before upload to check compatibility and estimate processing time.
    """
    filename: str = Field(
        description="File name to validate",
        example="document.pdf"
    )
    file_size: int = Field(
        description="File size in bytes",
        example=1048576
    )
    content_type: Optional[str] = Field(
        description="File content type (MIME type)",
        example="application/pdf"
    )

    class Config:
        schema_extra = {
            "example": {
                "filename": "document.pdf",
                "file_size": 1048576,
                "content_type": "application/pdf"
            }
        }


class FileValidationResponse(BaseModel):
    """File validation response model.
    
    Provides validation results including errors, warnings, and processing estimates.
    """
    is_valid: bool = Field(
        description="Whether the file is valid for processing",
        example=True
    )
    errors: List[str] = Field(
        description="Validation errors that prevent processing",
        example=[]
    )
    warnings: List[str] = Field(
        description="Validation warnings that don't prevent processing",
        example=["Large file size may take longer to process"]
    )
    estimated_processing_time: Optional[float] = Field(
        description="Estimated processing time in seconds",
        example=45.2
    )
    supported_features: List[str] = Field(
        description="Supported features for this file type",
        example=["text_extraction", "metadata_extraction", "chunking", "embedding"]
    )

    class Config:
        schema_extra = {
            "example": {
                "is_valid": True,
                "errors": [],
                "warnings": ["Large file size may take longer to process"],
                "estimated_processing_time": 45.2,
                "supported_features": ["text_extraction", "metadata_extraction", "chunking", "embedding"]
            }
        }


class DocumentInfo(BaseModel):
    """Document information model.
    
    Provides metadata about a stored document.
    """
    document_id: str = Field(
        description="Unique document identifier",
        example="doc_abc123def456"
    )
    filename: str = Field(
        description="Original filename",
        example="product_manual.pdf"
    )
    file_size: int = Field(
        description="File size in bytes",
        example=2048576
    )
    upload_timestamp: float = Field(
        description="Upload timestamp (Unix timestamp)",
        example=1703123456.789
    )
    chunks_count: int = Field(
        description="Number of text chunks",
        example=25
    )
    status: str = Field(
        description="Document status",
        example="active",
        enum=["active", "archived", "deleted", "processing", "failed"]
    )
    metadata: Dict[str, Any] = Field(
        description="Document metadata",
        example={
            "file_type": "pdf",
            "pages": 15,
            "language": "en",
            "uploaded_by": "user123"
        }
    )

    class Config:
        schema_extra = {
            "example": {
                "document_id": "doc_abc123def456",
                "filename": "product_manual.pdf",
                "file_size": 2048576,
                "upload_timestamp": 1703123456.789,
                "chunks_count": 25,
                "status": "active",
                "metadata": {
                    "file_type": "pdf",
                    "pages": 15,
                    "language": "en",
                    "uploaded_by": "user123"
                }
            }
        }


class DocumentListResponse(BaseModel):
    """Document list response model.
    
    Provides paginated list of documents with metadata.
    """
    documents: List[DocumentInfo] = Field(
        description="List of documents"
    )
    total: int = Field(
        description="Total number of documents",
        example=150
    )
    limit: int = Field(
        description="Requested limit",
        example=20
    )
    offset: int = Field(
        description="Requested offset",
        example=0
    )

    class Config:
        schema_extra = {
            "example": {
                "documents": [
                    {
                        "document_id": "doc_abc123def456",
                        "filename": "product_manual.pdf",
                        "file_size": 2048576,
                        "upload_timestamp": 1703123456.789,
                        "chunks_count": 25,
                        "status": "active",
                        "metadata": {
                            "file_type": "pdf",
                            "pages": 15,
                            "language": "en"
                        }
                    }
                ],
                "total": 150,
                "limit": 20,
                "offset": 0
            }
        }


class ErrorResponse(BaseModel):
    """Error response model.
    
    Standardized error response format with detailed error information.
    """
    error: str = Field(
        description="Error message",
        example="File validation failed"
    )
    detail: Optional[str] = Field(
        description="Detailed error information",
        example="File size exceeds maximum allowed size of 10MB"
    )
    timestamp: float = Field(
        description="Error timestamp (Unix timestamp)",
        example=1703123456.789
    )
    request_id: Optional[str] = Field(
        description="Request identifier for tracking",
        example="req_abc123def456"
    )

    class Config:
        schema_extra = {
            "example": {
                "error": "File validation failed",
                "detail": "File size exceeds maximum allowed size of 10MB",
                "timestamp": 1703123456.789,
                "request_id": "req_abc123def456"
            }
        }


class MetricsResponse(BaseModel):
    """System metrics response model.
    
    Provides system performance and usage metrics.
    """
    total_requests: int = Field(
        description="Total number of requests processed",
        example=1250
    )
    failed_requests: int = Field(
        description="Number of failed requests",
        example=23
    )
    success_rate: float = Field(
        description="Request success rate (0.0-1.0)",
        example=0.982
    )
    uptime: float = Field(
        description="System uptime in seconds",
        example=86400.5
    )
    services: Dict[str, Dict[str, Any]] = Field(
        description="Service-specific metrics",
        example={
            "document_processor": {
                "documents_processed": 150,
                "average_processing_time": 2.34,
                "queue_size": 0
            },
            "vector_store": {
                "total_documents": 150,
                "total_chunks": 3750,
                "index_size_mb": 45.2
            }
        }
    )

    class Config:
        schema_extra = {
            "example": {
                "total_requests": 1250,
                "failed_requests": 23,
                "success_rate": 0.982,
                "uptime": 86400.5,
                "services": {
                    "document_processor": {
                        "documents_processed": 150,
                        "average_processing_time": 2.34,
                        "queue_size": 0
                    },
                    "vector_store": {
                        "total_documents": 150,
                        "total_chunks": 3750,
                        "index_size_mb": 45.2
                    },
                    "llm_service": {
                        "queries_processed": 1250,
                        "average_response_time": 1.87,
                        "tokens_generated": 45000
                    }
                }
            }
        }


class ServiceHealthResponse(BaseModel):
    """Individual service health response model.
    
    Provides detailed health information for a specific service.
    """
    service: str = Field(
        description="Service name",
        example="document_processor"
    )
    status: str = Field(
        description="Service status",
        example="healthy",
        enum=["healthy", "degraded", "unhealthy", "error"]
    )
    health_data: Dict[str, Any] = Field(
        description="Service-specific health data",
        example={
            "queue_size": 0,
            "memory_usage_mb": 128.5,
            "cpu_usage_percent": 15.2
        }
    )
    last_check: float = Field(
        description="Last health check timestamp",
        example=1703123456.789
    )
    error_count: int = Field(
        description="Number of errors encountered",
        example=0
    )

    class Config:
        schema_extra = {
            "example": {
                "service": "document_processor",
                "status": "healthy",
                "health_data": {
                    "queue_size": 0,
                    "memory_usage_mb": 128.5,
                    "cpu_usage_percent": 15.2
                },
                "last_check": 1703123456.789,
                "error_count": 0
            }
        }


class StreamingChunk(BaseModel):
    """Streaming response chunk model.
    
    Represents a single chunk in a streaming response.
    """
    type: StreamChunkType = Field(
        description="Type of chunk",
        example="content"
    )
    content: Optional[str] = Field(
        description="Content chunk (for content type)",
        example="Our product offers several key features..."
    )
    sources: Optional[List[Dict[str, Any]]] = Field(
        description="Source information (for sources type)",
        example=[
            {
                "document_id": "doc_123",
                "filename": "manual.pdf",
                "score": 0.95
            }
        ]
    )
    metadata: Optional[Dict[str, Any]] = Field(
        description="Additional metadata",
        example={
            "chunk_index": 1,
            "total_chunks": 5
        }
    )
    timestamp: float = Field(
        description="Chunk timestamp",
        example=1703123456.789
    )
    progress: Optional[float] = Field(
        description="Progress percentage for uploads",
        example=75.5
    )
    error: Optional[str] = Field(
        description="Error message (for error type)",
        example=None
    )

    class Config:
        schema_extra = {
            "example": {
                "type": "content",
                "content": "Our product offers several key features including advanced AI capabilities...",
                "sources": None,
                "metadata": {
                    "chunk_index": 1,
                    "total_chunks": 5
                },
                "timestamp": 1703123456.789,
                "progress": None,
                "error": None
            }
        }


class StreamConnectionInfo(BaseModel):
    """Streaming connection information model.
    
    Provides information about active streaming connections.
    """
    connection_id: str = Field(
        description="Unique connection identifier",
        example="conn_abc123def456"
    )
    created_at: float = Field(
        description="Connection creation timestamp",
        example=1703123456.789
    )
    last_activity: float = Field(
        description="Last activity timestamp",
        example=1703123500.123
    )
    status: str = Field(
        description="Connection status",
        example="active",
        enum=["active", "idle", "closed", "error"]
    )
    metadata: Dict[str, Any] = Field(
        description="Connection metadata",
        example={
            "user_agent": "Mozilla/5.0...",
            "ip_address": "192.168.1.100",
            "query_type": "rag"
        }
    )

    class Config:
        schema_extra = {
            "example": {
                "connection_id": "conn_abc123def456",
                "created_at": 1703123456.789,
                "last_activity": 1703123500.123,
                "status": "active",
                "metadata": {
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "ip_address": "192.168.1.100",
                    "query_type": "rag"
                }
            }
        }


class APIInfo(BaseModel):
    """API information model.
    
    Provides basic API information and links.
    """
    name: str = Field(
        description="API name",
        example="ZeroRAG API"
    )
    version: str = Field(
        description="API version",
        example="1.0.0"
    )
    description: str = Field(
        description="API description",
        example="Production-ready RAG system using free/open-source components"
    )
    docs: str = Field(
        description="Documentation URL",
        example="/docs"
    )
    health: str = Field(
        description="Health check URL",
        example="/health"
    )

    class Config:
        schema_extra = {
            "example": {
                "name": "ZeroRAG API",
                "version": "1.0.0",
                "description": "Production-ready RAG system using free/open-source components",
                "docs": "/docs",
                "health": "/health"
            }
        }


class CleanupRequest(BaseModel):
    """Cleanup request model.
    
    Defines parameters for document and file cleanup operations.
    """
    document_ids: Optional[List[str]] = Field(
        description="Specific document IDs to cleanup",
        example=["doc_123", "doc_456"]
    )
    older_than_days: Optional[int] = Field(
        description="Cleanup documents older than N days",
        example=30
    )
    failed_uploads_only: bool = Field(
        default=False,
        description="Cleanup only failed uploads",
        example=False
    )
    dry_run: bool = Field(
        default=False,
        description="Perform dry run without actual deletion",
        example=True
    )

    class Config:
        schema_extra = {
            "example": {
                "document_ids": None,
                "older_than_days": 30,
                "failed_uploads_only": False,
                "dry_run": True
            }
        }


class CleanupResponse(BaseModel):
    """Cleanup response model.
    
    Provides results of cleanup operations including statistics and errors.
    """
    deleted_documents: int = Field(
        description="Number of documents deleted",
        example=15
    )
    deleted_files: int = Field(
        description="Number of files deleted",
        example=15
    )
    freed_space_bytes: int = Field(
        description="Space freed in bytes",
        example=52428800
    )
    errors: List[str] = Field(
        description="Errors encountered during cleanup",
        example=[]
    )
    dry_run: bool = Field(
        description="Whether this was a dry run",
        example=False
    )

    class Config:
        schema_extra = {
            "example": {
                "deleted_documents": 15,
                "deleted_files": 15,
                "freed_space_bytes": 52428800,
                "errors": [],
                "dry_run": False
            }
        }
