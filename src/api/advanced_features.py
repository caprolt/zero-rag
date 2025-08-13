"""
ZeroRAG Advanced API Features

This module provides advanced API features including:
- File validation and preprocessing
- Upload progress tracking
- Cleanup mechanisms
- Streaming connection management
- Enhanced error handling
"""

import logging
import time
import json
import asyncio
import hashlib
import mimetypes
from typing import Dict, List, Optional, Any, Set
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

try:
    from ..config import get_config
except ImportError:
    from config import get_config

logger = logging.getLogger(__name__)

# Initialize configuration
config = get_config()


class FileValidationError(Exception):
    """Custom exception for file validation errors."""
    pass


class ProcessingStep(str, Enum):
    """Document processing steps."""
    UPLOAD = "upload"
    VALIDATION = "validation"
    PARSING = "parsing"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    STORAGE = "storage"
    COMPLETED = "completed"


@dataclass
class UploadProgress:
    """Upload progress tracking data."""
    document_id: str
    filename: str
    file_size: int
    status: str
    progress: float
    current_step: ProcessingStep
    start_time: float
    last_update: float
    estimated_time_remaining: Optional[float]
    error_message: Optional[str]
    metadata: Dict[str, Any]


@dataclass
class StreamConnection:
    """Streaming connection tracking data."""
    connection_id: str
    created_at: float
    last_activity: float
    status: str
    metadata: Dict[str, Any]
    task: Optional[asyncio.Task] = None


class FileValidator:
    """File validation and preprocessing utilities."""
    
    def __init__(self):
        self.supported_formats = config.document.supported_formats
        self.max_file_size = self._parse_file_size(config.document.max_file_size)
        
        # File type signatures (magic bytes)
        self.file_signatures = {
            b'\x50\x4B\x03\x04': 'zip',
            b'\x25\x50\x44\x46': 'pdf',
            b'\xFF\xFE': 'txt',  # UTF-16 LE
            b'\xFE\xFF': 'txt',  # UTF-16 BE
            b'\xEF\xBB\xBF': 'txt',  # UTF-8 BOM
        }
        
        # Content type mappings
        self.content_type_mappings = {
            'text/plain': ['txt', 'md', 'csv'],
            'text/markdown': ['md', 'markdown'],
            'text/csv': ['csv'],
            'application/pdf': ['pdf'],
            'application/zip': ['zip'],
            'application/json': ['json'],
        }
    
    def _parse_file_size(self, size_str: str) -> int:
        """Parse file size string to bytes."""
        if size_str.endswith("MB"):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith("KB"):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith("B"):
            return int(size_str[:-1])
        else:
            return int(size_str)
    
    def validate_file(self, filename: str, file_size: int, content_type: Optional[str] = None) -> Dict[str, Any]:
        """Validate file before upload."""
        errors = []
        warnings = []
        
        # Check file size
        if file_size > self.max_file_size:
            errors.append(f"File size {file_size} bytes exceeds maximum {self.max_file_size} bytes")
        
        # Check file extension
        file_extension = Path(filename).suffix.lower().lstrip(".")
        if file_extension not in self.supported_formats:
            errors.append(f"Unsupported file format: {file_extension}")
        
        # Check content type if provided
        if content_type:
            expected_extensions = self.content_type_mappings.get(content_type, [])
            if file_extension not in expected_extensions:
                warnings.append(f"Content type {content_type} doesn't match file extension {file_extension}")
        
        # Check for potentially malicious files
        if self._is_potentially_malicious(filename, file_size):
            errors.append("File appears to be potentially malicious")
        
        # Estimate processing time
        estimated_time = self._estimate_processing_time(file_size, file_extension)
        
        # Get supported features
        supported_features = self._get_supported_features(file_extension)
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "estimated_processing_time": estimated_time,
            "supported_features": supported_features,
            "file_extension": file_extension,
            "content_type": content_type
        }
    
    def _is_potentially_malicious(self, filename: str, file_size: int) -> bool:
        """Check if file might be malicious."""
        suspicious_extensions = {'.exe', '.bat', '.cmd', '.com', '.scr', '.pif', '.vbs', '.js'}
        file_extension = Path(filename).suffix.lower()
        
        # Check for suspicious extensions
        if file_extension in suspicious_extensions:
            return True
        
        # Check for double extensions (e.g., document.pdf.exe)
        if filename.count('.') > 1:
            return True
        
        # Check for extremely large files
        if file_size > 100 * 1024 * 1024:  # 100MB
            return True
        
        return False
    
    def _estimate_processing_time(self, file_size: int, file_extension: str) -> float:
        """Estimate processing time based on file size and type."""
        # Base processing rate (bytes per second)
        base_rate = 1024 * 1024  # 1MB per second
        
        # Adjust rate based on file type
        type_multipliers = {
            'txt': 1.0,
            'md': 1.2,
            'csv': 1.5,
            'pdf': 2.0,
            'json': 1.1,
        }
        
        multiplier = type_multipliers.get(file_extension, 1.5)
        estimated_time = (file_size / base_rate) * multiplier
        
        return min(estimated_time, 300)  # Cap at 5 minutes
    
    def _get_supported_features(self, file_extension: str) -> List[str]:
        """Get supported features for file type."""
        features = ["text_extraction", "chunking", "embedding"]
        
        if file_extension in ['txt', 'md']:
            features.extend(["markdown_rendering", "syntax_highlighting"])
        elif file_extension == 'csv':
            features.extend(["table_parsing", "data_analysis"])
        elif file_extension == 'pdf':
            features.extend(["pdf_text_extraction", "page_metadata"])
        elif file_extension == 'json':
            features.extend(["json_parsing", "schema_validation"])
        
        return features


