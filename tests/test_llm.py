"""
Unit tests for LLM service components.

Tests cover:
- OllamaClient functionality
- HuggingFaceClient functionality  
- LLMService integration
- Error handling and fallback
- Health checks
- Performance metrics
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, Generator

import torch
import requests
from transformers import AutoTokenizer, AutoModelForCausalLM

from src.models.llm import (
    LLMService, 
    OllamaClient, 
    HuggingFaceClient,
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
            provider=LLMProvider.HUGGINGFACE,
            model_name="test-model",
            response_time=1.0
        )
        
        assert response.tokens_used is None
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
            device="cpu",
            enable_streaming=True
        )
        
        assert config.provider == LLMProvider.OLLAMA
        assert config.model_name == "test-model"
        assert config.temperature == 0.8
        assert config.max_tokens == 1024
        assert config.timeout == 60
        assert config.device == "cpu"
        assert config.enable_streaming is True
    
    def test_llm_config_defaults(self):
        """Test LLMConfig default values."""
        config = LLMConfig(
            provider=LLMProvider.HUGGINGFACE,
            model_name="test-model"
        )
        
        assert config.temperature == 0.7
        assert config.max_tokens == 2048
        assert config.timeout == 30
        assert config.device == "cpu"
        assert config.enable_streaming is True


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
    def ollama_client(self, ollama_config, mock_config):
        """Create OllamaClient instance."""
        with patch('src.models.llm.get_config', return_value=mock_config):
            return OllamaClient(ollama_config)
    
    def test_ollama_client_initialization(self, ollama_client):
        """Test OllamaClient initialization."""
        assert ollama_client.config.model_name == "test-model"
        assert ollama_client.base_url == "http://localhost:11434"
        assert ollama_client.session.timeout == 30
    
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
        
        with pytest.raises(ConnectionError):
            ollama_client.generate("Test prompt")
    
    @patch('requests.Session.post')
    def test_ollama_streaming_success(self, mock_post, ollama_client):
        """Test successful streaming generation."""
        mock_response = Mock()
        mock_response.iter_lines.return_value = [
            json.dumps({"response": "Hello", "done": False}).encode(),
            json.dumps({"response": " world", "done": False}).encode(),
            json.dumps({"response": "!", "done": True}).encode()
        ]
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response
        
        chunks = list(ollama_client.generate_streaming("Test prompt"))
        
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
        assert health["provider"] == "ollama"
        assert "test-model" in health["available_models"]
        assert health["model_loaded"] is True
    
    @patch('requests.Session.get')
    def test_ollama_health_check_failure(self, mock_get, ollama_client):
        """Test health check failure."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        health = ollama_client.health_check()
        
        assert health["status"] == "unhealthy"
        assert health["provider"] == "ollama"
        assert "error" in health


