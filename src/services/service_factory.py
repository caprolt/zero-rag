"""
ZeroRAG Service Factory

This module provides a factory pattern for managing AI services initialization,
configuration, and lifecycle management with comprehensive error handling.
"""

import logging
import threading
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

from ..config import get_config
from ..models.embeddings import EmbeddingService
from ..models.llm import LLMService, LLMProvider
from .document_processor import DocumentProcessor
from .vector_store import VectorStoreService
from .rag_pipeline import RAGPipeline

logger = logging.getLogger(__name__)


class ServiceStatus(str, Enum):
    """Service status enumeration."""
    INITIALIZING = "initializing"
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class ServiceInfo:
    """Service information container."""
    name: str
    status: ServiceStatus
    health_data: Dict[str, Any]
    last_check: float
    error_count: int
    initialization_time: Optional[float] = None


class ServiceFactory:
    """
    Factory for managing AI services with health monitoring and graceful degradation.
    
    Features:
    - Centralized service initialization
    - Health monitoring and status tracking
    - Graceful degradation on failures
    - Service lifecycle management
    - Performance metrics collection
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the service factory."""
        self.config = get_config() if config is None else config
        
        # Service instances
        self.embedding_service: Optional[EmbeddingService] = None
        self.llm_service: Optional[LLMService] = None
        self.document_processor: Optional[DocumentProcessor] = None
        self.vector_store: Optional[VectorStoreService] = None
        self.rag_pipeline: Optional[RAGPipeline] = None
        
        # Service status tracking
        self.services: Dict[str, ServiceInfo] = {}
        self.initialization_lock = threading.Lock()
        self.health_check_lock = threading.Lock()
        
        # Performance tracking
        self.total_requests = 0
        self.failed_requests = 0
        self.start_time = time.time()
        
        # Initialization state
        self._initializing = False
        self._initialized = False
        
        # Initialize services
        self._initialize_services()
    
    def _initialize_services(self):
        """Initialize all AI services."""
        # Prevent recursive initialization
        if self._initializing or self._initialized:
            logger.info("Services already initialized or initializing, skipping...")
            return
        
        with self.initialization_lock:
            if self._initializing or self._initialized:
                return
            
            self._initializing = True
            logger.info("Initializing ZeroRAG services...")
            
            try:
                # Initialize embedding service
                self._initialize_embedding_service()
                
                # Initialize LLM service
                self._initialize_llm_service()
                
                # Initialize document processor
                self._initialize_document_processor()
                
                # Initialize vector store
                self._initialize_vector_store()
                
                # Initialize RAG pipeline
                self._initialize_rag_pipeline()
                
                # Mark as initialized
                self._initialized = True
                logger.info("Service initialization completed")
                
                # Perform initial health check after initialization is complete
                try:
                    self._perform_health_check()
                except Exception as e:
                    logger.warning(f"Initial health check failed: {e}")
                
            except Exception as e:
                logger.error(f"Service initialization failed: {e}")
                self._initialized = False
                raise
            finally:
                self._initializing = False
    
    def _initialize_embedding_service(self):
        """Initialize the embedding service."""
        try:
            logger.info("Initializing embedding service...")
            start_time = time.time()
            
            self.embedding_service = EmbeddingService()
            init_time = time.time() - start_time
            
            # Register service
            self.services["embedding"] = ServiceInfo(
                name="embedding",
                status=ServiceStatus.INITIALIZING,
                health_data={},
                last_check=time.time(),
                error_count=0,
                initialization_time=init_time
            )
            
            logger.info(f"Embedding service initialized successfully in {init_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize embedding service: {e}")
            self.services["embedding"] = ServiceInfo(
                name="embedding",
                status=ServiceStatus.ERROR,
                health_data={"error": str(e)},
                last_check=time.time(),
                error_count=1,
                initialization_time=None
            )
    
    def _initialize_llm_service(self):
        """Initialize the LLM service."""
        try:
            logger.info("Initializing LLM service...")
            start_time = time.time()
            
            self.llm_service = LLMService()
            init_time = time.time() - start_time
            
            # Register service
            self.services["llm"] = ServiceInfo(
                name="llm",
                status=ServiceStatus.INITIALIZING,
                health_data={},
                last_check=time.time(),
                error_count=0,
                initialization_time=init_time
            )
            
            logger.info(f"LLM service initialized successfully in {init_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}")
            self.services["llm"] = ServiceInfo(
                name="llm",
                status=ServiceStatus.ERROR,
                health_data={"error": str(e)},
                last_check=time.time(),
                error_count=1,
                initialization_time=None
            )
    
    def _initialize_document_processor(self):
        """Initialize the document processor service."""
        try:
            logger.info("Initializing document processor...")
            start_time = time.time()
            
            self.document_processor = DocumentProcessor()
            init_time = time.time() - start_time
            
            # Register service
            self.services["document_processor"] = ServiceInfo(
                name="document_processor",
                status=ServiceStatus.INITIALIZING,
                health_data={},
                last_check=time.time(),
                error_count=0,
                initialization_time=init_time
            )
            
            logger.info(f"Document processor initialized successfully in {init_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize document processor: {e}")
            self.services["document_processor"] = ServiceInfo(
                name="document_processor",
                status=ServiceStatus.ERROR,
                health_data={"error": str(e)},
                last_check=time.time(),
                error_count=1,
                initialization_time=None
            )
    
    def _initialize_vector_store(self):
        """Initialize the vector store service."""
        try:
            logger.info("Initializing vector store service...")
            start_time = time.time()
            
            self.vector_store = VectorStoreService()
            init_time = time.time() - start_time
            
            # Register service
            self.services["vector_store"] = ServiceInfo(
                name="vector_store",
                status=ServiceStatus.INITIALIZING,
                health_data={},
                last_check=time.time(),
                error_count=0,
                initialization_time=init_time
            )
            
            logger.info(f"Vector store service initialized successfully in {init_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize vector store service: {e}")
            self.services["vector_store"] = ServiceInfo(
                name="vector_store",
                status=ServiceStatus.ERROR,
                health_data={"error": str(e)},
                last_check=time.time(),
                error_count=1,
                initialization_time=None
            )
    
    def _initialize_rag_pipeline(self):
        """Initialize the RAG pipeline service."""
        try:
            logger.info("Initializing RAG pipeline...")
            start_time = time.time()
            
            self.rag_pipeline = RAGPipeline(self)
            init_time = time.time() - start_time
            
            # Register service
            self.services["rag_pipeline"] = ServiceInfo(
                name="rag_pipeline",
                status=ServiceStatus.INITIALIZING,
                health_data={},
                last_check=time.time(),
                error_count=0,
                initialization_time=init_time
            )
            
            logger.info(f"RAG pipeline initialized successfully in {init_time:.2f}s")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG pipeline: {e}")
            self.services["rag_pipeline"] = ServiceInfo(
                name="rag_pipeline",
                status=ServiceStatus.ERROR,
                health_data={"error": str(e)},
                last_check=time.time(),
                error_count=1,
                initialization_time=None
            )
    
    def _perform_health_check(self):
        """Perform health check on all services."""
        with self.health_check_lock:
            logger.info("Performing health check on all services...")
            
            # Check embedding service
            if self.embedding_service:
                try:
                    health = self.embedding_service.health_check()
                    self.services["embedding"].health_data = health
                    self.services["embedding"].status = (
                        ServiceStatus.HEALTHY if health.get("status") == "healthy" 
                        else ServiceStatus.UNHEALTHY
                    )
                    self.services["embedding"].last_check = time.time()
                    
                    if self.services["embedding"].status == ServiceStatus.HEALTHY:
                        logger.info("Embedding service is healthy")
                    else:
                        logger.warning(f"Embedding service is unhealthy: {health}")
                        
                except Exception as e:
                    logger.error(f"Embedding service health check failed: {e}")
                    self.services["embedding"].status = ServiceStatus.ERROR
                    self.services["embedding"].health_data = {"error": str(e)}
                    self.services["embedding"].error_count += 1
                    self.services["embedding"].last_check = time.time()
            
            # Check LLM service
            if self.llm_service:
                try:
                    health = self.llm_service.health_check()
                    self.services["llm"].health_data = health
                    self.services["llm"].status = (
                        ServiceStatus.HEALTHY if health.get("status") == "healthy" 
                        else ServiceStatus.UNHEALTHY
                    )
                    self.services["llm"].last_check = time.time()
                    
                    if self.services["llm"].status == ServiceStatus.HEALTHY:
                        logger.info("LLM service is healthy")
                    else:
                        logger.warning(f"LLM service is unhealthy: {health}")
                        
                except Exception as e:
                    logger.error(f"LLM service health check failed: {e}")
                    self.services["llm"].status = ServiceStatus.ERROR
                    self.services["llm"].health_data = {"error": str(e)}
                    self.services["llm"].error_count += 1
                    self.services["llm"].last_check = time.time()
            
            # Check document processor
            if self.document_processor:
                try:
                    health = self.document_processor.health_check()
                    self.services["document_processor"].health_data = health
                    self.services["document_processor"].status = (
                        ServiceStatus.HEALTHY if health.get("status") == "healthy" 
                        else ServiceStatus.UNHEALTHY
                    )
                    self.services["document_processor"].last_check = time.time()
                    
                    if self.services["document_processor"].status == ServiceStatus.HEALTHY:
                        logger.info("Document processor is healthy")
                    else:
                        logger.warning(f"Document processor is unhealthy: {health}")
                        
                except Exception as e:
                    logger.error(f"Document processor health check failed: {e}")
                    self.services["document_processor"].status = ServiceStatus.ERROR
                    self.services["document_processor"].health_data = {"error": str(e)}
                    self.services["document_processor"].error_count += 1
                    self.services["document_processor"].last_check = time.time()
            
            # Check vector store
            if self.vector_store:
                try:
                    health = self.vector_store.get_health_status()
                    self.services["vector_store"].health_data = health
                    self.services["vector_store"].status = (
                        ServiceStatus.HEALTHY if health.get("status") == "healthy" 
                        else ServiceStatus.UNHEALTHY
                    )
                    self.services["vector_store"].last_check = time.time()
                    
                    if self.services["vector_store"].status == ServiceStatus.HEALTHY:
                        logger.info("Vector store is healthy")
                    else:
                        logger.warning(f"Vector store is unhealthy: {health}")
                        
                except Exception as e:
                    logger.error(f"Vector store health check failed: {e}")
                    self.services["vector_store"].status = ServiceStatus.ERROR
                    self.services["vector_store"].health_data = {"error": str(e)}
                    self.services["vector_store"].error_count += 1
                    self.services["vector_store"].last_check = time.time()
            
            # Check RAG pipeline (skip during initialization to avoid infinite loop)
            if self.rag_pipeline:
                try:
                    # For now, just check if the RAG pipeline object exists
                    # Don't call its health_check method to avoid infinite loop
                    self.services["rag_pipeline"].health_data = {"status": "available"}
                    self.services["rag_pipeline"].status = ServiceStatus.HEALTHY
                    self.services["rag_pipeline"].last_check = time.time()
                    logger.info("RAG pipeline is available")
                        
                except Exception as e:
                    logger.error(f"RAG pipeline check failed: {e}")
                    self.services["rag_pipeline"].status = ServiceStatus.ERROR
                    self.services["rag_pipeline"].health_data = {"error": str(e)}
                    self.services["rag_pipeline"].error_count += 1
                    self.services["rag_pipeline"].last_check = time.time()
    
    def get_embedding_service(self) -> Optional[EmbeddingService]:
        """Get the embedding service if available and healthy."""
        if (self.embedding_service and 
            self.services.get("embedding", {}).status == ServiceStatus.HEALTHY):
            return self.embedding_service
        return None
    
    def get_llm_service(self) -> Optional[LLMService]:
        """Get the LLM service if available and healthy."""
        if (self.llm_service and 
            self.services.get("llm", {}).status == ServiceStatus.HEALTHY):
            return self.llm_service
        return None
    
    def get_document_processor(self) -> Optional[DocumentProcessor]:
        """Get the document processor if available and healthy."""
        if (self.document_processor and 
            self.services.get("document_processor", {}).status == ServiceStatus.HEALTHY):
            return self.document_processor
        return None
    
    def get_vector_store(self) -> Optional[VectorStoreService]:
        """Get the vector store service if available (even if degraded)."""
        if self.vector_store:
            return self.vector_store
        return None
    
    def get_rag_pipeline(self) -> Optional[RAGPipeline]:
        """Get the RAG pipeline service if available (even if degraded)."""
        if self.rag_pipeline:
            return self.rag_pipeline
        return None
    
    def get_service_status(self, service_name: str) -> Optional[ServiceInfo]:
        """Get status information for a specific service."""
        return self.services.get(service_name)
    
    def get_all_service_status(self) -> Dict[str, ServiceInfo]:
        """Get status information for all services."""
        return self.services.copy()
    
    def is_service_healthy(self, service_name: str) -> bool:
        """Check if a specific service is healthy."""
        service_info = self.services.get(service_name)
        return service_info is not None and service_info.status == ServiceStatus.HEALTHY
    
    def are_all_services_healthy(self) -> bool:
        """Check if all services are healthy."""
        return all(
            service_info.status == ServiceStatus.HEALTHY 
            for service_info in self.services.values()
        )
    
    def get_healthy_services(self) -> List[str]:
        """Get list of healthy service names."""
        return [
            name for name, info in self.services.items()
            if info.status == ServiceStatus.HEALTHY
        ]
    
    def perform_health_check(self) -> Dict[str, Any]:
        """Perform health check and return comprehensive status."""
        self._perform_health_check()
        
        # Calculate overall metrics
        total_requests = self.total_requests
        failed_requests = self.failed_requests
        success_rate = (
            (total_requests - failed_requests) / total_requests 
            if total_requests > 0 else 1.0
        )
        
        uptime = time.time() - self.start_time
        
        return {
            "overall_status": "healthy" if self.are_all_services_healthy() else "unhealthy",
            "services": {
                name: {
                    "status": info.status.value,
                    "health_data": info.health_data,
                    "last_check": info.last_check,
                    "error_count": info.error_count,
                    "initialization_time": info.initialization_time
                }
                for name, info in self.services.items()
            },
            "metrics": {
                "total_requests": total_requests,
                "failed_requests": failed_requests,
                "success_rate": success_rate,
                "uptime": uptime
            },
            "healthy_services": self.get_healthy_services(),
            "timestamp": time.time()
        }
    
    def record_request(self, service_name: str, success: bool = True):
        """Record a request for metrics tracking."""
        self.total_requests += 1
        if not success:
            self.failed_requests += 1
            if service_name in self.services:
                self.services[service_name].error_count += 1
    
    def restart_service(self, service_name: str) -> bool:
        """Attempt to restart a failed service."""
        logger.info(f"Attempting to restart service: {service_name}")
        
        if service_name == "embedding":
            return self._restart_embedding_service()
        elif service_name == "llm":
            return self._restart_llm_service()
        elif service_name == "document_processor":
            return self._restart_document_processor()
        else:
            logger.error(f"Unknown service: {service_name}")
            return False
    
    def _restart_embedding_service(self) -> bool:
        """Restart the embedding service."""
        try:
            logger.info("Restarting embedding service...")
            
            # Clean up old service
            if self.embedding_service:
                del self.embedding_service
                self.embedding_service = None
            
            # Reinitialize
            self._initialize_embedding_service()
            
            # Check health
            if self.embedding_service:
                health = self.embedding_service.health_check()
                if health.get("status") == "healthy":
                    logger.info("Embedding service restarted successfully")
                    return True
            
            logger.error("Embedding service restart failed")
            return False
            
        except Exception as e:
            logger.error(f"Failed to restart embedding service: {e}")
            return False
    
    def _restart_llm_service(self) -> bool:
        """Restart the LLM service."""
        try:
            logger.info("Restarting LLM service...")
            
            # Clean up old service
            if self.llm_service:
                del self.llm_service
                self.llm_service = None
            
            # Reinitialize
            self._initialize_llm_service()
            
            # Check health
            if self.llm_service:
                health = self.llm_service.health_check()
                if health.get("status") == "healthy":
                    logger.info("LLM service restarted successfully")
                    return True
            
            logger.error("LLM service restart failed")
            return False
            
        except Exception as e:
            logger.error(f"Failed to restart LLM service: {e}")
            return False
    
    def _restart_document_processor(self) -> bool:
        """Restart the document processor service."""
        try:
            logger.info("Restarting document processor...")
            
            # Clean up old service
            if self.document_processor:
                del self.document_processor
                self.document_processor = None
            
            # Reinitialize
            self._initialize_document_processor()
            
            # Check health
            if self.document_processor:
                health = self.document_processor.health_check()
                if health.get("status") == "healthy":
                    logger.info("Document processor restarted successfully")
                    return True
            
            logger.error("Document processor restart failed")
            return False
            
        except Exception as e:
            logger.error(f"Failed to restart document processor: {e}")
            return False
    
    def get_service_summary(self) -> Dict[str, Any]:
        """Get a summary of all services."""
        healthy_services = self.get_healthy_services()
        total_services = len(self.services)
        
        summary = {
            "total_services": total_services,
            "healthy_services": len(healthy_services),
            "unhealthy_services": total_services - len(healthy_services),
            "overall_status": "healthy" if len(healthy_services) == total_services else "unhealthy",
            "uptime": time.time() - self.start_time,
            "total_requests": self.total_requests,
            "failed_requests": self.failed_requests,
            "success_rate": (self.total_requests - self.failed_requests) / max(self.total_requests, 1),
            "service_details": {},
            "service_metrics": {}
        }
        
        for name, info in self.services.items():
            # Service details
            summary["service_details"][name] = {
                "status": info.status.value,
                "error_count": info.error_count,
                "last_check": info.last_check,
                "initialization_time": info.initialization_time
            }
            
            # Service metrics (simplified for now)
            summary["service_metrics"][name] = {
                "requests": 0,  # TODO: Track per-service requests
                "errors": info.error_count,
                "success_rate": 1.0 if info.error_count == 0 else 0.0
            }
        
        return summary
    
    def shutdown(self):
        """Gracefully shutdown all services."""
        logger.info("Shutting down ZeroRAG services...")
        
        # Clean up services
        if self.embedding_service:
            del self.embedding_service
            self.embedding_service = None
        
        if self.llm_service:
            del self.llm_service
            self.llm_service = None
        
        # Clear service registry
        self.services.clear()
        
        logger.info("ZeroRAG services shutdown completed")


# Global service factory instance
_service_factory: Optional[ServiceFactory] = None
_service_factory_lock = threading.Lock()


def get_service_factory(config: Optional[Dict[str, Any]] = None) -> ServiceFactory:
    """Get the global service factory instance."""
    global _service_factory
    
    with _service_factory_lock:
        if _service_factory is None:
            _service_factory = ServiceFactory(config)
        elif config is not None and _service_factory.config != config:
            # Only recreate if config actually changed
            logger.info("Config changed, recreating service factory...")
            shutdown_service_factory()
            _service_factory = ServiceFactory(config)
        
        return _service_factory


def shutdown_service_factory():
    """Shutdown the global service factory."""
    global _service_factory
    
    with _service_factory_lock:
        if _service_factory:
            _service_factory.shutdown()
            _service_factory = None
