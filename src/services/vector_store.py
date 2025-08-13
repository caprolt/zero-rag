"""
ZeroRAG Vector Store Service

This module provides vector database operations using Qdrant for document storage,
retrieval, and search with comprehensive CRUD operations and performance monitoring.
Enhanced with Phase 4.3 optimizations including operation queuing, batch processing,
memory optimization, and performance alerts.
"""

import logging
import time
import hashlib
import json
import threading
import queue
from typing import Dict, Any, List, Optional, Tuple, Union, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
import gc
import weakref

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.http.models import (
    Distance, VectorParams, PointStruct, Filter, FieldCondition,
    Range, MatchValue, MatchAny, GeoBoundingBox
)

logger = logging.getLogger(__name__)


@dataclass
class VectorDocument:
    """Vector document container for storage and retrieval."""
    id: str
    text: str
    vector: List[float]
    metadata: Dict[str, Any]
    source_file: str
    chunk_index: int
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "text": self.text,
            "vector": self.vector,
            "metadata": self.metadata,
            "source_file": self.source_file,
            "chunk_index": self.chunk_index,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class SearchResult:
    """Search result container."""
    id: str
    text: str
    score: float
    metadata: Dict[str, Any]
    source_file: str
    chunk_index: int


@dataclass
class CollectionStats:
    """Collection statistics container."""
    total_points: int
    total_vectors: int
    collection_size: int
    last_updated: datetime
    source_files: List[str]
    chunk_count: int


@dataclass
class PerformanceAlert:
    """Performance alert container."""
    alert_type: str
    message: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    timestamp: datetime
    metrics: Dict[str, Any]


@dataclass
class OperationQueueItem:
    """Operation queue item for batch processing."""
    operation_type: str
    data: Any
    priority: int  # 1=high, 2=normal, 3=low
    callback: Optional[Callable] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
    
    def __lt__(self, other):
        """Enable comparison for priority queue ordering."""
        if not isinstance(other, OperationQueueItem):
            return NotImplemented
        # Lower priority number = higher priority
        if self.priority != other.priority:
            return self.priority < other.priority
        # If same priority, earlier timestamp = higher priority
        return self.timestamp < other.timestamp


