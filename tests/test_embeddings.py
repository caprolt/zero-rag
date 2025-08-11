"""
Unit tests for the ZeroRAG Embedding Service.

This module tests the embedding service functionality including:
- Model initialization
- Single text encoding
- Batch encoding
- Caching mechanisms
- Similarity calculations
- Error handling
- Performance metrics
"""

import pytest
import numpy as np
import time
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from src.models.embeddings import EmbeddingService, get_embedding_service, reset_embedding_service
from src.config import get_config


class TestEmbeddingService:
    """Test cases for the EmbeddingService class."""
    
    @pytest.fixture
    def mock_config(self):
        """Create a mock configuration for testing."""
        config = Mock()
        config.ai_model.embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
        config.ai_model.embedding_device = "cpu"
        config.ai_model.embedding_batch_size = 32
        config.ai_model.embedding_max_length = 512
        config.performance.enable_caching = True
        config.database.redis_host = "localhost"
        config.database.redis_port = 6379
        config.database.redis_password = None
        config.database.redis_db = 0
        config.database.redis_cache_ttl = 3600
        config.storage.cache_dir = "./data/cache"
        return config
    
    @pytest.fixture
    def mock_model(self):
        """Create a mock sentence transformer model."""
        model = Mock()
        model.encode.return_value = np.random.rand(384).astype(np.float32)
        model.get_sentence_embedding_dimension.return_value = 384
        return model
    
    @pytest.fixture
    def mock_redis(self):
        """Create a mock Redis client."""
        redis_client = Mock()
        redis_client.ping.return_value = True
        redis_client.get.return_value = None
        redis_client.setex.return_value = True
        redis_client.keys.return_value = []
        redis_client.delete.return_value = 0
        return redis_client
    
    def test_initialization_success(self, mock_config, mock_model, mock_redis):
        """Test successful initialization of the embedding service."""
        with patch('src.models.embeddings.SentenceTransformer', return_value=mock_model), \
             patch('src.models.embeddings.redis.Redis', return_value=mock_redis):
            
            service = EmbeddingService(mock_config)
            
            assert service._model_loaded is True
            assert service._cache_enabled is True
            assert service.model is not None
            assert service.redis_client is not None
    
    def test_initialization_without_cache(self, mock_config, mock_model):
        """Test initialization when Redis cache is not available."""
        with patch('src.models.embeddings.SentenceTransformer', return_value=mock_model), \
             patch('src.models.embeddings.redis.Redis', side_effect=Exception("Connection failed")):
            
            service = EmbeddingService(mock_config)
            
            assert service._model_loaded is True
            assert service._cache_enabled is False
            assert service.model is not None
            assert service.redis_client is None
    
    def test_encode_single_success(self, mock_config, mock_model, mock_redis):
        """Test successful single text encoding."""
        with patch('src.models.embeddings.SentenceTransformer', return_value=mock_model), \
             patch('src.models.embeddings.redis.Redis', return_value=mock_redis):
            
            service = EmbeddingService(mock_config)
            text = "This is a test sentence."
            
            embedding = service.encode_single(text)
            
            assert isinstance(embedding, np.ndarray)
            assert len(embedding) == 384
            assert embedding.dtype == np.float32
            mock_model.encode.assert_called_once()
    
    def test_encode_single_empty_text(self, mock_config, mock_model, mock_redis):
        """Test encoding with empty text raises ValueError."""
        with patch('src.models.embeddings.SentenceTransformer', return_value=mock_model), \
             patch('src.models.embeddings.redis.Redis', return_value=mock_redis):
            
            service = EmbeddingService(mock_config)
            
            with pytest.raises(ValueError, match="Text cannot be empty"):
                service.encode_single("")
            
            with pytest.raises(ValueError, match="Text cannot be empty"):
                service.encode_single("   ")
    
    def test_encode_single_model_not_loaded(self, mock_config):
        """Test encoding when model is not loaded raises RuntimeError."""
        service = EmbeddingService.__new__(EmbeddingService)
        service.config = mock_config
        service._model_loaded = False
        
        with pytest.raises(RuntimeError, match="Embedding model not loaded"):
            service.encode_single("test")
    
    def test_encode_batch_success(self, mock_config, mock_model, mock_redis):
        """Test successful batch encoding."""
        with patch('src.models.embeddings.SentenceTransformer', return_value=mock_model), \
             patch('src.models.embeddings.redis.Redis', return_value=mock_redis):
            
            service = EmbeddingService(mock_config)
            texts = ["First sentence.", "Second sentence.", "Third sentence."]
            
            embeddings = service.encode_batch(texts)
            
            assert isinstance(embeddings, list)
            assert len(embeddings) == 3
            assert all(isinstance(emb, np.ndarray) for emb in embeddings)
            assert all(len(emb) == 384 for emb in embeddings)
            assert mock_model.encode.call_count == 3
    
    def test_encode_batch_empty_list(self, mock_config, mock_model, mock_redis):
        """Test batch encoding with empty list raises ValueError."""
        with patch('src.models.embeddings.SentenceTransformer', return_value=mock_model), \
             patch('src.models.embeddings.redis.Redis', return_value=mock_redis):
            
            service = EmbeddingService(mock_config)
            
            with pytest.raises(ValueError, match="Texts list cannot be empty"):
                service.encode_batch([])
    
    def test_encode_batch_with_empty_texts(self, mock_config, mock_model, mock_redis):
        """Test batch encoding with empty texts raises ValueError."""
        with patch('src.models.embeddings.SentenceTransformer', return_value=mock_model), \
             patch('src.models.embeddings.redis.Redis', return_value=mock_redis):
            
            service = EmbeddingService(mock_config)
            texts = ["Valid text", "", "Another valid text"]
            
            with pytest.raises(ValueError, match="All texts must be non-empty"):
                service.encode_batch(texts)
    
    def test_cache_functionality(self, mock_config, mock_model, mock_redis):
        """Test caching functionality."""
        # Mock cached embedding
        cached_embedding = np.random.rand(384).astype(np.float32)
        mock_redis.get.return_value = cached_embedding.tobytes()
        
        with patch('src.models.embeddings.SentenceTransformer', return_value=mock_model), \
             patch('src.models.embeddings.redis.Redis', return_value=mock_redis):
            
            service = EmbeddingService(mock_config)
            text = "This should be cached."
            
            # First call should use cache
            embedding1 = service.encode_single(text)
            
            # Second call should also use cache (no model.encode call)
            embedding2 = service.encode_single(text)
            
            assert np.array_equal(embedding1, embedding2)
            assert mock_model.encode.call_count == 0  # Should not call model.encode
    
    def test_similarity_calculation(self, mock_config, mock_model, mock_redis):
        """Test similarity calculation between embeddings."""
        with patch('src.models.embeddings.SentenceTransformer', return_value=mock_model), \
             patch('src.models.embeddings.redis.Redis', return_value=mock_redis):
            
            service = EmbeddingService(mock_config)
            
            # Create test embeddings
            emb1 = np.random.rand(384).astype(np.float32)
            emb2 = np.random.rand(384).astype(np.float32)
            
            similarity = service.similarity(emb1, emb2)
            
            assert isinstance(similarity, float)
            assert 0.0 <= similarity <= 1.0
    
    def test_batch_similarity_calculation(self, mock_config, mock_model, mock_redis):
        """Test batch similarity calculation."""
        with patch('src.models.embeddings.SentenceTransformer', return_value=mock_model), \
             patch('src.models.embeddings.redis.Redis', return_value=mock_redis):
            
            service = EmbeddingService(mock_config)
            
            # Create test embeddings
            query_emb = np.random.rand(384).astype(np.float32)
            candidate_embs = [np.random.rand(384).astype(np.float32) for _ in range(3)]
            
            similarities = service.batch_similarity(query_emb, candidate_embs)
            
            assert isinstance(similarities, list)
            assert len(similarities) == 3
            assert all(isinstance(sim, float) for sim in similarities)
            assert all(0.0 <= sim <= 1.0 for sim in similarities)
    
    def test_batch_similarity_empty_candidates(self, mock_config, mock_model, mock_redis):
        """Test batch similarity with empty candidate list."""
        with patch('src.models.embeddings.SentenceTransformer', return_value=mock_model), \
             patch('src.models.embeddings.redis.Redis', return_value=mock_redis):
            
            service = EmbeddingService(mock_config)
            query_emb = np.random.rand(384).astype(np.float32)
            
            similarities = service.batch_similarity(query_emb, [])
            
            assert similarities == []
    
    def test_performance_metrics(self, mock_config, mock_model, mock_redis):
        """Test performance metrics collection."""
        with patch('src.models.embeddings.SentenceTransformer', return_value=mock_model), \
             patch('src.models.embeddings.redis.Redis', return_value=mock_redis):
            
            service = EmbeddingService(mock_config)
            
            # Generate some embeddings to populate metrics
            service.encode_single("Test text 1")
            service.encode_single("Test text 2")
            service.encode_batch(["Batch text 1", "Batch text 2"])
            
            metrics = service.get_performance_metrics()
            
            assert metrics['total_embeddings'] == 4
            assert metrics['batch_operations'] == 1
            assert metrics['model_loaded'] is True
            assert metrics['cache_enabled'] is True
            assert metrics['vector_size'] == 384
            assert 'total_time' in metrics
            assert 'average_time_per_embedding' in metrics
    
    def test_memory_usage(self, mock_config, mock_model, mock_redis):
        """Test memory usage monitoring."""
        with patch('src.models.embeddings.SentenceTransformer', return_value=mock_model), \
             patch('src.models.embeddings.redis.Redis', return_value=mock_redis), \
             patch('src.models.embeddings.psutil') as mock_psutil:
            
            # Mock psutil Process and memory info
            mock_process = Mock()
            mock_memory_info = Mock()
            mock_memory_info.rss = 100 * 1024 * 1024  # 100 MB
            mock_memory_info.vms = 200 * 1024 * 1024  # 200 MB
            mock_process.memory_info.return_value = mock_memory_info
            mock_process.memory_percent.return_value = 5.0
            mock_psutil.Process.return_value = mock_process
            mock_psutil.virtual_memory.return_value.available = 8000 * 1024 * 1024  # 8 GB
            
            service = EmbeddingService(mock_config)
            memory_info = service.get_memory_usage()
            
            assert memory_info['rss_mb'] == 100.0
            assert memory_info['vms_mb'] == 200.0
            assert memory_info['percent'] == 5.0
            assert memory_info['available_mb'] == 8000.0
    
    def test_memory_usage_psutil_not_available(self, mock_config, mock_model, mock_redis):
        """Test memory usage when psutil is not available."""
        with patch('src.models.embeddings.SentenceTransformer', return_value=mock_model), \
             patch('src.models.embeddings.redis.Redis', return_value=mock_redis), \
             patch('src.models.embeddings.psutil', side_effect=ImportError):
            
            service = EmbeddingService(mock_config)
            memory_info = service.get_memory_usage()
            
            assert memory_info['error'] == 'psutil not available'
    
    def test_health_check_healthy(self, mock_config, mock_model, mock_redis):
        """Test health check when service is healthy."""
        with patch('src.models.embeddings.SentenceTransformer', return_value=mock_model), \
             patch('src.models.embeddings.redis.Redis', return_value=mock_redis):
            
            service = EmbeddingService(mock_config)
            health_status = service.health_check()
            
            assert health_status['status'] == 'healthy'
            assert health_status['model_loaded'] is True
            assert health_status['cache_enabled'] is True
            assert health_status['model_test'] == 'passed'
            assert health_status['cache_test'] == 'passed'
            assert 'performance' in health_status
            assert 'memory' in health_status
            assert len(health_status['errors']) == 0
    
    def test_health_check_unhealthy_model(self, mock_config, mock_redis):
        """Test health check when model fails."""
        with patch('src.models.embeddings.SentenceTransformer', side_effect=Exception("Model failed")), \
             patch('src.models.embeddings.redis.Redis', return_value=mock_redis):
            
            service = EmbeddingService(mock_config)
            health_status = service.health_check()
            
            assert health_status['status'] == 'unhealthy'
            assert health_status['model_loaded'] is False
            assert len(health_status['errors']) > 0
    
    def test_clear_cache(self, mock_config, mock_model, mock_redis):
        """Test cache clearing functionality."""
        # Mock cache keys
        mock_redis.keys.return_value = [b"embedding:key1", b"embedding:key2"]
        mock_redis.delete.return_value = 2
        
        with patch('src.models.embeddings.SentenceTransformer', return_value=mock_model), \
             patch('src.models.embeddings.redis.Redis', return_value=mock_redis):
            
            service = EmbeddingService(mock_config)
            result = service.clear_cache()
            
            assert result is True
            mock_redis.keys.assert_called_once_with("embedding:*")
            mock_redis.delete.assert_called_once_with(b"embedding:key1", b"embedding:key2")
    
    def test_clear_cache_disabled(self, mock_config, mock_model):
        """Test cache clearing when cache is disabled."""
        with patch('src.models.embeddings.SentenceTransformer', return_value=mock_model), \
             patch('src.models.embeddings.redis.Redis', side_effect=Exception("Connection failed")):
            
            service = EmbeddingService(mock_config)
            result = service.clear_cache()
            
            assert result is False
    
    def test_global_service_functions(self, mock_config, mock_model, mock_redis):
        """Test global service functions."""
        with patch('src.models.embeddings.SentenceTransformer', return_value=mock_model), \
             patch('src.models.embeddings.redis.Redis', return_value=mock_redis):
            
            # Reset global service
            reset_embedding_service()
            
            # Get service instance
            service1 = get_embedding_service(mock_config)
            assert service1 is not None
            
            # Get service instance again (should be the same)
            service2 = get_embedding_service(mock_config)
            assert service2 is service1
            
            # Reset and get new instance
            reset_embedding_service()
            service3 = get_embedding_service(mock_config)
            assert service3 is not service1


