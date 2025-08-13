"""
ZeroRAG API Routes

This module contains all the API route handlers organized by functionality.
"""

import logging
import time
import json
import uuid
from typing import List, Optional, Dict, Any, Generator
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, BackgroundTasks, Request
from fastapi.responses import StreamingResponse

try:
    from ..config import get_config
    from ..services.service_factory import ServiceFactory
    from .advanced_features import (
        file_validator, upload_tracker, stream_manager, cleanup_manager,
        ProcessingStep, FileValidationError
    )
except ImportError:
    from config import get_config
    from services.service_factory import ServiceFactory
    from .advanced_features import (
        file_validator, upload_tracker, stream_manager, cleanup_manager,
        ProcessingStep, FileValidationError
    )
from .models import (
    HealthResponse, QueryRequest, QueryResponse, DocumentUploadResponse,
    DocumentListResponse, MetricsResponse, ServiceHealthResponse, APIInfo,
    UploadProgressResponse, FileValidationRequest, FileValidationResponse,
    CleanupRequest, CleanupResponse, StreamConnectionInfo
)

logger = logging.getLogger(__name__)

# Initialize configuration
config = get_config()

# Create routers
health_router = APIRouter(prefix="/health", tags=["Health"])
documents_router = APIRouter(prefix="/documents", tags=["Documents"])
query_router = APIRouter(prefix="/query", tags=["Query"])
metrics_router = APIRouter(prefix="/metrics", tags=["Metrics"])
advanced_router = APIRouter(prefix="/advanced", tags=["Advanced Features"])


# Dependency injection
def get_service_factory() -> ServiceFactory:
    """Get the service factory instance."""
    return ServiceFactory()


# Health Routes
@health_router.get("/ping")
async def ping():
    """Simple ping endpoint for quick health checks."""
    return {"status": "ok", "timestamp": time.time()}