class VectorStoreService:
    """
    Vector store service using Qdrant for document storage and retrieval.
    
    Features:
    - Full CRUD operations (Create, Read, Update, Delete)
    - Enhanced batch document operations with queuing
    - Advanced search with metadata filtering
    - Performance monitoring and metrics
    - Connection pooling and error handling
    - Collection management and statistics
    - Operation queuing for batch processing
    - Memory optimization and garbage collection
    - Performance alerts and health monitoring
    """
    
    def __init__(self, config=None):
        """Initialize the vector store service."""
        try:
            from ..config import get_config
        except ImportError:
            from config import get_config
        self.config = config or get_config()
        
        # Qdrant client
        self.client: Optional[QdrantClient] = None
        self.collection_name = self.config.database.qdrant_collection_name
        self.vector_size = self.config.database.qdrant_vector_size
        

        
        # Performance tracking
        self.total_operations = 0
        self.failed_operations = 0
        self.operation_times: Dict[str, List[float]] = {}
        self.start_time = time.time()
        
        # Connection status
        self.is_connected = False
        self.last_health_check = 0
        self.health_check_interval = 300  # 5 minutes
        
        # Phase 4.3 Enhancements: Operation Queuing
        self.operation_queue = queue.PriorityQueue()
        self.queue_worker_thread = None
        self.queue_running = False
        self.max_queue_size = 1000
        self.batch_size = self.config.api.batch_size  # Use configured batch size
        
        # Phase 4.3 Enhancements: Memory Management
        self.memory_threshold_mb = self.config.api.memory_threshold_mb
        self.last_gc_time = 0
        self.gc_interval = self.config.api.gc_interval_seconds
        self._memory_monitor_thread = None
        self._memory_monitor_running = False
        
        # Phase 4.3 Enhancements: Performance Alerts
        self.performance_alerts: List[PerformanceAlert] = []
        self.alert_callbacks: List[Callable] = []
        self.performance_thresholds = {
            'operation_time_ms': 1000,  # 1 second
            'memory_usage_mb': self.config.api.memory_critical_threshold_mb,
            'queue_size': 500,          # 500 items
            'error_rate': 0.05          # 5% error rate
        }
        
        # Phase 4.3 Enhancements: Enhanced Monitoring
        self.operation_counters: Dict[str, int] = {}
        self.error_counters: Dict[str, int] = {}
        self.memory_usage_history: List[Dict[str, Any]] = []
        self.max_history_size = 100
        
        # Initialize connection and start background services
        self._initialize_connection()
        self._start_background_services()
    
    def _start_background_services(self):
        """Start background services for queuing and monitoring."""
        try:
            # Start operation queue worker
            self.queue_running = True
            self.queue_worker_thread = threading.Thread(
                target=self._queue_worker,
                daemon=True,
                name="VectorStore-QueueWorker"
            )
            self.queue_worker_thread.start()
            
            # Start memory monitor
            self._memory_monitor_running = True
            self._memory_monitor_thread = threading.Thread(
                target=self._memory_monitor,
                daemon=True,
                name="VectorStore-MemoryMonitor"
            )
            self._memory_monitor_thread.start()
            
            logger.info("Background services started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start background services: {e}")
    
    def _queue_worker(self):
        """Background worker for processing queued operations."""
        while self.queue_running:
            try:
                # Get item from queue with timeout
                try:
                    item: OperationQueueItem = self.operation_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Process the operation
                self._process_queued_operation(item)
                
                # Mark task as done
                self.operation_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in queue worker: {e}")
                time.sleep(0.1)  # Brief pause on error
    
    def _process_queued_operation(self, item: OperationQueueItem):
        """Process a queued operation."""
        try:
            if item.operation_type == "batch_insert":
                # Process batch insert
                documents = item.data
                result = self._process_batch_insert(documents)
                
                # Call callback if provided
                if item.callback:
                    item.callback(result)
                    
            elif item.operation_type == "batch_delete":
                # Process batch delete
                document_ids = item.data
                result = self._process_batch_delete(document_ids)
                
                if item.callback:
                    item.callback(result)
                    
            elif item.operation_type == "collection_cleanup":
                # Process collection cleanup
                result = self._process_collection_cleanup()
                
                if item.callback:
                    item.callback(result)
                    
        except Exception as e:
            logger.error(f"Error processing queued operation {item.operation_type}: {e}")
            # Call callback with error if provided
            if item.callback:
                item.callback({"error": str(e), "successful": False})
    
    def _process_batch_insert(self, documents: List[VectorDocument]) -> Dict[str, Any]:
        """Process batch insert operation."""
        return self.insert_documents_batch(documents)
    
    def _process_batch_delete(self, document_ids: List[str]) -> Dict[str, Any]:
        """Process batch delete operation."""
        results = {
            "total": len(document_ids),
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        for doc_id in document_ids:
            try:
                if self.delete_document(doc_id):
                    results["successful"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Failed to delete {doc_id}")
            except Exception as e:
                results["failed"] += 1
                results["errors"].append(f"Error deleting {doc_id}: {e}")
        
        return results
    
    def _process_collection_cleanup(self) -> Dict[str, Any]:
        """Process collection cleanup operation."""
        try:
            # Force garbage collection
            gc.collect()
            
            # Clear memory usage history if too large
            if len(self.memory_usage_history) > self.max_history_size:
                self.memory_usage_history = self.memory_usage_history[-self.max_history_size:]
            
            return {"successful": True, "message": "Cleanup completed"}
        except Exception as e:
            return {"successful": False, "error": str(e)}
    
    def _memory_monitor(self):
        """Background memory monitoring thread."""
        consecutive_critical_alerts = 0
        last_cleanup_time = 0
        cleanup_cooldown = 60  # Minimum seconds between cleanups
        
        while self._memory_monitor_running:
            try:
                # Get current memory usage
                memory_info = self._get_memory_usage()
                current_memory_mb = memory_info.get("rss_mb", 0)
                current_time = time.time()
                
                # Store in history
                self.memory_usage_history.append({
                    "timestamp": datetime.now(),
                    "memory_mb": current_memory_mb,
                    "memory_percent": memory_info.get("percent", 0)
                })
                
                # Enhanced memory monitoring with multiple thresholds and cooldown
                if current_memory_mb > self.performance_thresholds['memory_usage_mb']:
                    # Critical memory usage
                    consecutive_critical_alerts += 1
                    
                    # Only trigger cleanup if enough time has passed since last cleanup
                    if current_time - last_cleanup_time > cleanup_cooldown:
                        self._create_performance_alert(
                            "memory_usage",
                            f"Memory usage critical: {current_memory_mb:.1f}MB (Alert #{consecutive_critical_alerts})",
                            "critical"
                        )
                        # Immediate aggressive cleanup
                        self._trigger_aggressive_memory_cleanup()
                        last_cleanup_time = current_time
                        
                        # If we've had multiple critical alerts, increase cooldown
                        if consecutive_critical_alerts > 3:
                            cleanup_cooldown = min(cleanup_cooldown * 1.5, 300)  # Max 5 minutes
                    else:
                        logger.debug(f"Memory critical but cleanup on cooldown: {current_memory_mb:.1f}MB")
                        
                elif current_memory_mb > self.memory_threshold_mb:
                    # High memory usage
                    consecutive_critical_alerts = 0  # Reset counter
                    cleanup_cooldown = 60  # Reset cooldown
                    
                    if current_time - last_cleanup_time > cleanup_cooldown:
                        self._create_performance_alert(
                            "memory_usage",
                            f"Memory usage high: {current_memory_mb:.1f}MB",
                            "high"
                        )
                        # Trigger standard cleanup
                        self._trigger_memory_cleanup()
                        last_cleanup_time = current_time
                        
                elif current_memory_mb > self.memory_threshold_mb * 0.8:
                    # Approaching threshold - preventive cleanup
                    consecutive_critical_alerts = 0  # Reset counter
                    cleanup_cooldown = 60  # Reset cooldown
                    
                    if current_time - last_cleanup_time > cleanup_cooldown * 2:  # Less frequent for preventive
                        self._create_performance_alert(
                            "memory_usage",
                            f"Memory usage approaching threshold: {current_memory_mb:.1f}MB",
                            "medium"
                        )
                        # Light cleanup
                        self._trigger_light_memory_cleanup()
                        last_cleanup_time = current_time
                else:
                    # Memory usage is normal
                    consecutive_critical_alerts = 0
                    cleanup_cooldown = 60
                
                # Check for memory leaks (gradual increase over time)
                if len(self.memory_usage_history) > 10:
                    recent_memory = [entry["memory_mb"] for entry in self.memory_usage_history[-10:]]
                    if len(recent_memory) >= 10:
                        # Check if memory is consistently increasing
                        if all(recent_memory[i] <= recent_memory[i+1] for i in range(len(recent_memory)-1)):
                            if recent_memory[-1] - recent_memory[0] > 200:  # 200MB increase
                                self._create_performance_alert(
                                    "memory_leak",
                                    f"Potential memory leak detected: {recent_memory[-1] - recent_memory[0]:.1f}MB increase over 10 checks",
                                    "high"
                                )
                                # Force aggressive cleanup for potential leak
                                self._trigger_aggressive_memory_cleanup()
                                last_cleanup_time = current_time
                
                # Check if garbage collection is needed
                if current_time - self.last_gc_time > self.gc_interval:
                    gc.collect()
                    self.last_gc_time = current_time
                
                # Sleep for monitoring interval
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in memory monitor: {e}")
                time.sleep(60)  # Longer sleep on error
    
    def _trigger_memory_cleanup(self):
        """Trigger standard memory cleanup operations."""
        try:
            # Add cleanup operation to queue
            cleanup_item = OperationQueueItem(
                operation_type="collection_cleanup",
                data=None,
                priority=1,  # High priority
                callback=None
            )
            
            self.operation_queue.put(cleanup_item)
            logger.info("Memory cleanup triggered")
            
        except Exception as e:
            logger.error(f"Error triggering memory cleanup: {e}")
    
    def _trigger_light_memory_cleanup(self):
        """Trigger light memory cleanup operations."""
        try:
            # Immediate light cleanup without queuing
            self._perform_light_cleanup()
            logger.info("Light memory cleanup performed")
            
        except Exception as e:
            logger.error(f"Error triggering light memory cleanup: {e}")
    
    def _trigger_aggressive_memory_cleanup(self):
        """Trigger aggressive memory cleanup operations."""
        try:
            # Immediate aggressive cleanup
            self._perform_aggressive_cleanup()
            logger.info("Aggressive memory cleanup performed")
            
            # Also queue a standard cleanup for additional safety
            cleanup_item = OperationQueueItem(
                operation_type="collection_cleanup",
                data=None,
                priority=1,  # High priority
                callback=None
            )
            self.operation_queue.put(cleanup_item)
            
        except Exception as e:
            logger.error(f"Error triggering aggressive memory cleanup: {e}")
    
    def _perform_light_cleanup(self):
        """Perform light memory cleanup."""
        try:
            # Force garbage collection
            gc.collect()
            
            # Clear old memory history entries
            if len(self.memory_usage_history) > self.max_history_size:
                self.memory_usage_history = self.memory_usage_history[-self.max_history_size//2:]
            
            # Clear old performance alerts
            if len(self.performance_alerts) > 25:
                self.performance_alerts = self.performance_alerts[-25:]
                
        except Exception as e:
            logger.error(f"Error in light cleanup: {e}")
    
    def _perform_aggressive_cleanup(self):
        """Perform aggressive memory cleanup."""
        try:
            # Multiple garbage collection passes with different generations
            for generation in range(3):
                collected = gc.collect(generation)
                logger.debug(f"GC generation {generation}: collected {collected} objects")
            
            # Clear most memory history
            if len(self.memory_usage_history) > 10:
                self.memory_usage_history = self.memory_usage_history[-10:]
            
            # Clear most performance alerts
            if len(self.performance_alerts) > 10:
                self.performance_alerts = self.performance_alerts[-10:]
            
            # Clear operation time history for old operations
            current_time = time.time()
            for operation in list(self.operation_times.keys()):
                if len(self.operation_times[operation]) > 100:
                    # Keep only recent times
                    self.operation_times[operation] = self.operation_times[operation][-50:]
            
            # Clear operation counters if they're too large
            for counter in list(self.operation_counters.keys()):
                if self.operation_counters[counter] > 10000:
                    self.operation_counters[counter] = 1000  # Reset to reasonable value
            
            # Clear error counters if they're too large
            for counter in list(self.error_counters.keys()):
                if self.error_counters[counter] > 1000:
                    self.error_counters[counter] = 100  # Reset to reasonable value
            
            # Force memory release
            import sys
            if hasattr(sys, 'exc_clear'):
                sys.exc_clear()
            
            # Clear any cached data in the client
            if hasattr(self.client, '_session') and hasattr(self.client._session, 'cache'):
                self.client._session.cache.clear()
            
            # Force Python to release memory back to OS
            try:
                import ctypes
                libc = ctypes.CDLL("libc.so.6")
                libc.malloc_trim(0)
            except (OSError, AttributeError):
                # Not available on Windows or other systems
                pass
                
        except Exception as e:
            logger.error(f"Error in aggressive cleanup: {e}")
    
    def _create_performance_alert(self, alert_type: str, message: str, severity: str, metrics: Dict[str, Any] = None):
        """Create a performance alert."""
        alert = PerformanceAlert(
            alert_type=alert_type,
            message=message,
            severity=severity,
            timestamp=datetime.now(),
            metrics=metrics or {}
        )
        
        self.performance_alerts.append(alert)
        
        # Keep only recent alerts
        if len(self.performance_alerts) > 50:
            self.performance_alerts = self.performance_alerts[-50:]
        
        # Call alert callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
        
        logger.warning(f"Performance Alert [{severity.upper()}]: {message}")
    
    def add_alert_callback(self, callback: Callable[[PerformanceAlert], None]):
        """Add a callback for performance alerts."""
        self.alert_callbacks.append(callback)
    
    def queue_batch_insert(self, documents: List[VectorDocument], priority: int = 2, callback: Callable = None) -> bool:
        """
        Queue a batch insert operation for background processing.
        
        Args:
            documents: List of documents to insert
            priority: Operation priority (1=high, 2=normal, 3=low)
            callback: Optional callback function to call when complete
            
        Returns:
            bool: True if queued successfully
        """
        try:
            if self.operation_queue.qsize() >= self.max_queue_size:
                self._create_performance_alert(
                    "queue_full",
                    f"Operation queue full: {self.operation_queue.qsize()} items",
                    "high"
                )
                return False
            
            item = OperationQueueItem(
                operation_type="batch_insert",
                data=documents,
                priority=priority,
                callback=callback
            )
            
            self.operation_queue.put(item)
            logger.debug(f"Queued batch insert: {len(documents)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error queuing batch insert: {e}")
            return False
    
    def queue_batch_delete(self, document_ids: List[str], priority: int = 2, callback: Callable = None) -> bool:
        """
        Queue a batch delete operation for background processing.
        
        Args:
            document_ids: List of document IDs to delete
            priority: Operation priority (1=high, 2=normal, 3=low)
            callback: Optional callback function to call when complete
            
        Returns:
            bool: True if queued successfully
        """
        try:
            if self.operation_queue.qsize() >= self.max_queue_size:
                self._create_performance_alert(
                    "queue_full",
                    f"Operation queue full: {self.operation_queue.qsize()} items",
                    "high"
                )
                return False
            
            item = OperationQueueItem(
                operation_type="batch_delete",
                data=document_ids,
                priority=priority,
                callback=callback
            )
            
            self.operation_queue.put(item)
            logger.debug(f"Queued batch delete: {len(document_ids)} documents")
            return True
            
        except Exception as e:
            logger.error(f"Error queuing batch delete: {e}")
            return False
    
    def _initialize_connection(self):
        """Initialize Qdrant client connection."""
        try:
            logger.info(f"Initializing Qdrant connection to {self.config.database.qdrant_host}:{self.config.database.qdrant_port}")
            
            # Create client with connection parameters
            self.client = QdrantClient(
                host=self.config.database.qdrant_host,
                port=self.config.database.qdrant_port,
                api_key=self.config.database.qdrant_api_key,
                timeout=30.0,
                prefer_grpc=True
            )
            
            # Test connection
            self._test_connection()
            
            # Ensure collection exists
            self._ensure_collection_exists()
            
            self.is_connected = True
            logger.info("Qdrant connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant connection: {e}")
            self.is_connected = False
            raise Exception(f"Qdrant connection failed: {e}. Please ensure Qdrant is running and accessible.")
    
    def _test_connection(self):
        """Test Qdrant connection."""
        try:
            # Get collections info to test connection
            collections = self.client.get_collections()
            logger.debug(f"Connected to Qdrant. Available collections: {len(collections.collections)}")
        except Exception as e:
            logger.error(f"Qdrant connection test failed: {e}")
            raise
    
    def _ensure_collection_exists(self):
        """Ensure the required collection exists with proper configuration."""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating collection: {self.collection_name}")
                self._create_collection()
            else:
                logger.info(f"Collection {self.collection_name} already exists")
                self._validate_collection_config()
                
        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {e}")
            raise
    
    def _create_collection(self):
        """Create the vector collection with proper configuration."""
        try:
            # Create collection with vector parameters
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            
            # Create payload indexes for efficient filtering
            self._create_payload_indexes()
            
            logger.info(f"Collection {self.collection_name} created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise
    
    def _create_payload_indexes(self):
        """Create payload indexes for efficient filtering."""
        try:
            # Index for source file filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="source_file",
                field_schema=models.PayloadFieldSchema.PARAMS(
                    models.PayloadIndexParams(
                        indexed=True
                    )
                )
            )
            
            # Index for chunk index filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="chunk_index",
                field_schema=models.PayloadFieldSchema.PARAMS(
                    models.PayloadIndexParams(
                        indexed=True
                    )
                )
            )
            
            # Index for created_at filtering
            self.client.create_payload_index(
                collection_name=self.collection_name,
                field_name="created_at",
                field_schema=models.PayloadFieldSchema.PARAMS(
                    models.PayloadIndexParams(
                        indexed=True
                    )
                )
            )
            
            logger.info("Payload indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Failed to create some payload indexes: {e}")
    
    def _validate_collection_config(self):
        """Validate collection configuration matches requirements."""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            config = collection_info.config.params.vectors
            
            if config.size != self.vector_size:
                logger.warning(f"Collection vector size mismatch: expected {self.vector_size}, got {config.size}")
            
            logger.info("Collection configuration validated")
            
        except Exception as e:
            logger.warning(f"Failed to validate collection config: {e}")
    
    def _check_health(self) -> bool:
        """Check service health and connection status."""
        current_time = time.time()
        
        # Skip if checked recently
        if current_time - self.last_health_check < self.health_check_interval:
            return self.is_connected
        
        try:
            # Test connection
            self.client.get_collections()
            self.is_connected = True
            self.last_health_check = current_time
            return True
            
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            self.is_connected = False
            return False
    
    def _track_operation(self, operation: str, start_time: float):
        """Track operation performance metrics with enhanced monitoring."""
        duration = time.time() - start_time
        
        # Update operation counters
        if operation not in self.operation_counters:
            self.operation_counters[operation] = 0
        self.operation_counters[operation] += 1
        
        # Track operation times
        if operation not in self.operation_times:
            self.operation_times[operation] = []
        
        self.operation_times[operation].append(duration)
        self.total_operations += 1
        
        # Check for performance alerts
        if duration * 1000 > self.performance_thresholds['operation_time_ms']:
            self._create_performance_alert(
                "slow_operation",
                f"Slow operation detected: {operation} took {duration*1000:.1f}ms",
                "medium",
                {"operation": operation, "duration_ms": duration * 1000}
            )
    
    def _handle_operation_error(self, operation: str, error: Exception):
        """Handle operation errors and update metrics with enhanced tracking."""
        self.failed_operations += 1
        
        # Update error counters
        if operation not in self.error_counters:
            self.error_counters[operation] = 0
        self.error_counters[operation] += 1
        
        # Check error rate
        total_ops = self.operation_counters.get(operation, 0)
        if total_ops > 0:
            error_rate = self.error_counters[operation] / total_ops
            if error_rate > self.performance_thresholds['error_rate']:
                self._create_performance_alert(
                    "high_error_rate",
                    f"High error rate for {operation}: {error_rate:.1%}",
                    "high",
                    {"operation": operation, "error_rate": error_rate}
                )
        
        logger.error(f"Operation '{operation}' failed: {error}")
    
    def insert_document(self, document: VectorDocument) -> bool:
        """
        Insert a single document into the vector store.
        
        Args:
            document: VectorDocument to insert
            
        Returns:
            bool: True if successful, False otherwise
        """
        start_time = time.time()
        
        try:
            if not self._check_health():
                raise ConnectionError("Vector store not connected")
            
            # Create point for insertion
            point = PointStruct(
                id=document.id,
                vector=document.vector,
                payload={
                    "text": document.text,
                    "metadata": document.metadata,
                    "source_file": document.source_file,
                    "chunk_index": document.chunk_index,
                    "created_at": document.created_at.isoformat(),
                    "updated_at": document.updated_at.isoformat()
                }
            )
            
            # Insert point
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            self._track_operation("insert_document", start_time)
            logger.debug(f"Document inserted successfully: {document.id}")
            return True
            
        except Exception as e:
            self._handle_operation_error("insert_document", e)
            return False
    
    def insert_documents_batch(self, documents: List[VectorDocument]) -> Dict[str, Any]:
        """
        Insert multiple documents in batch for better performance.
        Enhanced with Phase 4.3 optimizations including chunked processing and memory management.
        
        Args:
            documents: List of VectorDocument objects
            
        Returns:
            Dict with operation results
        """
        start_time = time.time()
        results = {
            "total": len(documents),
            "successful": 0,
            "failed": 0,
            "errors": [],
            "processing_time": 0,
            "memory_usage": {}
        }
        
        try:
            if not self._check_health():
                raise ConnectionError("Vector store not connected")
            
            # Phase 4.3 Enhancement: Chunked batch processing for large datasets
            chunk_size = self.batch_size
            total_chunks = (len(documents) + chunk_size - 1) // chunk_size
            
            for i in range(0, len(documents), chunk_size):
                chunk = documents[i:i + chunk_size]
                chunk_start = time.time()
                
                try:
                    # Convert chunk to points
                    points = []
                    for doc in chunk:
                        point = PointStruct(
                            id=doc.id,
                            vector=doc.vector,
                            payload={
                                "text": doc.text,
                                "metadata": doc.metadata,
                                "source_file": doc.source_file,
                                "chunk_index": doc.chunk_index,
                                "created_at": doc.created_at.isoformat(),
                                "updated_at": doc.updated_at.isoformat()
                            }
                        )
                        points.append(point)
                    
                    # Insert chunk
                    self.client.upsert(
                        collection_name=self.collection_name,
                        points=points
                    )
                    
                    results["successful"] += len(chunk)
                    chunk_time = time.time() - chunk_start
                    
                    # Log progress for large batches
                    if total_chunks > 1:
                        chunk_num = (i // chunk_size) + 1
                        logger.debug(f"Batch chunk {chunk_num}/{total_chunks} completed: {len(chunk)} documents in {chunk_time:.3f}s")
                    
                    # Enhanced memory management: force GC after chunks and check memory
                    if len(chunk) > 25:  # Reduced threshold for more frequent cleanup
                        gc.collect()
                        
                        # Check memory usage after large chunks
                        memory_info = self._get_memory_usage()
                        current_memory_mb = memory_info.get("rss_mb", 0)
                        
                        if current_memory_mb > self.memory_threshold_mb * 0.9:
                            logger.warning(f"Memory usage high after chunk {chunk_num}: {current_memory_mb:.1f}MB")
                            self._perform_light_cleanup()
                    
                    # Clear points list to free memory
                    points.clear()
                    
                except Exception as e:
                    results["failed"] += len(chunk)
                    results["errors"].append(f"Chunk {i//chunk_size + 1}: {str(e)}")
                    logger.error(f"Error in batch chunk {i//chunk_size + 1}: {e}")
            
            results["processing_time"] = time.time() - start_time
            results["memory_usage"] = self._get_memory_usage()
            self._track_operation("insert_documents_batch", start_time)
            
            # Performance alert for slow batch operations
            if results["processing_time"] > 10.0:  # 10 seconds threshold
                self._create_performance_alert(
                    "slow_batch_operation",
                    f"Slow batch insert: {len(documents)} documents in {results['processing_time']:.1f}s",
                    "medium",
                    {"documents": len(documents), "time_seconds": results["processing_time"]}
                )
            
            logger.info(f"Batch insert completed: {results['successful']}/{len(documents)} documents in {results['processing_time']:.3f}s")
            
        except Exception as e:
            self._handle_operation_error("insert_documents_batch", e)
            results["failed"] = len(documents)
            results["errors"].append(str(e))
            results["processing_time"] = time.time() - start_time
        
        return results
    
    def search_similar(
        self,
        query_vector: List[float],
        top_k: int = 5,
        score_threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar documents using vector similarity.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of top results to return
            score_threshold: Minimum similarity score
            filters: Optional metadata filters
            
        Returns:
            List of SearchResult objects
        """
        start_time = time.time()
        
        try:
            if not self._check_health():
                raise ConnectionError("Vector store not connected")
            
            # Build search filter
            search_filter = self._build_search_filter(filters) if filters else None
            
            # Perform search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                score_threshold=score_threshold,
                query_filter=search_filter,
                with_payload=True
            )
            
            # Convert to SearchResult objects
            results = []
            for result in search_results:
                search_result = SearchResult(
                    id=result.id,
                    text=result.payload.get("text", ""),
                    score=result.score,
                    metadata=result.payload.get("metadata", {}),
                    source_file=result.payload.get("source_file", ""),
                    chunk_index=result.payload.get("chunk_index", 0)
                )
                results.append(search_result)
            
            self._track_operation("search_similar", start_time)
            logger.debug(f"Search completed: {len(results)} results")
            return results
            
        except Exception as e:
            self._handle_operation_error("search_similar", e)
            return []
    
    def _build_search_filter(self, filters: Dict[str, Any]) -> Filter:
        """Build Qdrant filter from metadata filters."""
        conditions = []
        
        for key, value in filters.items():
            if key == "document_ids":
                # Filter by document IDs - use the document_id field in metadata
                if isinstance(value, list):
                    conditions.append(FieldCondition(key="metadata.document_id", match=MatchAny(any=value)))
                else:
                    conditions.append(FieldCondition(key="metadata.document_id", match=MatchValue(value=value)))
            
            elif key == "source_file":
                if isinstance(value, list):
                    conditions.append(FieldCondition(key=key, match=MatchAny(any=value)))
                else:
                    conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
            
            elif key == "chunk_index":
                if isinstance(value, dict) and "min" in value and "max" in value:
                    conditions.append(FieldCondition(
                        key=key,
                        range=Range(gte=value["min"], lte=value["max"])
                    ))
                else:
                    conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
            
            elif key == "created_at":
                if isinstance(value, dict):
                    range_conditions = {}
                    if "min" in value:
                        range_conditions["gte"] = value["min"]
                    if "max" in value:
                        range_conditions["lte"] = value["max"]
                    conditions.append(FieldCondition(key=key, range=Range(**range_conditions)))
            
            else:
                # Generic field matching
                conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
        
        return Filter(must=conditions) if conditions else None
    
    def get_document(self, document_id: str) -> Optional[VectorDocument]:
        """
        Retrieve a specific document by ID.
        
        Args:
            document_id: Document ID to retrieve
            
        Returns:
            VectorDocument if found, None otherwise
        """
        start_time = time.time()
        
        try:
            if not self._check_health():
                raise ConnectionError("Vector store not connected")
            
            # Retrieve point
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[document_id],
                with_payload=True
            )
            
            if not points:
                return None
            
            point = points[0]
            payload = point.payload
            
            # Convert to VectorDocument
            document = VectorDocument(
                id=point.id,
                text=payload.get("text", ""),
                vector=point.vector,
                metadata=payload.get("metadata", {}),
                source_file=payload.get("source_file", ""),
                chunk_index=payload.get("chunk_index", 0),
                created_at=datetime.fromisoformat(payload.get("created_at", datetime.now().isoformat())),
                updated_at=datetime.fromisoformat(payload.get("updated_at", datetime.now().isoformat()))
            )
            
            self._track_operation("get_document", start_time)
            return document
            
        except Exception as e:
            self._handle_operation_error("get_document", e)
            return None
    
    def update_document(self, document: VectorDocument) -> bool:
        """
        Update an existing document.
        
        Args:
            document: Updated VectorDocument
            
        Returns:
            bool: True if successful, False otherwise
        """
        start_time = time.time()
        
        try:
            if not self._check_health():
                raise ConnectionError("Vector store not connected")
            
            # Update document
            return self.insert_document(document)
            
        except Exception as e:
            self._handle_operation_error("update_document", e)
            return False
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete a document by ID.
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        start_time = time.time()
        
        try:
            if not self._check_health():
                raise ConnectionError("Vector store not connected")
            
            # Delete point
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.PointIdsList(
                    points=[document_id]
                )
            )
            
            self._track_operation("delete_document", start_time)
            logger.debug(f"Document deleted successfully: {document_id}")
            return True
            
        except Exception as e:
            self._handle_operation_error("delete_document", e)
            return False
    
    def delete_documents_by_source(self, source_file: str) -> Dict[str, Any]:
        """
        Delete all documents from a specific source file.
        
        Args:
            source_file: Source file name to delete documents from
            
        Returns:
            Dict with deletion results
        """
        start_time = time.time()
        results = {
            "total_deleted": 0,
            "successful": False,
            "error": None
        }
        
        try:
            if not self._check_health():
                raise ConnectionError("Vector store not connected")
            
            # Delete points by filter
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=Filter(
                        must=[
                            FieldCondition(
                                key="source_file",
                                match=MatchValue(value=source_file)
                            )
                        ]
                    )
                )
            )
            
            results["successful"] = True
            self._track_operation("delete_documents_by_source", start_time)
            logger.info(f"Documents deleted for source: {source_file}")
            
        except Exception as e:
            self._handle_operation_error("delete_documents_by_source", e)
            results["error"] = str(e)
        
        return results
    
    def get_collection_stats(self) -> CollectionStats:
        """
        Get collection statistics and metadata.
        
        Returns:
            CollectionStats object with collection information
        """
        start_time = time.time()
        
        try:
            if not self._check_health():
                raise ConnectionError("Vector store not connected")
            
            # Get collection info
            collection_info = self.client.get_collection(self.collection_name)
            
            # Get collection statistics
            stats = self.client.get_collection(self.collection_name)
            
            # Get unique source files
            source_files = set()
            chunk_count = 0
            
            # Scan collection for metadata (limited to avoid performance issues)
            search_results = self.client.scroll(
                collection_name=self.collection_name,
                limit=1000,
                with_payload=True
            )[0]
            
            for point in search_results:
                source_file = point.payload.get("source_file", "")
                if source_file:
                    source_files.add(source_file)
                chunk_count += 1
            
            collection_stats = CollectionStats(
                total_points=stats.points_count or 0,
                total_vectors=stats.vectors_count or 0,
                collection_size=(stats.vectors_count or 0) * self.vector_size * 4,  # Approximate size in bytes
                last_updated=datetime.now(),
                source_files=list(source_files),
                chunk_count=chunk_count
            )
            
            self._track_operation("get_collection_stats", start_time)
            return collection_stats
            
        except Exception as e:
            self._handle_operation_error("get_collection_stats", e)
            # Return empty stats on error
            return CollectionStats(
                total_points=0,
                total_vectors=0,
                collection_size=0,
                last_updated=datetime.now(),
                source_files=[],
                chunk_count=0
            )
    
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get comprehensive health status of the vector store service.
        Enhanced with Phase 4.3 monitoring and performance metrics.
        
        Returns:
            Dict with health information
        """
        current_time = time.time()
        
        # Calculate performance metrics
        avg_operation_times = {}
        for operation, times in self.operation_times.items():
            if times:
                avg_operation_times[operation] = sum(times) / len(times)
        
        # Get collection stats
        collection_stats = self.get_collection_stats()
        
        # Phase 4.3 Enhancement: Enhanced monitoring metrics
        memory_info = self._get_memory_usage()
        queue_size = self.operation_queue.qsize()
        
        # Calculate error rates by operation
        error_rates = {}
        for operation in self.operation_counters:
            total_ops = self.operation_counters[operation]
            failed_ops = self.error_counters.get(operation, 0)
            if total_ops > 0:
                error_rates[operation] = failed_ops / total_ops
        
        # Determine overall health status
        health_score = 100
        health_issues = []
        
        # Check connection
        if not self.is_connected:
            health_score -= 30
            health_issues.append("Not connected to vector database")
        
        # Check error rate
        overall_error_rate = self.failed_operations / max(self.total_operations, 1)
        if overall_error_rate > 0.1:  # 10% error rate
            health_score -= 20
            health_issues.append(f"High error rate: {overall_error_rate:.1%}")
        
        # Check memory usage
        if memory_info.get("rss_mb", 0) > self.performance_thresholds['memory_usage_mb']:
            health_score -= 15
            health_issues.append(f"High memory usage: {memory_info.get('rss_mb', 0):.1f}MB")
        
        # Check queue size
        if queue_size > self.performance_thresholds['queue_size']:
            health_score -= 10
            health_issues.append(f"Large operation queue: {queue_size} items")
        
        # Determine status based on health score
        if health_score >= 90:
            status = "healthy"
        elif health_score >= 70:
            status = "degraded"
        elif health_score >= 50:
            status = "unhealthy"
        else:
            status = "critical"
        
        health_status = {
            "status": status,
            "health_score": health_score,
            "health_issues": health_issues,
            "connected": self.is_connected,
            "collection_name": self.collection_name,
            "vector_size": self.vector_size,
            "uptime": current_time - self.start_time,
            "total_operations": self.total_operations,
            "failed_operations": self.failed_operations,
            "success_rate": (self.total_operations - self.failed_operations) / max(self.total_operations, 1),
            "avg_operation_times": avg_operation_times,
            "collection_stats": asdict(collection_stats),
            "last_health_check": self.last_health_check,
            "memory_usage": memory_info,
            "queue_size": queue_size,
            "error_rates": error_rates,
            "performance_alerts": len(self.performance_alerts),
            "recent_alerts": [asdict(alert) for alert in self.performance_alerts[-5:]],  # Last 5 alerts
            "background_services": {
                "queue_worker_running": self.queue_running,
                "memory_monitor_running": self._memory_monitor_running
            }
        }
        
        return health_status
    
    def get_detailed_metrics(self) -> Dict[str, Any]:
        """
        Get detailed performance metrics for monitoring and analysis.
        
        Returns:
            Dict with detailed metrics
        """
        current_time = time.time()
        
        # Calculate percentiles for operation times
        operation_percentiles = {}
        for operation, times in self.operation_times.items():
            if times:
                sorted_times = sorted(times)
                operation_percentiles[operation] = {
                    "p50": sorted_times[len(sorted_times) // 2],
                    "p90": sorted_times[int(len(sorted_times) * 0.9)],
                    "p95": sorted_times[int(len(sorted_times) * 0.95)],
                    "p99": sorted_times[int(len(sorted_times) * 0.99)] if len(sorted_times) > 1 else sorted_times[0],
                    "min": min(times),
                    "max": max(times),
                    "count": len(times)
                }
        
        # Memory usage trends
        memory_trend = []
        if len(self.memory_usage_history) > 1:
            recent_history = self.memory_usage_history[-10:]  # Last 10 measurements
            for entry in recent_history:
                memory_trend.append({
                    "timestamp": entry["timestamp"].isoformat(),
                    "memory_mb": entry["memory_mb"],
                    "memory_percent": entry["memory_percent"]
                })
        
        detailed_metrics = {
            "timestamp": datetime.now().isoformat(),
            "operation_percentiles": operation_percentiles,
            "memory_trend": memory_trend,
            "operation_counters": self.operation_counters,
            "error_counters": self.error_counters,
            "queue_metrics": {
                "current_size": self.operation_queue.qsize(),
                "max_size": self.max_queue_size,
                "utilization": self.operation_queue.qsize() / self.max_queue_size
            },
            "performance_thresholds": self.performance_thresholds,
            "uptime_seconds": current_time - self.start_time,
            "gc_stats": {
                "last_gc_time": self.last_gc_time,
                "gc_interval": self.gc_interval
            }
        }
        
        return detailed_metrics
    
    def get_performance_alerts(self, severity: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get performance alerts with optional filtering.
        
        Args:
            severity: Filter by severity ('low', 'medium', 'high', 'critical')
            limit: Maximum number of alerts to return
            
        Returns:
            List of alert dictionaries
        """
        alerts = self.performance_alerts
        
        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]
        
        # Return most recent alerts up to limit
        return [asdict(alert) for alert in alerts[-limit:]]
    
    def clear_performance_alerts(self):
        """Clear all performance alerts."""
        self.performance_alerts.clear()
        logger.info("Performance alerts cleared")
    
    def get_storage_monitoring(self) -> Dict[str, Any]:
        """
        Get storage monitoring information.
        
        Returns:
            Dict with storage metrics
        """
        try:
            if not self._check_health():
                raise ConnectionError("Vector store not connected")
            
            # Get collection info
            collection_info = self.client.get_collection(self.collection_name)
            
            # Calculate storage metrics
            total_points = collection_info.points_count
            total_vectors = collection_info.vectors_count
            estimated_size = total_vectors * self.vector_size * 4  # Approximate size in bytes
            
            # Get storage path info if available
            storage_info = {
                "storage_type": "qdrant",
                "total_documents": total_points,
                "total_vectors": total_vectors,
                "estimated_size_bytes": estimated_size,
                "estimated_size_mb": estimated_size / (1024 * 1024),
                "vector_size": self.vector_size,
                "collection_name": self.collection_name,
                "collection_status": collection_info.status,
                "optimizers_status": collection_info.optimizers_status
            }
            
            return storage_info
            
        except Exception as e:
            logger.error(f"Error getting storage monitoring: {e}")
            return {
                "storage_type": "unknown",
                "error": str(e),
                "collection_name": self.collection_name
            }
    
    def _get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage information."""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "percent": process.memory_percent()
            }
        except ImportError:
            return {"error": "psutil not available"}
        except Exception as e:
            return {"error": str(e)}
    
    def clear_collection(self) -> bool:
        """
        Clear all documents from the collection.
        
        Returns:
            bool: True if successful, False otherwise
        """
        start_time = time.time()
        
        try:
            if not self._check_health():
                raise ConnectionError("Vector store not connected")
            
            # Delete all points
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=Filter(must=[])
                )
            )
            
            self._track_operation("clear_collection", start_time)
            logger.info("Collection cleared successfully")
            return True
            
        except Exception as e:
            self._handle_operation_error("clear_collection", e)
            return False
    

    

    
    def list_documents(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        List documents in the vector store with pagination.
        
        Args:
            limit: Maximum number of documents to return
            offset: Number of documents to skip
            
        Returns:
            List of document metadata dictionaries
        """
        start_time = time.time()
        
        try:
            if not self._check_health():
                raise ConnectionError("Vector store not connected")
            
            # Get documents from Qdrant
            search_results = self.client.scroll(
                collection_name=self.collection_name,
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
            
            result = list(source_files.values())
            
            self._track_operation("list_documents", start_time)
            return result
            
        except Exception as e:
            self._handle_operation_error("list_documents", e)
            return []

    def close(self):
        """Close the vector store connection and stop background services."""
        try:
            # Stop background services
            self.queue_running = False
            self._memory_monitor_running = False
            
            # Wait for background threads to finish
            if self.queue_worker_thread and self.queue_worker_thread.is_alive():
                self.queue_worker_thread.join(timeout=5.0)
            
            if self._memory_monitor_thread and self._memory_monitor_thread.is_alive():
                self._memory_monitor_thread.join(timeout=5.0)
            
            # Close Qdrant client
            if self.client:
                self.client.close()
            
            self.is_connected = False
            logger.info("Vector store connection and background services closed")
            
        except Exception as e:
            logger.warning(f"Error closing vector store connection: {e}")
    
    def batch_search(
        self,
        query_vectors: List[List[float]],
        top_k: int = 5,
        score_threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[List[SearchResult]]:
        """
        Perform batch search for multiple query vectors.
        Enhanced with Phase 4.3 optimizations for better performance.
        
        Args:
            query_vectors: List of query embedding vectors
            top_k: Number of top results to return per query
            score_threshold: Minimum similarity score
            filters: Optional metadata filters
            
        Returns:
            List of search result lists (one list per query)
        """
        start_time = time.time()
        
        try:
            if not self._check_health():
                raise ConnectionError("Vector store not connected")
            
            # Phase 4.3 Enhancement: Optimized batch search
            all_results = []
            
            # Process queries in chunks for better performance
            chunk_size = min(10, len(query_vectors))  # Process up to 10 queries at once
            
            for i in range(0, len(query_vectors), chunk_size):
                chunk_vectors = query_vectors[i:i + chunk_size]
                chunk_start = time.time()
                
                try:
                    # Build search filter
                    search_filter = self._build_search_filter(filters) if filters else None
                    
                    # Perform batch search
                    batch_results = self.client.search_batch(
                        collection_name=self.collection_name,
                        requests=[
                            models.SearchRequest(
                                vector=vector,
                                limit=top_k,
                                score_threshold=score_threshold,
                                query_filter=search_filter,
                                with_payload=True
                            ) for vector in chunk_vectors
                        ]
                    )
                    
                    # Convert results
                    for batch_result in batch_results:
                        results = []
                        for result in batch_result:
                            search_result = SearchResult(
                                id=result.id,
                                text=result.payload.get("text", ""),
                                score=result.score,
                                metadata=result.payload.get("metadata", {}),
                                source_file=result.payload.get("source_file", ""),
                                chunk_index=result.payload.get("chunk_index", 0)
                            )
                            results.append(search_result)
                        all_results.append(results)
                    
                    chunk_time = time.time() - chunk_start
                    logger.debug(f"Batch search chunk {i//chunk_size + 1} completed: {len(chunk_vectors)} queries in {chunk_time:.3f}s")
                    
                except Exception as e:
                    logger.error(f"Error in batch search chunk {i//chunk_size + 1}: {e}")
                    # Add empty results for failed queries
                    for _ in chunk_vectors:
                        all_results.append([])
            
            self._track_operation("batch_search", start_time)
            
            # Performance alert for slow batch searches
            total_time = time.time() - start_time
            if total_time > 5.0:  # 5 seconds threshold
                self._create_performance_alert(
                    "slow_batch_search",
                    f"Slow batch search: {len(query_vectors)} queries in {total_time:.1f}s",
                    "medium",
                    {"queries": len(query_vectors), "time_seconds": total_time}
                )
            
            logger.info(f"Batch search completed: {len(query_vectors)} queries in {total_time:.3f}s")
            return all_results
            
        except Exception as e:
            self._handle_operation_error("batch_search", e)
            # Return empty results for all queries on error
            return [[] for _ in query_vectors]


# Utility functions for document conversion
def create_vector_document(
    text: str,
    vector: List[float],
    metadata: Dict[str, Any],
    source_file: str,
    chunk_index: int,
    document_id: Optional[str] = None
) -> VectorDocument:
    """
    Create a VectorDocument from components.
    
    Args:
        text: Document text content
        vector: Document embedding vector
        metadata: Document metadata
        source_file: Source file name
        chunk_index: Chunk index within the document
        document_id: Optional document ID (generated if not provided)
        
    Returns:
        VectorDocument object
    """
    if document_id is None:
        # Generate unique UUID for Qdrant compatibility
        document_id = str(uuid.uuid4())
    
    current_time = datetime.now()
    
    return VectorDocument(
        id=document_id,
        text=text,
        vector=vector,
        metadata=metadata,
        source_file=source_file,
        chunk_index=chunk_index,
        created_at=current_time,
        updated_at=current_time
    )


def convert_document_chunks_to_vector_documents(
    chunks: List[Any],
    vectors: List[List[float]],
    source_file: str,
    base_metadata: Optional[Dict[str, Any]] = None
) -> List[VectorDocument]:
    """
    Convert document chunks and vectors to VectorDocument objects.
    
    Args:
        chunks: List of document chunks (any format with 'text' attribute)
        vectors: List of embedding vectors
        source_file: Source file name
        base_metadata: Base metadata to include in all documents
        
    Returns:
        List of VectorDocument objects
    """
    if len(chunks) != len(vectors):
        raise ValueError("Number of chunks must match number of vectors")
    
    base_metadata = base_metadata or {}
    vector_documents = []
    
    for i, (chunk, vector) in enumerate(zip(chunks, vectors)):
        # Extract text from chunk
        if hasattr(chunk, 'text'):
            text = chunk.text
        elif isinstance(chunk, dict):
            text = chunk.get('text', '')
        else:
            text = str(chunk)
        
        # Extract chunk metadata
        chunk_metadata = {}
        if hasattr(chunk, 'metadata'):
            chunk_metadata = chunk.metadata
        elif isinstance(chunk, dict):
            chunk_metadata = chunk.get('metadata', {})
        
        # Combine base and chunk metadata
        combined_metadata = {**base_metadata, **chunk_metadata}
        
        # Create vector document
        vector_doc = create_vector_document(
            text=text,
            vector=vector,
            metadata=combined_metadata,
            source_file=source_file,
            chunk_index=i,
            document_id=None  # Auto-generate ID
        )
        
        vector_documents.append(vector_doc)
    
    return vector_documents