class TestHuggingFaceClient:
    """Test HuggingFaceClient functionality."""
    
    @pytest.fixture
    def hf_config(self):
        """Create LLMConfig for HuggingFace."""
        return LLMConfig(
            provider=LLMProvider.HUGGINGFACE,
            model_name="test-model",
            temperature=0.7,
            max_tokens=1024,
            device="cpu"
        )
    
    @patch('src.models.llm.AutoTokenizer.from_pretrained')
    @patch('src.models.llm.AutoModelForCausalLM.from_pretrained')
    def test_hf_client_initialization(self, mock_model, mock_tokenizer, hf_config):
        """Test HuggingFaceClient initialization."""
        # Mock tokenizer
        mock_tokenizer_instance = Mock()
        mock_tokenizer_instance.pad_token = None
        mock_tokenizer_instance.eos_token = "<eos>"
        mock_tokenizer_instance.eos_token_id = 2
        mock_tokenizer.return_value = mock_tokenizer_instance
        
        # Mock model
        mock_model_instance = Mock()
        mock_model.return_value = mock_model_instance
        
        client = HuggingFaceClient(hf_config)
        
        assert client.config.model_name == "test-model"
        assert client.tokenizer is not None
        assert client.model is not None
        assert client.tokenizer.pad_token == "<eos>"
    
    @patch('src.models.llm.AutoTokenizer.from_pretrained')
    @patch('src.models.llm.AutoModelForCausalLM.from_pretrained')
    def test_hf_generate_success(self, mock_model, mock_tokenizer, hf_config):
        """Test successful text generation."""
        # Mock tokenizer
        mock_tokenizer_instance = Mock()
        mock_tokenizer_instance.pad_token = "<eos>"
        mock_tokenizer_instance.eos_token_id = 2
        
        # Create a proper mock that returns the expected structure
        mock_inputs = Mock()
        mock_inputs.input_ids = torch.tensor([[1, 2, 3, 4, 5]])
        mock_inputs.attention_mask = torch.tensor([[1, 1, 1, 1, 1]])
        mock_tokenizer_instance.return_value = mock_inputs
        mock_tokenizer_instance.decode.return_value = "Generated response"
        mock_tokenizer.return_value = mock_tokenizer_instance
        
        # Mock model
        mock_model_instance = Mock()
        mock_model_instance.generate.return_value = torch.tensor([[1, 2, 3, 4, 5, 6, 7, 8]])
        mock_model.return_value = mock_model_instance
        
        client = HuggingFaceClient(hf_config)
        
        with patch('torch.no_grad'):
            response = client.generate("Test prompt")
        
        assert response.text == "Generated response"
        assert response.provider == LLMProvider.HUGGINGFACE
        assert response.model_name == "test-model"
        assert response.tokens_used == 3  # 8 - 5 = 3
        assert response.response_time > 0
    
    @patch('src.models.llm.AutoTokenizer.from_pretrained')
    @patch('src.models.llm.AutoModelForCausalLM.from_pretrained')
    def test_hf_streaming_success(self, mock_model, mock_tokenizer, hf_config):
        """Test successful streaming generation."""
        # Mock tokenizer
        mock_tokenizer_instance = Mock()
        mock_tokenizer_instance.pad_token = "<eos>"
        mock_tokenizer_instance.eos_token_id = 2
        
        # Create a proper mock that returns the expected structure
        mock_inputs = Mock()
        mock_inputs.input_ids = torch.tensor([[1, 2, 3, 4, 5]])
        mock_inputs.attention_mask = torch.tensor([[1, 1, 1, 1, 1]])
        mock_tokenizer_instance.return_value = mock_inputs
        mock_tokenizer_instance.decode.side_effect = ["Hello", " world", "!"]
        mock_tokenizer.return_value = mock_tokenizer_instance
        
        # Mock model - need to mock the tensor operations properly
        mock_model_instance = Mock()
        
        # Mock the generate method to return tensors that work with the streaming logic
        def mock_generate(*args, **kwargs):
            # Return a tensor that when indexed with [0][-1] gives a 1D tensor
            # This simulates the actual behavior in the streaming code
            return torch.tensor([[1, 2, 3, 4, 5, 6]])  # 2D tensor
        
        mock_model_instance.generate = mock_generate
        mock_model.return_value = mock_model_instance
        
        client = HuggingFaceClient(hf_config)
        
        with patch('torch.no_grad'):
            chunks = list(client.generate_streaming("Test prompt", max_tokens=3))
        
        # The test should pass now that the tensor dimensions are correct
        assert len(chunks) > 0
    
    @patch('src.models.llm.AutoTokenizer.from_pretrained')
    @patch('src.models.llm.AutoModelForCausalLM.from_pretrained')
    def test_hf_health_check_success(self, mock_model, mock_tokenizer, hf_config):
        """Test successful health check."""
        # Mock tokenizer
        mock_tokenizer_instance = Mock()
        mock_tokenizer_instance.pad_token = "<eos>"
        mock_tokenizer_instance.eos_token_id = 2
        
        # Create a proper mock that returns the expected structure
        mock_inputs = Mock()
        mock_inputs.input_ids = torch.tensor([[1, 2, 3]])
        mock_tokenizer_instance.return_value = mock_inputs
        mock_tokenizer.return_value = mock_tokenizer_instance
        
        # Mock model
        mock_model_instance = Mock()
        mock_model_instance.parameters.return_value = iter([torch.tensor([1.0])])
        mock_model.return_value = mock_model_instance
        
        client = HuggingFaceClient(hf_config)
        
        health = client.health_check()
        
        assert health["status"] == "healthy"
        assert health["provider"] == "huggingface"
        assert health["model_name"] == "test-model"
        assert health["model_loaded"] is True
    
    def test_hf_health_check_model_not_loaded(self, hf_config):
        """Test health check when model is not loaded."""
        client = HuggingFaceClient.__new__(HuggingFaceClient)
        client.config = hf_config
        client.tokenizer = None
        client.model = None
        
        health = client.health_check()
        
        assert health["status"] == "unhealthy"
        assert health["provider"] == "huggingface"
        assert health["error"] == "Model not loaded"