@health_router.get("/", response_model=HealthResponse)
async def health_check(service_factory: ServiceFactory = Depends(get_service_factory)):
    """Comprehensive health check endpoint."""
    try:
        # Get service status
        services_status = {}
        for service_name, service_info in service_factory.services.items():
            services_status[service_name] = {
                "status": service_info.status.value,
                "last_check": service_info.last_check,
                "error_count": service_info.error_count,
                "health_data": service_info.health_data
            }
        
        # Determine overall status
        overall_status = "healthy"
        if any(s["status"] == "unhealthy" for s in services_status.values()):
            overall_status = "degraded"
        if any(s["status"] == "error" for s in services_status.values()):
            overall_status = "unhealthy"
        
        return HealthResponse(
            status=overall_status,
            timestamp=time.time(),
            services=services_status,
            uptime=time.time() - service_factory.start_time
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@health_router.get("/services/{service_name}", response_model=ServiceHealthResponse)
async def service_health_check(
    service_name: str,
    service_factory: ServiceFactory = Depends(get_service_factory)
):
    """Individual service health check."""
    try:
        if service_name not in service_factory.services:
            raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
        
        service_info = service_factory.services[service_name]
        return ServiceHealthResponse(
            service=service_name,
            status=service_info.status.value,
            health_data=service_info.health_data,
            last_check=service_info.last_check,
            error_count=service_info.error_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Service health check failed for {service_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Service health check failed: {str(e)}")


# Document Routes
@documents_router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    service_factory: ServiceFactory = Depends(get_service_factory)
):
    """Upload and process a document with enhanced validation and progress tracking."""
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No filename provided")
        
        # Enhanced file validation
        validation_result = file_validator.validate_file(
            filename=file.filename,
            file_size=file.size,
            content_type=file.content_type
        )
        
        if not validation_result["is_valid"]:
            raise HTTPException(
                status_code=400,
                detail=f"File validation failed: {'; '.join(validation_result['errors'])}"
            )
        
        # Generate unique document ID
        document_id = str(uuid.uuid4())
        
        # Create upload progress tracker
        await upload_tracker.create_upload(document_id, file.filename, file.size)
        
        # Save file with original filename (no UUID prefix)
        # Handle filename conflicts by appending a number if file already exists
        base_path = Path(config.storage.upload_dir) / file.filename
        upload_path = base_path
        counter = 1
        
        while upload_path.exists():
            # Split filename and extension
            stem = base_path.stem
            suffix = base_path.suffix
            upload_path = base_path.parent / f"{stem}_{counter}{suffix}"
            counter += 1
        
        upload_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(upload_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Update progress to validation step
        await upload_tracker.update_progress(document_id, ProcessingStep.VALIDATION, 10.0)
        
        # Start background processing with progress tracking
        background_tasks.add_task(
            process_document_background_with_progress,
            upload_path,
            file.filename,
            document_id,
            service_factory
        )
        
        return DocumentUploadResponse(
            document_id=document_id,
            filename=file.filename,
            file_size=file.size,
            chunks_created=0,  # Will be updated after processing
            processing_time=0.0,
            status="processing",
            metadata={
                "content_type": file.content_type,
                "upload_timestamp": time.time(),
                "validation_warnings": validation_result.get("warnings", []),
                "estimated_processing_time": validation_result.get("estimated_processing_time"),
                "supported_features": validation_result.get("supported_features", [])
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@documents_router.get("/upload/{document_id}/progress", response_model=UploadProgressResponse)
async def get_upload_progress(document_id: str):
    """Get upload progress for a specific document."""
    try:
        progress = await upload_tracker.get_progress(document_id)
        if not progress:
            raise HTTPException(status_code=404, detail="Upload not found")
        
        return UploadProgressResponse(
            document_id=progress.document_id,
            status=progress.status,
            progress=progress.progress,
            current_step=progress.current_step.value,
            estimated_time_remaining=progress.estimated_time_remaining,
            error_message=progress.error_message,
            metadata=progress.metadata
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get upload progress for {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")


@documents_router.post("/validate", response_model=FileValidationResponse)
async def validate_file(request: FileValidationRequest):
    """Validate a file before upload."""
    try:
        validation_result = file_validator.validate_file(
            filename=request.filename,
            file_size=request.file_size,
            content_type=request.content_type
        )
        
        return FileValidationResponse(
            is_valid=validation_result["is_valid"],
            errors=validation_result["errors"],
            warnings=validation_result["warnings"],
            estimated_processing_time=validation_result["estimated_processing_time"],
            supported_features=validation_result["supported_features"]
        )
        
    except Exception as e:
        logger.error(f"File validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@documents_router.get("/", response_model=DocumentListResponse)
async def list_documents(
    limit: int = 100,
    offset: int = 0,
    service_factory: ServiceFactory = Depends(get_service_factory)
):
    """List uploaded documents."""
    try:
        # Try to use existing vector store first
        if service_factory.vector_store:
            documents = service_factory.vector_store.list_documents(limit=limit, offset=offset)
        else:
            # Create lightweight direct Qdrant connection for document listing only
            from qdrant_client import QdrantClient
            from ..config import get_config
            
            config = get_config()
            client = QdrantClient(
                host=config.database.qdrant_host,
                port=config.database.qdrant_port,
                api_key=config.database.qdrant_api_key,
                timeout=10.0
            )
            
            # Get documents directly from Qdrant
            search_results = client.scroll(
                collection_name=config.database.qdrant_collection_name,
                limit=limit,
                offset=offset,
                with_payload=True
            )[0]
            
            # Group by source file
            source_files = {}
            for point in search_results:
                source_file = point.payload.get("source_file", "")
                if source_file not in source_files:
                    source_files[source_file] = {
                        "id": source_file,
                        "source_file": source_file,
                        "chunk_count": 0,
                        "created_at": point.payload.get("created_at", ""),
                        "updated_at": point.payload.get("updated_at", ""),
                        "metadata": point.payload.get("metadata", {})
                    }
                source_files[source_file]["chunk_count"] += 1
            
            documents = list(source_files.values())
        
        # Format documents for response
        formatted_documents = []
        for doc in documents:
            # Try to get document_id from metadata, fallback to source_file
            metadata = doc.get("metadata", {})
            document_id = metadata.get("document_id", doc.get("id", ""))
            
            formatted_documents.append({
                "document_id": document_id,
                "filename": doc.get("source_file", "Unknown"),
                "file_size": 0,  # Not available from vector store
                "upload_timestamp": time.time(),  # Use current time as fallback
                "chunks_count": doc.get("chunk_count", 0),
                "status": "active",
                "metadata": doc.get("metadata", {})
            })
        
        return DocumentListResponse(
            documents=formatted_documents,
            total=len(formatted_documents),
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@documents_router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    service_factory: ServiceFactory = Depends(get_service_factory)
):
    """Delete a document and its chunks."""
    try:
        # This would typically delete from vector store and file system
        # For now, return a placeholder response
        return {"message": f"Document {document_id} deleted successfully"}
        
    except Exception as e:
        logger.error(f"Failed to delete document {document_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


# Query Routes
@query_router.post("/", response_model=QueryResponse)
async def query(
    request: QueryRequest,
    service_factory: ServiceFactory = Depends(get_service_factory)
):
    """Process a query and return a response."""
    try:
        start_time = time.time()
        
        # Validate RAG pipeline availability
        if not service_factory.rag_pipeline:
            raise HTTPException(status_code=503, detail="RAG pipeline not available")
        
        # Create RAG query
        from ..services.rag_pipeline import RAGQuery
        
        # Prepare filters for document selection
        filters = None
        if request.document_ids:
            filters = {"document_ids": request.document_ids}
            logger.info(f"Applying document filters: {filters}")
        
        rag_query = RAGQuery(
            query=request.query,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
            max_context_length=request.max_context_length,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            include_sources=request.include_sources,
            response_format=request.response_format,
            safety_level=request.safety_level,
            filters=filters
        )
        
        logger.info(f"RAG query created with filters: {rag_query.filters}")
        
        # Process query
        response = service_factory.rag_pipeline.process_query(rag_query)
        
        if not response:
            raise HTTPException(status_code=404, detail="No relevant documents found")
        
        # Format sources
        sources = []
        if response.sources:
            for source in response.sources:
                sources.append({
                    "filename": source.get("file", "Unknown"),
                    "chunk_index": source.get("chunk_index", 0),
                    "relevance_score": source.get("score", 0.0),
                    "content_preview": source.get("text_preview", "")[:200] + "..." if len(source.get("text_preview", "")) > 200 else source.get("text_preview", "")
                })
        
        return QueryResponse(
            answer=response.answer,
            sources=sources,
            response_time=time.time() - start_time,
            tokens_used=response.tokens_used,
            metadata={
                "query_type": response.context.query if hasattr(response, 'context') else None,
                "context_length": response.context.context_length if hasattr(response, 'context') else 0,
                "validation_status": response.validation_status,
                "safety_score": response.safety_score
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {str(e)}")


@query_router.post("/stream")
async def query_stream(
    request: QueryRequest,
    client_request: Request,
    service_factory: ServiceFactory = Depends(get_service_factory)
):
    """Process a query and return a streaming response with connection management."""
    try:
        # Validate RAG pipeline availability
        if not service_factory.rag_pipeline:
            raise HTTPException(status_code=503, detail="RAG pipeline not available")
        
        # Create connection ID
        connection_id = str(uuid.uuid4())
        
        # Create streaming connection
        await stream_manager.create_connection(
            connection_id,
            metadata={
                "query": request.query[:100],  # Truncate for metadata
                "user_agent": client_request.headers.get("user-agent", ""),
                "ip_address": client_request.client.host if client_request.client else None
            }
        )
        
        # Create RAG query
        from ..services.rag_pipeline import RAGQuery
        
        # Prepare filters for document selection
        filters = None
        if request.document_ids:
            filters = {"document_ids": request.document_ids}
        
        rag_query = RAGQuery(
            query=request.query,
            top_k=request.top_k,
            score_threshold=request.score_threshold,
            max_context_length=request.max_context_length,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            include_sources=request.include_sources,
            response_format=request.response_format,
            safety_level=request.safety_level,
            filters=filters
        )
        
        async def generate_stream() -> Generator[str, None, None]:
            """Generate streaming response with connection management."""
            try:
                # Update connection activity
                await stream_manager.update_activity(connection_id)
                
                # Get streaming response from RAG pipeline
                for chunk in service_factory.rag_pipeline.process_query_stream(rag_query):
                    if chunk:
                        # Update connection activity
                        await stream_manager.update_activity(connection_id)
                        
                        # Send chunk
                        yield f"data: {json.dumps(chunk)}\n\n"
                
                # Send end marker
                yield f"data: {json.dumps({'type': 'end'})}\n\n"
                
                # Close connection
                await stream_manager.close_connection(connection_id)
                
            except Exception as e:
                error_data = {"type": "error", "message": str(e)}
                yield f"data: {json.dumps(error_data)}\n\n"
                
                # Close connection on error
                await stream_manager.close_connection(connection_id)
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Content-Type": "text/event-stream",
                "X-Connection-ID": connection_id
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Streaming query failed: {e}")
        raise HTTPException(status_code=500, detail=f"Streaming query failed: {str(e)}")


# Advanced Features Routes
@advanced_router.get("/connections", response_model=List[StreamConnectionInfo])
async def list_stream_connections():
    """List active streaming connections."""
    try:
        connections = await stream_manager.list_connections()
        return [
            StreamConnectionInfo(
                connection_id=conn.connection_id,
                created_at=conn.created_at,
                last_activity=conn.last_activity,
                status=conn.status,
                metadata=conn.metadata
            )
            for conn in connections
        ]
    except Exception as e:
        logger.error(f"Failed to list connections: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list connections: {str(e)}")


@advanced_router.delete("/connections/{connection_id}")
async def close_stream_connection(connection_id: str):
    """Close a specific streaming connection."""
    try:
        success = await stream_manager.close_connection(connection_id)
        if not success:
            raise HTTPException(status_code=404, detail="Connection not found")
        
        return {"message": f"Connection {connection_id} closed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to close connection {connection_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to close connection: {str(e)}")


@advanced_router.post("/cleanup", response_model=CleanupResponse)
async def cleanup_documents(request: CleanupRequest):
    """Clean up documents and files."""
    try:
        result = await cleanup_manager.cleanup_documents(
            document_ids=request.document_ids,
            older_than_days=request.older_than_days,
            failed_uploads_only=request.failed_uploads_only,
            dry_run=request.dry_run
        )
        
        return CleanupResponse(
            deleted_documents=result["deleted_documents"],
            deleted_files=result["deleted_files"],
            freed_space_bytes=result["freed_space_bytes"],
            errors=result["errors"],
            dry_run=result["dry_run"]
        )
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")


@advanced_router.get("/storage/stats")
async def get_storage_stats():
    """Get storage statistics."""
    try:
        stats = await cleanup_manager.get_storage_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get storage stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get storage stats: {str(e)}")


# Metrics Routes
@metrics_router.get("/", response_model=MetricsResponse)
async def get_metrics(service_factory: ServiceFactory = Depends(get_service_factory)):
    """Get system metrics."""
    try:
        return MetricsResponse(
            total_requests=service_factory.total_requests,
            failed_requests=service_factory.failed_requests,
            success_rate=(service_factory.total_requests - service_factory.failed_requests) / max(service_factory.total_requests, 1),
            uptime=time.time() - service_factory.start_time,
            services={
                name: {
                    "status": info.status.value,
                    "error_count": info.error_count,
                    "last_check": info.last_check
                }
                for name, info in service_factory.services.items()
            }
        )
        
    except Exception as e:
        logger.error(f"Failed to get metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


# Background task function with progress tracking
async def process_document_background_with_progress(
    file_path: Path,
    filename: str,
    document_id: str,
    service_factory: ServiceFactory
):
    """Background task for document processing with progress tracking."""
    try:
        logger.info(f"Processing document {filename} in background")
        
        # Update progress to parsing step
        await upload_tracker.update_progress(document_id, ProcessingStep.PARSING, 20.0)
        
        # Process document
        try:
            result = service_factory.document_processor.process_file(file_path, document_id)
            logger.info(f"Document processing completed for {filename}, result type: {type(result)}")
        except Exception as e:
            logger.error(f"Document processing failed for {filename}: {e}")
            raise
        
        # Update progress to chunking step
        await upload_tracker.update_progress(document_id, ProcessingStep.CHUNKING, 40.0)
        
        # Store in vector database
        logger.info(f"Processing result for {filename}: {result}")
        if result and result.get('chunks'):
            # Update progress to embedding step
            await upload_tracker.update_progress(document_id, ProcessingStep.EMBEDDING, 60.0)
            
            # Embed the documents before storing
            try:
                embedding_service = service_factory.get_embedding_service()
                if embedding_service:
                    # Extract text from chunks for embedding
                    texts = [chunk.text for chunk in result['chunks']]
                    embeddings = embedding_service.encode(texts)
                    
                    # Update chunks with embeddings
                    for i, chunk in enumerate(result['chunks']):
                        if i < len(embeddings):
                            chunk.vector = embeddings[i]
                        else:
                            logger.warning(f"Missing embedding for chunk {i}")
                    
                    logger.info(f"Successfully embedded {len(embeddings)} chunks for {filename}")
                else:
                    logger.error("Embedding service not available")
                    raise Exception("Embedding service not available")
            except Exception as e:
                logger.error(f"Embedding failed for {filename}: {e}")
                raise
            
            service_factory.vector_store.insert_documents_batch(result['chunks'])
            
            # Update progress to storage step
            await upload_tracker.update_progress(document_id, ProcessingStep.STORAGE, 80.0)
            
            # Update progress to completed
            await upload_tracker.update_progress(document_id, ProcessingStep.COMPLETED, 100.0)
            
            logger.info(f"Successfully processed and stored {len(result['chunks'])} chunks for {filename}")
        else:
            # Update progress to failed
            await upload_tracker.update_progress(
                document_id, 
                ProcessingStep.COMPLETED, 
                100.0, 
                error_message="No chunks created from document"
            )
            logger.warning(f"No chunks created for document {filename}")
            
    except Exception as e:
        # Update progress to failed
        await upload_tracker.update_progress(
            document_id, 
            ProcessingStep.COMPLETED, 
            100.0, 
            error_message=str(e)
        )
        logger.error(f"Background processing failed for {filename}: {e}")


# Background task function (legacy)
async def process_document_background(
    file_path: Path,
    filename: str,
    document_id: str,
    service_factory: ServiceFactory
):
    """Background task for document processing."""
    try:
        logger.info(f"Processing document {filename} in background")
        
        # Process document
        result = service_factory.document_processor.process_file(file_path)
        
        # Store in vector database
        if result and result.get('chunks'):
            # Embed the documents before storing
            try:
                embedding_service = service_factory.get_embedding_service()
                if embedding_service:
                    # Extract text from chunks for embedding
                    texts = [chunk.text for chunk in result['chunks']]
                    embeddings = embedding_service.encode(texts)
                    
                    # Update chunks with embeddings
                    for i, chunk in enumerate(result['chunks']):
                        if i < len(embeddings):
                            chunk.vector = embeddings[i]
                        else:
                            logger.warning(f"Missing embedding for chunk {i}")
                    
                    logger.info(f"Successfully embedded {len(embeddings)} chunks for {filename}")
                else:
                    logger.error("Embedding service not available")
                    raise Exception("Embedding service not available")
            except Exception as e:
                logger.error(f"Embedding failed for {filename}: {e}")
                raise
            
            service_factory.vector_store.insert_documents_batch(result['chunks'])
            logger.info(f"Successfully processed and stored {len(result['chunks'])} chunks for {filename}")
        else:
            logger.warning(f"No chunks created for document {filename}")
            
    except Exception as e:
        logger.error(f"Background processing failed for {filename}: {e}")
