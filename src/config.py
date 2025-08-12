"""
ZeroRAG Configuration Management

This module provides centralized configuration management for the ZeroRAG system,
including environment variable loading, validation, and logging setup.
"""

import os
import logging
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv


class DatabaseConfig(BaseSettings):
    """Database configuration settings."""
    
    # Qdrant Vector Database
    qdrant_host: str = Field(default="localhost", env="QDRANT_HOST")
    qdrant_port: int = Field(default=6333, env="QDRANT_PORT")
    qdrant_api_key: Optional[str] = Field(default=None, env="QDRANT_API_KEY")
    qdrant_collection_name: str = Field(default="zero_rag_documents", env="QDRANT_COLLECTION_NAME")
    qdrant_vector_size: int = Field(default=384, env="QDRANT_VECTOR_SIZE")
    
    # Redis Configuration
    redis_host: str = Field(default="localhost", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_cache_ttl: int = Field(default=3600, env="REDIS_CACHE_TTL")
    
    @field_validator("qdrant_vector_size")
    @classmethod
    def validate_vector_size(cls, v):
        if v <= 0:
            raise ValueError("Vector size must be positive")
        return v
    
    @field_validator("redis_cache_ttl")
    @classmethod
    def validate_cache_ttl(cls, v):
        if v < 0:
            raise ValueError("Cache TTL must be non-negative")
        return v


class AIModelConfig(BaseSettings):
    """AI model configuration settings."""
    
    # Ollama Configuration
    ollama_host: str = Field(default="http://localhost:11434", env="OLLAMA_HOST")
    ollama_model: str = Field(default="llama3.2:1b", env="OLLAMA_MODEL")
    ollama_timeout: int = Field(default=30, env="OLLAMA_TIMEOUT")
    ollama_max_tokens: int = Field(default=2048, env="OLLAMA_MAX_TOKENS")
    ollama_temperature: float = Field(default=0.7, env="OLLAMA_TEMPERATURE")
    
    # HuggingFace Fallback Configuration
    hf_model_name: str = Field(default="microsoft/DialoGPT-small", env="HF_MODEL_NAME")
    hf_model_file: str = Field(default="llama-3.2-1b-chat.Q4_K_M.gguf", env="HF_MODEL_FILE")
    hf_device: str = Field(default="cpu", env="HF_DEVICE")
    hf_max_length: int = Field(default=2048, env="HF_MAX_LENGTH")
    
    # Embedding Model Configuration
    embedding_model_name: str = Field(default="sentence-transformers/all-MiniLM-L6-v2", env="EMBEDDING_MODEL_NAME")
    embedding_device: str = Field(default="cpu", env="EMBEDDING_DEVICE")
    embedding_batch_size: int = Field(default=32, env="EMBEDDING_BATCH_SIZE")
    embedding_max_length: int = Field(default=512, env="EMBEDDING_MAX_LENGTH")
    
    @field_validator("ollama_temperature")
    @classmethod
    def validate_temperature(cls, v):
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v
    
    @field_validator("embedding_batch_size")
    @classmethod
    def validate_batch_size(cls, v):
        if v <= 0:
            raise ValueError("Batch size must be positive")
        return v


class APIConfig(BaseSettings):
    """API configuration settings."""
    
    host: str = Field(default="127.0.0.1", env="API_HOST")
    port: int = Field(default=8000, env="API_PORT")
    workers: int = Field(default=1, env="API_WORKERS")
    reload: bool = Field(default=True, env="API_RELOAD")
    log_level: str = Field(default="info", env="API_LOG_LEVEL")
    
    # Security
    enable_cors: bool = Field(default=True, env="ENABLE_CORS")
    cors_origins: List[str] = Field(default=["http://localhost:8501", "http://127.0.0.1:8501"], env="CORS_ORIGINS")
    api_key: Optional[str] = Field(default=None, env="API_KEY")
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    
    @field_validator("port")
    @classmethod
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return [v]
        return v


class DocumentConfig(BaseSettings):
    """Document processing configuration settings."""
    
    max_file_size: str = Field(default="50MB", env="MAX_FILE_SIZE")
    supported_formats: str = Field(default="txt,csv,md", env="SUPPORTED_FORMATS")
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    max_chunks_per_document: int = Field(default=1000, env="MAX_CHUNKS_PER_DOCUMENT")
    
    @field_validator("supported_formats")
    @classmethod
    def parse_supported_formats(cls, v):
        if isinstance(v, str):
            # Handle both JSON array format and comma-separated string
            if v.startswith('[') and v.endswith(']'):
                try:
                    import json
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass
            # Handle comma-separated string
            return [fmt.strip() for fmt in v.split(",")]
        return v
    
    @field_validator("max_file_size")
    @classmethod
    def validate_file_size(cls, v):
        # Convert MB to bytes for validation
        if v.endswith("MB"):
            size_mb = int(v[:-2])
            if size_mb <= 0:
                raise ValueError("File size must be positive")
        return v
    
    @field_validator("chunk_overlap")
    @classmethod
    def validate_chunk_overlap(cls, v, info):
        if "chunk_size" in info.data and v >= info.data["chunk_size"]:
            raise ValueError("Chunk overlap must be less than chunk size")
        return v


class RAGConfig(BaseSettings):
    """RAG pipeline configuration settings."""
    
    top_k_results: int = Field(default=5, env="TOP_K_RESULTS")
    similarity_threshold: float = Field(default=0.7, env="SIMILARITY_THRESHOLD")
    max_context_length: int = Field(default=4000, env="MAX_CONTEXT_LENGTH")
    enable_streaming: bool = Field(default=True, env="ENABLE_STREAMING")
    
    @field_validator("similarity_threshold")
    @classmethod
    def validate_similarity_threshold(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Similarity threshold must be between 0.0 and 1.0")
        return v
    
    @field_validator("top_k_results")
    @classmethod
    def validate_top_k(cls, v):
        if v <= 0:
            raise ValueError("Top K results must be positive")
        return v


class PerformanceConfig(BaseSettings):
    """Performance and caching configuration settings."""
    
    enable_caching: bool = Field(default=True, env="ENABLE_CACHING")
    cache_ttl: int = Field(default=3600, env="CACHE_TTL")
    batch_size: int = Field(default=10, env="BATCH_SIZE")
    max_concurrent_requests: int = Field(default=5, env="MAX_CONCURRENT_REQUESTS")
    
    @field_validator("cache_ttl")
    @classmethod
    def validate_cache_ttl(cls, v):
        if v < 0:
            raise ValueError("Cache TTL must be non-negative")
        return v


class LoggingConfig(BaseSettings):
    """Logging configuration settings."""
    
    level: str = Field(default="INFO", env="LOG_LEVEL")
    format: str = Field(default="json", env="LOG_FORMAT")
    log_file: str = Field(default="logs/zero_rag.log", env="LOG_FILE")
    enable_debug: bool = Field(default=False, env="ENABLE_DEBUG")
    
    @field_validator("level")
    @classmethod
    def validate_log_level(cls, v):
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()


class MonitoringConfig(BaseSettings):
    """Monitoring and metrics configuration settings."""
    
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")
    metrics_port: int = Field(default=9090, env="METRICS_PORT")
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")
    
    @field_validator("metrics_port")
    @classmethod
    def validate_metrics_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError("Metrics port must be between 1 and 65535")
        return v


class DevelopmentConfig(BaseSettings):
    """Development and environment configuration settings."""
    
    debug: bool = Field(default=True, env="DEBUG")
    environment: str = Field(default="development", env="ENVIRONMENT")
    enable_hot_reload: bool = Field(default=True, env="ENABLE_HOT_RELOAD")
    test_mode: bool = Field(default=False, env="TEST_MODE")
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v):
        valid_envs = ["development", "staging", "production"]
        if v not in valid_envs:
            raise ValueError(f"Environment must be one of: {valid_envs}")
        return v


class StorageConfig(BaseSettings):
    """Data storage configuration settings."""
    
    data_dir: str = Field(default="./data", env="DATA_DIR")
    upload_dir: str = Field(default="./data/uploads", env="UPLOAD_DIR")
    processed_dir: str = Field(default="./data/processed", env="PROCESSED_DIR")
    cache_dir: str = Field(default="./data/cache", env="CACHE_DIR")
    
    def ensure_directories(self, log_file_path: str = None):
        """Ensure all required directories exist."""
        directories = [
            self.data_dir,
            self.upload_dir,
            self.processed_dir,
            self.cache_dir,
        ]
        
        # Add log directory if provided
        if log_file_path:
            log_dir = os.path.dirname(log_file_path)
            if log_dir:
                directories.append(log_dir)
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)


