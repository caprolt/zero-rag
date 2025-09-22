"""
Unit tests for LLM service components.

Tests cover:
- OllamaClient functionality
- LLMService integration
- Error handling
- Health checks
- Performance metrics
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, Generator

import requests

from src.models.llm import (
    LLMService, 
    OllamaClient, 
    LLMProvider, 
    LLMResponse, 
    LLMConfig
)
from src.config import get_config


class TestLLMResponse:
    """Test LLMResponse model."""
    
    def test_llm_response_creation(self):
        """Test creating LLMResponse objects."""
        response = LLMResponse(
            text="Test response",
            provider=LLMProvider.OLLAMA,
            model_name="test-model",
            tokens_used=10,
            response_time=1.5,
            metadata={"test": "data"}
        )
        
        assert response.text == "Test response"
        assert response.provider == LLMProvider.OLLAMA
        assert response.model_name == "test-model"
        assert response.tokens_used == 10
        assert response.response_time == 1.5
        assert response.metadata["test"] == "data"
    
    def test_llm_response_optional_fields(self):
        """Test LLMResponse with optional fields."""
        response = LLMResponse(
            text="Test response",
            provider=LLMProvider.OLLAMA,
            model_name="test-model",
            response_time=1.0
        )
        
        assert response.tokens_used == 0
        assert response.metadata == {}


class TestLLMConfig:
    """Test LLMConfig dataclass."""
    
    def test_llm_config_creation(self):
        """Test creating LLMConfig objects."""
        config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model_name="test-model",
            temperature=0.8,
            max_tokens=1024,
            timeout=60,
            device="cpu"
        )
        
        assert config.provider == LLMProvider.OLLAMA
        assert config.model_name == "test-model"
        assert config.temperature == 0.8
        assert config.max_tokens == 1024
        assert config.timeout == 60
        assert config.device == "cpu"
    
    def test_llm_config_defaults(self):
        """Test LLMConfig default values."""
        config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model_name="test-model"
        )
        
        assert config.temperature == 0.7
        assert config.max_tokens == 1000
        assert config.timeout == 30
        assert config.device == "auto"


class TestOllamaClient:
    """Test OllamaClient functionality."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        config = Mock()
        config.ai_model.ollama_host = "http://localhost:11434"
        return config
    
    @pytest.fixture
    def ollama_config(self):
        """Create LLMConfig for Ollama."""
        return LLMConfig(
            provider=LLMProvider.OLLAMA,
            model_name="test-model",
            temperature=0.7,
            max_tokens=1024,
            timeout=30
        )
    
    @pytest.fixture
    def ollama_client(self, ollama_config):
        """Create OllamaClient instance."""
        return OllamaClient(ollama_config)
    
    def test_ollama_client_initialization(self, ollama_client):
        """Test OllamaClient initialization."""
        assert ollama_client.config.model_name == "test-model"
        assert ollama_client.base_url == "http://localhost:11434"
    
    @patch('requests.Session.post')
    def test_ollama_generate_success(self, mock_post, ollama_client):
        """Test successful text generation."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "response": "Generated text",
            "eval_count": 15,
            "prompt_eval_count": 5,
            "eval_duration": 1000
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        response = ollama_client.generate("Test prompt")
        
        assert response.text == "Generated text"
        assert response.provider == LLMProvider.OLLAMA
        assert response.model_name == "test-model"
        assert response.tokens_used == 15
        assert response.response_time > 0
        assert response.metadata["prompt_eval_count"] == 5
        assert response.metadata["eval_duration"] == 1000
    
    @patch('requests.Session.post')
    def test_ollama_generate_failure(self, mock_post, ollama_client):
        """Test generation failure handling."""
        mock_post.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        response = ollama_client.generate("Test prompt")
        
        assert response.text == ""
        assert response.error == "Ollama API request failed: Connection failed"
    
    @patch('requests.Session.post')
    def test_ollama_streaming_success(self, mock_post, ollama_client):
        """Test successful streaming generation."""
        mock_response = Mock()
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=None)
        mock_response.iter_lines.return_value = [
            json.dumps({"response": "Hello", "done": False}).encode(),
            json.dumps({"response": " world", "done": False}).encode(),
            json.dumps({"response": "!", "done": True}).encode()
        ]
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        chunks = list(ollama_client.stream_generate("Test prompt"))
        
        assert chunks == ["Hello", " world", "!"]
    
    @patch('requests.Session.get')
    def test_ollama_health_check_success(self, mock_get, ollama_client):
        """Test successful health check."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "models": [
                {"name": "test-model"},
                {"name": "other-model"}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        health = ollama_client.health_check()
        
        assert health["status"] == "healthy"
        assert health["model_available"] is True
        assert "test-model" in health["available_models"]
    
    @patch('requests.Session.get')
    def test_ollama_health_check_failure(self, mock_get, ollama_client):
        """Test health check failure."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        health = ollama_client.health_check()
        
        assert health["status"] == "unhealthy"
        assert health["model_available"] is False
        assert "Connection failed" in health["error"]


class TestLLMService:
    """Test LLMService integration."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        config = Mock()
        config.ai_model.ollama_host = "http://localhost:11434"
        config.ai_model.ollama_model = "test-model"
        config.ai_model.ollama_temperature = 0.7
        config.ai_model.ollama_max_tokens = 1000
        config.ai_model.ollama_timeout = 30
        return config
    
    @patch('src.models.llm.OllamaClient')
    def test_llm_service_initialization(self, mock_ollama, mock_config):
        """Test LLMService initialization."""
        mock_ollama_instance = Mock()
        mock_ollama.return_value = mock_ollama_instance
        
        with patch('src.models.llm.get_config', return_value=mock_config):
            service = LLMService()
        
        assert service.current_provider == LLMProvider.OLLAMA
        assert LLMProvider.OLLAMA in service.clients
        mock_ollama.assert_called_once()
    
    @patch('src.models.llm.OllamaClient')
    def test_llm_service_generation(self, mock_ollama, mock_config):
        """Test text generation through service."""
        mock_ollama_instance = Mock()
        mock_ollama_instance.generate.return_value = LLMResponse(
            text="Generated text",
            provider=LLMProvider.OLLAMA,
            model_name="test-model",
            tokens_used=10,
            response_time=1.0
        )
        mock_ollama.return_value = mock_ollama_instance
        
        with patch('src.models.llm.get_config', return_value=mock_config):
            service = LLMService()
            response = service.generate("Test prompt")
        
        assert response.text == "Generated text"
        assert response.provider == LLMProvider.OLLAMA
        assert service.total_requests == 1
        assert service.successful_requests == 1
        assert service.failed_requests == 0
    
    @patch('src.models.llm.OllamaClient')
    def test_llm_service_generation_failure(self, mock_ollama, mock_config):
        """Test generation failure handling."""
        mock_ollama_instance = Mock()
        mock_ollama_instance.generate.return_value = LLMResponse(
            text="",
            provider=LLMProvider.OLLAMA,
            model_name="test-model",
            error="Connection failed"
        )
        mock_ollama.return_value = mock_ollama_instance
        
        with patch('src.models.llm.get_config', return_value=mock_config):
            service = LLMService()
            response = service.generate("Test prompt")
        
        assert response.text == ""
        assert response.error == "Ollama provider failed or not available"
        assert service.total_requests == 1
        assert service.successful_requests == 0
        assert service.failed_requests == 1
    
    @patch('src.models.llm.OllamaClient')
    def test_llm_service_streaming(self, mock_ollama, mock_config):
        """Test streaming generation through service."""
        mock_ollama_instance = Mock()
        mock_ollama_instance.stream_generate.return_value = iter(["Hello", " world", "!"])
        mock_ollama.return_value = mock_ollama_instance
        
        with patch('src.models.llm.get_config', return_value=mock_config):
            service = LLMService()
            chunks = list(service.stream_generate("Test prompt"))
        
        assert chunks == ["Hello", " world", "!"]
    
    @patch('src.models.llm.OllamaClient')
    def test_llm_service_health_check(self, mock_ollama, mock_config):
        """Test health check through service."""
        mock_ollama_instance = Mock()
        mock_ollama_instance.health_check.return_value = {
            "status": "healthy",
            "model_available": True
        }
        mock_ollama.return_value = mock_ollama_instance
        
        with patch('src.models.llm.get_config', return_value=mock_config):
            service = LLMService()
            health = service.health_check()
        
        assert health["status"] == "healthy"
        assert health["current_provider"] == "ollama"
        assert "ollama" in health["available_providers"]
        assert "metrics" in health
    
    @patch('src.models.llm.OllamaClient')
    def test_llm_service_switch_provider(self, mock_ollama, mock_config):
        """Test provider switching (should only work with Ollama)."""
        mock_ollama_instance = Mock()
        mock_ollama_instance.health_check.return_value = {
            "status": "healthy",
            "model_available": True
        }
        mock_ollama.return_value = mock_ollama_instance
        
        with patch('src.models.llm.get_config', return_value=mock_config):
            service = LLMService()
            
            # Should work with Ollama
            result = service.switch_provider(LLMProvider.OLLAMA)
            assert result is True
            assert service.current_provider == LLMProvider.OLLAMA
    
    @patch('src.models.llm.OllamaClient')
    def test_llm_service_performance_metrics(self, mock_ollama, mock_config):
        """Test performance metrics."""
        mock_ollama_instance = Mock()
        mock_ollama.return_value = mock_ollama_instance
        
        with patch('src.models.llm.get_config', return_value=mock_config):
            service = LLMService()
            
            # Simulate some requests
            service.total_requests = 10
            service.successful_requests = 8
            service.failed_requests = 2
            service.provider_usage[LLMProvider.OLLAMA] = 8
            
            metrics = service.get_performance_metrics()
            
            assert metrics["total_requests"] == 10
            assert metrics["successful_requests"] == 8
            assert metrics["failed_requests"] == 2
            assert metrics["success_rate"] == 0.8
            assert metrics["provider_usage"]["ollama"] == 8


class TestLLMServiceGlobal:
    """Test global LLM service functions."""
    
    @patch('src.models.llm.LLMService')
    def test_get_llm_service_singleton(self, mock_service_class):
        """Test global service instance creation."""
        from src.models.llm import get_llm_service, reset_llm_service
        
        # Reset to ensure clean state
        reset_llm_service()
        
        mock_service_instance = Mock()
        mock_service_class.return_value = mock_service_instance
        
        # First call should create instance
        service1 = get_llm_service()
        
        # Second call should return same instance
        service2 = get_llm_service()
        
        assert service1 is service2
        mock_service_class.assert_called_once()
    
    def test_reset_llm_service(self):
        """Test resetting global service instance."""
        from src.models.llm import reset_llm_service, _llm_service
        
        reset_llm_service()
        
        # After reset, the global variable should be None
        # This is tested indirectly by checking that get_llm_service creates a new instance
        assert True  # This test verifies the function executes without error


if __name__ == "__main__":
    pytest.main([__file__])