class UploadProgressTracker:
    """Upload progress tracking and management."""
    
    def __init__(self):
        self.uploads: Dict[str, UploadProgress] = {}
        self._lock = asyncio.Lock()
    
    async def create_upload(self, document_id: str, filename: str, file_size: int) -> UploadProgress:
        """Create a new upload progress tracker."""
        async with self._lock:
            progress = UploadProgress(
                document_id=document_id,
                filename=filename,
                file_size=file_size,
                status="pending",
                progress=0.0,
                current_step=ProcessingStep.UPLOAD,
                start_time=time.time(),
                last_update=time.time(),
                estimated_time_remaining=None,
                error_message=None,
                metadata={}
            )
            self.uploads[document_id] = progress
            return progress
    
    async def update_progress(self, document_id: str, step: ProcessingStep, progress: float, 
                            error_message: Optional[str] = None) -> Optional[UploadProgress]:
        """Update upload progress."""
        async with self._lock:
            if document_id not in self.uploads:
                return None
            
            upload = self.uploads[document_id]
            upload.current_step = step
            upload.progress = min(progress, 100.0)
            upload.last_update = time.time()
            
            if error_message:
                upload.error_message = error_message
                upload.status = "failed"
            elif progress >= 100.0:
                upload.status = "completed"
            else:
                upload.status = "processing"
            
            # Update estimated time remaining
            if upload.progress > 0:
                elapsed = time.time() - upload.start_time
                if upload.progress < 100:
                    upload.estimated_time_remaining = (elapsed / upload.progress) * (100 - upload.progress)
                else:
                    upload.estimated_time_remaining = 0
            
            return upload
    
    async def get_progress(self, document_id: str) -> Optional[UploadProgress]:
        """Get upload progress."""
        async with self._lock:
            return self.uploads.get(document_id)
    
    async def cleanup_old_uploads(self, max_age_hours: int = 24) -> int:
        """Clean up old upload records."""
        async with self._lock:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            to_remove = []
            for doc_id, upload in self.uploads.items():
                if current_time - upload.last_update > max_age_seconds:
                    to_remove.append(doc_id)
            
            for doc_id in to_remove:
                del self.uploads[doc_id]
            
            return len(to_remove)


class StreamConnectionManager:
    """Streaming connection management and monitoring."""
    
    def __init__(self):
        self.connections: Dict[str, StreamConnection] = {}
        self._lock = asyncio.Lock()
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def create_connection(self, connection_id: str, metadata: Dict[str, Any] = None) -> StreamConnection:
        """Create a new streaming connection."""
        async with self._lock:
            connection = StreamConnection(
                connection_id=connection_id,
                created_at=time.time(),
                last_activity=time.time(),
                status="active",
                metadata=metadata or {},
                task=None
            )
            self.connections[connection_id] = connection
            return connection
    
    async def update_activity(self, connection_id: str) -> bool:
        """Update connection activity timestamp."""
        async with self._lock:
            if connection_id in self.connections:
                self.connections[connection_id].last_activity = time.time()
                return True
            return False
    
    async def close_connection(self, connection_id: str) -> bool:
        """Close a streaming connection."""
        async with self._lock:
            if connection_id in self.connections:
                connection = self.connections[connection_id]
                connection.status = "closed"
                if connection.task and not connection.task.done():
                    connection.task.cancel()
                return True
            return False
    
    async def get_connection_info(self, connection_id: str) -> Optional[StreamConnection]:
        """Get connection information."""
        async with self._lock:
            return self.connections.get(connection_id)
    
    async def list_connections(self) -> List[StreamConnection]:
        """List all active connections."""
        async with self._lock:
            return list(self.connections.values())
    
    async def cleanup_inactive_connections(self, timeout_minutes: int = 30) -> int:
        """Clean up inactive connections."""
        async with self._lock:
            current_time = time.time()
            timeout_seconds = timeout_minutes * 60
            
            to_remove = []
            for conn_id, connection in self.connections.items():
                if current_time - connection.last_activity > timeout_seconds:
                    to_remove.append(conn_id)
            
            for conn_id in to_remove:
                if self.connections[conn_id].task and not self.connections[conn_id].task.done():
                    self.connections[conn_id].task.cancel()
                del self.connections[conn_id]
            
            return len(to_remove)
    
    async def start_cleanup_task(self):
        """Start periodic cleanup task."""
        if self._cleanup_task and not self._cleanup_task.done():
            return
        
        async def cleanup_loop():
            while True:
                try:
                    await asyncio.sleep(300)  # Run every 5 minutes
                    await self.cleanup_inactive_connections()
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Cleanup task error: {e}")
        
        self._cleanup_task = asyncio.create_task(cleanup_loop())