class Config:
    """Main configuration class that combines all configuration sections."""
    
    def __init__(self, env_file: Optional[str] = None):
        """Initialize configuration with optional environment file."""
        # Initialize all configuration sections with environment file
        self.database = DatabaseConfig(_env_file=env_file)
        self.ai_model = AIModelConfig(_env_file=env_file)
        self.api = APIConfig(_env_file=env_file)
        self.document = DocumentConfig(_env_file=env_file)
        self.rag = RAGConfig(_env_file=env_file)
        self.performance = PerformanceConfig(_env_file=env_file)
        self.logging = LoggingConfig(_env_file=env_file)
        self.monitoring = MonitoringConfig(_env_file=env_file)
        self.development = DevelopmentConfig(_env_file=env_file)
        self.storage = StorageConfig(_env_file=env_file)
        
        # Ensure directories exist
        self.storage.ensure_directories(self.logging.log_file)
        
        # Setup logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Configure logging based on settings."""
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(self.logging.log_file)
        if log_dir:
            Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # Configure logging format
        if self.logging.format.lower() == "json":
            formatter = logging.Formatter(
                '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", "message": "%(message)s"}'
            )
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(self.logging.level)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Add console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
        
        # Add file handler if log file is specified
        if self.logging.log_file:
            file_handler = logging.FileHandler(self.logging.log_file)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        
        # Set debug level if enabled
        if self.logging.enable_debug:
            root_logger.setLevel(logging.DEBUG)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary for serialization."""
        return {
            "database": self.database.model_dump(),
            "ai_model": self.ai_model.model_dump(),
            "api": self.api.model_dump(),
            "document": self.document.model_dump(),
            "rag": self.rag.model_dump(),
            "performance": self.performance.model_dump(),
            "logging": self.logging.model_dump(),
            "monitoring": self.monitoring.model_dump(),
            "development": self.development.model_dump(),
            "storage": self.storage.model_dump(),
        }
    
    def validate(self) -> bool:
        """Validate all configuration settings."""
        try:
            # All validation is handled by Pydantic models
            # If we get here, validation passed
            return True
        except Exception as e:
            logging.error(f"Configuration validation failed: {e}")
            return False
    
    def get_connection_strings(self) -> Dict[str, str]:
        """Get database connection strings."""
        return {
            "qdrant": f"http://{self.database.qdrant_host}:{self.database.qdrant_port}",
            "redis": f"redis://{self.database.redis_host}:{self.database.redis_port}/{self.database.redis_db}",
        }


# Global configuration instance
config: Optional[Config] = None


def get_config(env_file: Optional[str] = None) -> Config:
    """Get or create the global configuration instance."""
    global config
    if config is None:
        config = Config(env_file)
    return config


def reload_config(env_file: Optional[str] = None) -> Config:
    """Reload the configuration from environment file."""
    global config
    config = Config(env_file)
    return config