class TestLLMService:
    """Test LLMService integration."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration for testing."""
        config = Mock()
        config.ai_model.ollama_host = "http://localhost:11434"
        config.ai_model.ollama_model = "test-model"
        config.ai_model.ollama_temperature = 0.7
        config.ai_model.ollama_max_tokens = 1024
        config.ai_model.ollama_timeout = 30
        config.ai_model.hf_model_name = "test-hf-model"
        config.ai_model.hf_max_length = 1024
        config.ai_model.hf_device = "cpu"
        return config
    
    @patch('src.models.llm.OllamaClient')
    @patch('src.models.llm.HuggingFaceClient')
    def test_llm_service_initialization_ollama_primary(self, mock_hf, mock_ollama, mock_config):
        """Test LLMService initialization with Ollama as primary."""
        # Mock Ollama health check success
        mock_ollama_instance = Mock()
        mock_ollama_instance.health_check.return_value = {"status": "healthy"}
        mock_ollama.return_value = mock_ollama_instance
        
        # Mock HuggingFace initialization
        mock_hf_instance = Mock()
        mock_hf.return_value = mock_hf_instance
        
        with patch('src.models.llm.get_config', return_value=mock_config):
            service = LLMService()
        
        assert service.current_provider == LLMProvider.OLLAMA
        assert service.ollama_client is not None
        assert service.hf_client is not None
    
    @patch('src.models.llm.OllamaClient')
    @patch('src.models.llm.HuggingFaceClient')
    def test_llm_service_initialization_hf_primary(self, mock_hf, mock_ollama, mock_config):
        """Test LLMService initialization with HuggingFace as primary."""
        # Mock Ollama health check failure
        mock_ollama_instance = Mock()
        mock_ollama_instance.health_check.return_value = {"status": "unhealthy", "error": "Connection failed"}
        mock_ollama.side_effect = Exception("Ollama failed")
        
        # Mock HuggingFace initialization
        mock_hf_instance = Mock()
        mock_hf.return_value = mock_hf_instance
        
        with patch('src.models.llm.get_config', return_value=mock_config):
            service = LLMService()
        
        assert service.current_provider == LLMProvider.HUGGINGFACE
        assert service.ollama_client is None
        assert service.hf_client is not None
    
    @patch('src.models.llm.OllamaClient')
    @patch('src.models.llm.HuggingFaceClient')
    def test_llm_service_initialization_no_providers(self, mock_hf, mock_ollama, mock_config):
        """Test LLMService initialization with no available providers."""
        # Mock both providers failing
        mock_ollama.side_effect = Exception("Ollama failed")
        mock_hf.side_effect = Exception("HuggingFace failed")
        
        with patch('src.models.llm.get_config', return_value=mock_config):
            with pytest.raises(RuntimeError, match="No LLM providers available"):
                LLMService()
    
    @patch('src.models.llm.OllamaClient')
    @patch('src.models.llm.HuggingFaceClient')
    def test_llm_service_generate_ollama_success(self, mock_hf, mock_ollama, mock_config):
        """Test successful generation with Ollama."""
        # Mock Ollama success
        mock_ollama_instance = Mock()
        mock_ollama_instance.health_check.return_value = {"status": "healthy"}
        mock_ollama_instance.generate.return_value = LLMResponse(
            text="Ollama response",
            provider=LLMProvider.OLLAMA,
            model_name="test-model",
            response_time=1.0
        )
        mock_ollama.return_value = mock_ollama_instance
        
        # Mock HuggingFace
        mock_hf_instance = Mock()
        mock_hf.return_value = mock_hf_instance
        
        with patch('src.models.llm.get_config', return_value=mock_config):
            service = LLMService()
        
        response = service.generate("Test prompt")
        
        assert response.text == "Ollama response"
        assert response.provider == LLMProvider.OLLAMA
        assert service.request_count == 1
        assert service.error_count == 0
    
    @patch('src.models.llm.OllamaClient')
    @patch('src.models.llm.HuggingFaceClient')
    def test_llm_service_generate_fallback(self, mock_hf, mock_ollama, mock_config):
        """Test generation with fallback to HuggingFace."""
        # Mock Ollama failure
        mock_ollama_instance = Mock()
        mock_ollama_instance.health_check.return_value = {"status": "healthy"}
        mock_ollama_instance.generate.side_effect = Exception("Ollama failed")
        mock_ollama.return_value = mock_ollama_instance
        
        # Mock HuggingFace success
        mock_hf_instance = Mock()
        mock_hf_instance.generate.return_value = LLMResponse(
            text="HuggingFace response",
            provider=LLMProvider.HUGGINGFACE,
            model_name="test-hf-model",
            response_time=2.0
        )
        mock_hf.return_value = mock_hf_instance
        
        with patch('src.models.llm.get_config', return_value=mock_config):
            service = LLMService()
        
        response = service.generate("Test prompt")
        
        assert response.text == "HuggingFace response"
        assert response.provider == LLMProvider.HUGGINGFACE
        assert service.request_count == 1
        assert service.error_count == 1  # Ollama failed
    
    @patch('src.models.llm.OllamaClient')
    @patch('src.models.llm.HuggingFaceClient')
    def test_llm_service_generate_all_fail(self, mock_hf, mock_ollama, mock_config):
        """Test generation when all providers fail."""
        # Mock both providers failing
        mock_ollama_instance = Mock()
        mock_ollama_instance.health_check.return_value = {"status": "healthy"}
        mock_ollama_instance.generate.side_effect = Exception("Ollama failed")
        mock_ollama.return_value = mock_ollama_instance
        
        mock_hf_instance = Mock()
        mock_hf_instance.generate.side_effect = Exception("HuggingFace failed")
        mock_hf.return_value = mock_hf_instance
        
        with patch('src.models.llm.get_config', return_value=mock_config):
            service = LLMService()
        
        with pytest.raises(RuntimeError, match="All LLM providers failed"):
            service.generate("Test prompt")
        
        assert service.request_count == 1
        assert service.error_count == 2  # Both failed
    
    @patch('src.models.llm.OllamaClient')
    @patch('src.models.llm.HuggingFaceClient')
    def test_llm_service_streaming(self, mock_hf, mock_ollama, mock_config):
        """Test streaming generation."""
        # Mock Ollama streaming
        mock_ollama_instance = Mock()
        mock_ollama_instance.health_check.return_value = {"status": "healthy"}
        mock_ollama_instance.generate_streaming.return_value = ["Hello", " world", "!"]
        mock_ollama.return_value = mock_ollama_instance
        
        # Mock HuggingFace
        mock_hf_instance = Mock()
        mock_hf.return_value = mock_hf_instance
        
        with patch('src.models.llm.get_config', return_value=mock_config):
            service = LLMService()
        
        chunks = list(service.generate_streaming("Test prompt"))
        
        assert chunks == ["Hello", " world", "!"]
        assert service.request_count == 1
    
    @patch('src.models.llm.OllamaClient')
    @patch('src.models.llm.HuggingFaceClient')
    def test_llm_service_health_check(self, mock_hf, mock_ollama, mock_config):
        """Test health check functionality."""
        # Mock Ollama health
        mock_ollama_instance = Mock()
        mock_ollama_instance.health_check.return_value = {"status": "healthy", "provider": "ollama"}
        mock_ollama.return_value = mock_ollama_instance
        
        # Mock HuggingFace health
        mock_hf_instance = Mock()
        mock_hf_instance.health_check.return_value = {"status": "healthy", "provider": "huggingface"}
        mock_hf.return_value = mock_hf_instance
        
        with patch('src.models.llm.get_config', return_value=mock_config):
            service = LLMService()
        
        health = service.health_check()
        
        assert health["status"] == "healthy"
        assert health["current_provider"] == LLMProvider.OLLAMA
        assert "ollama" in health["providers"]
        assert "huggingface" in health["providers"]
        assert "metrics" in health
    
    @patch('src.models.llm.OllamaClient')
    @patch('src.models.llm.HuggingFaceClient')
    def test_llm_service_metrics(self, mock_hf, mock_ollama, mock_config):
        """Test performance metrics tracking."""
        # Mock Ollama success
        mock_ollama_instance = Mock()
        mock_ollama_instance.health_check.return_value = {"status": "healthy"}
        mock_ollama_instance.generate.return_value = LLMResponse(
            text="Response",
            provider=LLMProvider.OLLAMA,
            model_name="test-model",
            response_time=1.5
        )
        mock_ollama.return_value = mock_ollama_instance
        
        # Mock HuggingFace
        mock_hf_instance = Mock()
        mock_hf.return_value = mock_hf_instance
        
        with patch('src.models.llm.get_config', return_value=mock_config):
            service = LLMService()
        
        # Make multiple requests
        service.generate("Test 1")
        service.generate("Test 2")
        
        metrics = service._get_metrics()
        
        assert metrics["total_requests"] == 2
        assert metrics["error_count"] == 0
        assert metrics["error_rate"] == 0.0
        assert metrics["average_response_time"] == 1.5
        assert metrics["total_response_time"] == 3.0
    
    @patch('src.models.llm.OllamaClient')
    @patch('src.models.llm.HuggingFaceClient')
    def test_llm_service_switch_provider(self, mock_hf, mock_ollama, mock_config):
        """Test provider switching functionality."""
        # Mock both providers healthy
        mock_ollama_instance = Mock()
        mock_ollama_instance.health_check.return_value = {"status": "healthy"}
        mock_ollama.return_value = mock_ollama_instance
        
        mock_hf_instance = Mock()
        mock_hf_instance.health_check.return_value = {"status": "healthy"}
        mock_hf.return_value = mock_hf_instance
        
        with patch('src.models.llm.get_config', return_value=mock_config):
            service = LLMService()
        
        # Switch to HuggingFace
        success = service.switch_provider(LLMProvider.HUGGINGFACE)
        assert success is True
        assert service.current_provider == LLMProvider.HUGGINGFACE
        
        # Switch back to Ollama
        success = service.switch_provider(LLMProvider.OLLAMA)
        assert success is True
        assert service.current_provider == LLMProvider.OLLAMA
    
    @patch('src.models.llm.OllamaClient')
    @patch('src.models.llm.HuggingFaceClient')
    def test_llm_service_get_available_providers(self, mock_hf, mock_ollama, mock_config):
        """Test getting available providers."""
        # Mock both providers healthy
        mock_ollama_instance = Mock()
        mock_ollama_instance.health_check.return_value = {"status": "healthy"}
        mock_ollama.return_value = mock_ollama_instance
        
        mock_hf_instance = Mock()
        mock_hf_instance.health_check.return_value = {"status": "healthy"}
        mock_hf.return_value = mock_hf_instance
        
        with patch('src.models.llm.get_config', return_value=mock_config):
            service = LLMService()
        
        available = service.get_available_providers()
        
        assert LLMProvider.OLLAMA in available
        assert LLMProvider.HUGGINGFACE in available
        assert len(available) == 2


if __name__ == "__main__":
    pytest.main([__file__])