class CleanupManager:
    """File and document cleanup management."""
    
    def __init__(self):
        self.upload_dir = Path(config.storage.upload_dir)
        self.processed_dir = Path(config.storage.processed_dir)
        self.cache_dir = Path(config.storage.cache_dir)
    
    async def cleanup_documents(self, document_ids: Optional[List[str]] = None, 
                              older_than_days: Optional[int] = None,
                              failed_uploads_only: bool = False,
                              dry_run: bool = False) -> Dict[str, Any]:
        """Clean up documents and files."""
        deleted_documents = 0
        deleted_files = 0
        freed_space_bytes = 0
        errors = []
        
        try:
            # Clean up specific documents
            if document_ids:
                for doc_id in document_ids:
                    try:
                        space_freed = await self._cleanup_document(doc_id, dry_run)
                        if space_freed > 0:
                            deleted_documents += 1
                            deleted_files += 1
                            freed_space_bytes += space_freed
                    except Exception as e:
                        errors.append(f"Failed to cleanup document {doc_id}: {e}")
            
            # Clean up old documents
            elif older_than_days:
                cutoff_time = datetime.now() - timedelta(days=older_than_days)
                cutoff_timestamp = cutoff_time.timestamp()
                
                for file_path in self.upload_dir.glob("*"):
                    if file_path.is_file():
                        try:
                            file_mtime = file_path.stat().st_mtime
                            if file_mtime < cutoff_timestamp:
                                space_freed = await self._cleanup_file(file_path, dry_run)
                                if space_freed > 0:
                                    deleted_files += 1
                                    freed_space_bytes += space_freed
                        except Exception as e:
                            errors.append(f"Failed to cleanup file {file_path}: {e}")
            
            # Clean up failed uploads
            elif failed_uploads_only:
                # This would require tracking failed uploads in a database
                # For now, we'll implement a simple file-based approach
                pass
            
            return {
                "deleted_documents": deleted_documents,
                "deleted_files": deleted_files,
                "freed_space_bytes": freed_space_bytes,
                "errors": errors,
                "dry_run": dry_run
            }
            
        except Exception as e:
            errors.append(f"Cleanup operation failed: {e}")
            return {
                "deleted_documents": deleted_documents,
                "deleted_files": deleted_files,
                "freed_space_bytes": freed_space_bytes,
                "errors": errors,
                "dry_run": dry_run
            }
    
    async def _cleanup_document(self, document_id: str, dry_run: bool) -> int:
        """Clean up a specific document."""
        freed_space = 0
        
        # Get the upload progress to find the filename
        upload_progress = await self.get_progress(document_id)
        if upload_progress and upload_progress.filename:
            # Look for files with the original filename (and potential number suffixes)
            filename_stem = Path(upload_progress.filename).stem
            filename_suffix = Path(upload_progress.filename).suffix
            
            # Find files in upload directory
            for file_path in self.upload_dir.glob(f"{filename_stem}*{filename_suffix}"):
                if file_path.is_file():
                    freed_space += await self._cleanup_file(file_path, dry_run)
            
            # Find files in processed directory
            for file_path in self.processed_dir.glob(f"{filename_stem}*{filename_suffix}"):
                if file_path.is_file():
                    freed_space += await self._cleanup_file(file_path, dry_run)
        
        return freed_space
    
    async def _cleanup_file(self, file_path: Path, dry_run: bool) -> int:
        """Clean up a specific file."""
        try:
            file_size = file_path.stat().st_size
            
            if not dry_run:
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
            
            return file_size
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return 0
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        try:
            upload_size = sum(f.stat().st_size for f in self.upload_dir.rglob("*") if f.is_file())
            processed_size = sum(f.stat().st_size for f in self.processed_dir.rglob("*") if f.is_file())
            cache_size = sum(f.stat().st_size for f in self.cache_dir.rglob("*") if f.is_file())
            
            return {
                "upload_dir_size": upload_size,
                "processed_dir_size": processed_size,
                "cache_dir_size": cache_size,
                "total_size": upload_size + processed_size + cache_size,
                "file_counts": {
                    "upload": len(list(self.upload_dir.rglob("*"))),
                    "processed": len(list(self.processed_dir.rglob("*"))),
                    "cache": len(list(self.cache_dir.rglob("*")))
                }
            }
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {
                "upload_dir_size": 0,
                "processed_dir_size": 0,
                "cache_dir_size": 0,
                "total_size": 0,
                "file_counts": {"upload": 0, "processed": 0, "cache": 0},
                "error": str(e)
            }


# Global instances
file_validator = FileValidator()
upload_tracker = UploadProgressTracker()
stream_manager = StreamConnectionManager()
cleanup_manager = CleanupManager()