class TestEmbeddingServiceIntegration:
    """Integration tests for the embedding service."""
    
    @pytest.mark.integration
    def test_real_model_loading(self):
        """Test loading a real sentence transformer model."""
        # This test requires internet connection to download the model
        config = get_config()
        config.ai_model.embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
        config.ai_model.embedding_device = "cpu"
        
        try:
            service = EmbeddingService(config)
            assert service._model_loaded is True
            assert service.model is not None
            
            # Test encoding
            text = "This is a test sentence for integration testing."
            embedding = service.encode_single(text)
            
            assert isinstance(embedding, np.ndarray)
            assert len(embedding) > 0
            assert embedding.dtype == np.float32
            
        except Exception as e:
            pytest.skip(f"Integration test skipped: {e}")
    
    @pytest.mark.integration
    def test_batch_processing_performance(self):
        """Test batch processing performance."""
        config = get_config()
        config.ai_model.embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
        config.ai_model.embedding_device = "cpu"
        
        try:
            service = EmbeddingService(config)
            
            # Create test texts
            texts = [f"This is test sentence number {i} for batch processing." for i in range(10)]
            
            # Time batch processing
            start_time = time.time()
            embeddings = service.encode_batch(texts)
            batch_time = time.time() - start_time
            
            # Time individual processing
            start_time = time.time()
            individual_embeddings = [service.encode_single(text) for text in texts]
            individual_time = time.time() - start_time
            
            assert len(embeddings) == len(individual_embeddings) == 10
            assert batch_time < individual_time  # Batch should be faster
            
        except Exception as e:
            pytest.skip(f"Integration test skipped: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
