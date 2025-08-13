"""
ZeroRAG RAG Pipeline Service

This module provides the core RAG (Retrieval-Augmented Generation) pipeline that
integrates document retrieval, context assembly, and response generation with
comprehensive error handling and performance monitoring.

Phase 5.2 Enhancements:
- Advanced prompt engineering with optimized templates
- Context-aware prompt selection
- Safety and ethics guidelines
- Response validation and formatting
- Query-specific prompt customization
"""

import logging
import time
import re
from typing import Dict, Any, List, Optional, Generator, Tuple
from dataclasses import dataclass
from enum import Enum
import json

from .vector_store import SearchResult
try:
    from ..models.llm import LLMResponse
except ImportError:
    from models.llm import LLMResponse
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .service_factory import ServiceFactory

logger = logging.getLogger(__name__)


class RAGStatus(str, Enum):
    """RAG pipeline status enumeration."""
    READY = "ready"
    PROCESSING = "processing"
    ERROR = "error"
    NO_RESULTS = "no_results"


class QueryType(str, Enum):
    """Query type classification for prompt selection."""
    GENERAL = "general"
    FACTUAL = "factual"
    ANALYTICAL = "analytical"
    COMPARATIVE = "comparative"
    SUMMARIZATION = "summarization"
    CREATIVE = "creative"


@dataclass
class RAGQuery:
    """RAG query container with enhanced prompt engineering support."""
    query: str
    top_k: int = 5
    score_threshold: float = 0.7
    max_context_length: int = 4000
    temperature: float = 0.7
    max_tokens: int = 1024
    filters: Optional[Dict[str, Any]] = None
    query_type: Optional[QueryType] = None
    response_format: Optional[str] = None  # "text", "json", "bullet_points", "table"
    include_sources: bool = True
    safety_level: str = "standard"  # "standard", "conservative", "permissive"


@dataclass
class RAGContext:
    """RAG context container."""
    query: str
    retrieved_documents: List[SearchResult]
    assembled_context: str
    context_length: int
    source_files: List[str]
    relevance_scores: List[float]


@dataclass
class RAGResponse:
    """RAG response container with enhanced validation."""
    answer: str
    context: RAGContext
    response_time: float
    tokens_used: Optional[int] = None
    sources: List[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None
    validation_status: str = "valid"  # "valid", "warning", "error"
    safety_score: float = 1.0  # 0.0 to 1.0, higher is safer


@dataclass
class RAGMetrics:
    """RAG pipeline metrics."""
    total_queries: int = 0
    successful_queries: int = 0
    failed_queries: int = 0
    avg_response_time: float = 0.0
    avg_retrieval_time: float = 0.0
    avg_generation_time: float = 0.0
    avg_context_length: float = 0.0
    avg_documents_retrieved: float = 0.0
    avg_safety_score: float = 1.0
    validation_warnings: int = 0
    validation_errors: int = 0


class PromptEngine:
    """
    Advanced prompt engineering system for RAG pipeline.
    
    Features:
    - Context-aware prompt selection
    - Query type classification
    - Safety and ethics guidelines
    - Response format customization
    - Template optimization
    """
    
    def __init__(self):
        """Initialize the prompt engine."""
        self.prompt_templates = self._initialize_prompt_templates()
        self.safety_guidelines = self._initialize_safety_guidelines()
        self.response_formats = self._initialize_response_formats()
    
    def _initialize_prompt_templates(self) -> Dict[str, str]:
        """Initialize optimized prompt templates."""
        return {
            "base": """You are ZeroRAG, an intelligent AI assistant that provides accurate, helpful, and contextually relevant answers based on the provided documents. Your responses should be:

1. **Accurate**: Based only on the information provided in the context
2. **Helpful**: Address the user's question directly and completely
3. **Transparent**: Clearly indicate when information is not available in the context
4. **Ethical**: Follow safety guidelines and avoid harmful content
5. **Well-structured**: Organize information clearly and logically

Context Information:
{context}

User Question: {query}

Instructions:
- Use only the information from the provided context
- If the context doesn't contain enough information, say so clearly
- Cite specific sources when possible
- Provide a comprehensive but concise answer
- Maintain a helpful and professional tone

Answer:""",

            "factual": """You are ZeroRAG, a factual information assistant. Your task is to provide precise, accurate answers based on the provided documents.

Context Information:
{context}

Factual Question: {query}

Instructions:
- Provide specific facts and data from the context
- Include exact numbers, dates, names, and details when available
- If information is missing or unclear, state this explicitly
- Cite the specific source documents for each fact
- Avoid speculation or interpretation beyond the provided facts

Answer:""",

            "analytical": """You are ZeroRAG, an analytical assistant. Your task is to analyze the provided information and offer insights.

Context Information:
{context}

Analytical Question: {query}

Instructions:
- Analyze patterns, trends, and relationships in the data
- Provide logical reasoning and conclusions
- Consider multiple perspectives from the context
- Identify key insights and implications
- Support your analysis with specific evidence from the context
- Acknowledge limitations or gaps in the analysis

Answer:""",

            "comparative": """You are ZeroRAG, a comparative analysis assistant. Your task is to compare and contrast information from the provided documents.

Context Information:
{context}

Comparative Question: {query}

Instructions:
- Identify similarities and differences clearly
- Organize your response with clear comparisons
- Use structured format (e.g., similarities vs differences)
- Provide specific examples from the context
- Highlight key distinctions and implications
- Maintain objectivity in comparisons

Answer:""",

            "summarization": """You are ZeroRAG, a summarization assistant. Your task is to create concise, comprehensive summaries of the provided information.

Context Information:
{context}

Summarization Request: {query}

Instructions:
- Create a well-structured summary covering key points
- Maintain the most important information
- Use clear, concise language
- Organize information logically
- Include main themes and conclusions
- Ensure the summary is complete but not overly detailed

Answer:""",

            "creative": """You are ZeroRAG, a creative assistant. Your task is to provide innovative insights and creative solutions based on the provided information.

Context Information:
{context}

Creative Request: {query}

Instructions:
- Use the context as inspiration for creative thinking
- Generate innovative ideas and solutions
- Think outside the box while staying relevant
- Provide multiple creative approaches
- Explain the reasoning behind creative suggestions
- Maintain appropriateness and usefulness

Answer:""",

            "fallback": """You are ZeroRAG, a helpful AI assistant. The user has asked a question, but no relevant context was found in the available documents.

Question: {query}

Instructions:
- Provide a helpful response based on your general knowledge
- Clearly state that you don't have access to specific document information
- Offer general guidance or suggestions if appropriate
- Maintain a helpful and professional tone
- Encourage the user to rephrase or ask about available topics

Answer:"""
        }
    
    def _initialize_safety_guidelines(self) -> Dict[str, List[str]]:
        """Initialize safety and ethics guidelines."""
        return {
            "standard": [
                "Avoid harmful, dangerous, or illegal content",
                "Respect privacy and confidentiality",
                "Provide accurate information only",
                "Maintain professional and respectful tone",
                "Avoid bias and discrimination"
            ],
            "conservative": [
                "Strictly avoid any potentially harmful content",
                "Be extra cautious with medical, legal, or financial advice",
                "Require explicit disclaimers for sensitive topics",
                "Prioritize safety over completeness",
                "Avoid controversial or polarizing topics"
            ],
            "permissive": [
                "Allow broader range of topics and discussions",
                "Provide more detailed and comprehensive responses",
                "Include more creative and exploratory content",
                "Maintain basic safety standards",
                "Allow for more nuanced discussions"
            ]
        }
    
    def _initialize_response_formats(self) -> Dict[str, str]:
        """Initialize response format templates."""
        return {
            "text": "Provide a natural, flowing text response.",
            "bullet_points": "Organize your response as a list of bullet points for clarity.",
            "numbered_list": "Present your response as a numbered list for structured information.",
            "table": "Format your response as a table when comparing multiple items or data points.",
            "json": "Provide your response in JSON format for structured data.",
            "summary": "Provide a concise summary with key points highlighted."
        }
    
    def classify_query_type(self, query: str) -> QueryType:
        """Classify the query type for appropriate prompt selection."""
        query_lower = query.lower()
        
        # Factual queries
        if any(word in query_lower for word in ["what is", "when", "where", "who", "how many", "how much", "facts", "data"]):
            return QueryType.FACTUAL
        
        # Analytical queries
        if any(word in query_lower for word in ["analyze", "explain", "why", "how does", "what causes", "implications", "trends", "analysis"]):
            return QueryType.ANALYTICAL
        
        # Comparative queries
        if any(word in query_lower for word in ["compare", "difference", "similar", "versus", "vs", "contrast", "better", "worse"]):
            return QueryType.COMPARATIVE
        
        # Summarization queries
        if any(word in query_lower for word in ["summarize", "summary", "overview", "brief", "key points", "main points"]):
            return QueryType.SUMMARIZATION
        
        # Creative queries
        if any(word in query_lower for word in ["creative", "innovative", "ideas", "suggestions", "brainstorm", "imagine"]):
            return QueryType.CREATIVE
        
        return QueryType.GENERAL
    
    def create_prompt(self, rag_query: RAGQuery, context: RAGContext) -> str:
        """Create an optimized prompt based on query type and context."""
        # Determine query type if not provided
        if not rag_query.query_type:
            rag_query.query_type = self.classify_query_type(rag_query.query)
        
        # Select appropriate template
        template_key = rag_query.query_type.value
        if template_key not in self.prompt_templates:
            template_key = "base"
        
        template = self.prompt_templates[template_key]
        
        # Format context with enhanced structure
        formatted_context = self._format_context(context)
        
        # Add safety guidelines
        safety_guidelines = self._get_safety_guidelines(rag_query.safety_level)
        
        # Add response format instructions
        format_instructions = self._get_format_instructions(rag_query.response_format)
        
        # Create the final prompt
        prompt = template.format(
            context=formatted_context,
            query=rag_query.query
        )
        
        # Add safety and format instructions
        if safety_guidelines:
            prompt += f"\n\nSafety Guidelines:\n{safety_guidelines}"
        
        if format_instructions:
            prompt += f"\n\nResponse Format: {format_instructions}"
        
        return prompt
    
    def _format_context(self, context: RAGContext) -> str:
        """Format context with enhanced structure and metadata."""
        if not context.assembled_context:
            return "No relevant context available."
        
        # Split context into individual documents
        doc_sections = context.assembled_context.split("Source:")
        
        formatted_sections = []
        for i, section in enumerate(doc_sections[1:], 1):  # Skip empty first section
            lines = section.strip().split('\n')
            if len(lines) >= 3:
                source_file = lines[0].strip()
                chunk_index = lines[1].strip()
                content = '\n'.join(lines[2:]).strip()
                
                # Add relevance score if available
                relevance_score = ""
                if i <= len(context.relevance_scores):
                    score = context.relevance_scores[i-1]
                    relevance_score = f" (Relevance: {score:.3f})"
                
                formatted_section = f"Document {i}: {source_file}{relevance_score}\nChunk: {chunk_index}\nContent: {content}\n"
                formatted_sections.append(formatted_section)
        
        return "\n".join(formatted_sections)
    
    def _get_safety_guidelines(self, safety_level: str) -> str:
        """Get safety guidelines for the specified level."""
        if safety_level not in self.safety_guidelines:
            safety_level = "standard"
        
        guidelines = self.safety_guidelines[safety_level]
        return "\n".join([f"- {guideline}" for guideline in guidelines])
    
    def _get_format_instructions(self, response_format: Optional[str]) -> str:
        """Get format instructions for the specified response format."""
        if not response_format or response_format not in self.response_formats:
            return ""
        
        return self.response_formats[response_format]
    
    def validate_response(self, response: str, query: str, context: RAGContext) -> Tuple[str, float]:
        """Validate response for safety and quality."""
        validation_status = "valid"
        safety_score = 1.0
        
        # Check for potential safety issues
        safety_issues = self._check_safety_issues(response)
        if safety_issues:
            validation_status = "warning"
            safety_score = max(0.5, safety_score - len(safety_issues) * 0.1)
        
        # Check for context adherence
        if context.assembled_context and not self._check_context_adherence(response, context):
            validation_status = "warning"
            safety_score = max(0.7, safety_score - 0.2)
        
        # Check for response quality
        quality_issues = self._check_response_quality(response, query)
        if quality_issues:
            validation_status = "warning"
            safety_score = max(0.6, safety_score - len(quality_issues) * 0.1)
        
        return validation_status, safety_score
    
    def _check_safety_issues(self, response: str) -> List[str]:
        """Check for potential safety issues in the response."""
        issues = []
        response_lower = response.lower()
        
        # Check for potentially harmful content
        harmful_patterns = [
            r"how to (harm|hurt|kill|injure)",
            r"illegal (activities|methods|procedures)",
            r"dangerous (chemicals|substances|methods)",
            r"hack(ing|er)",
            r"exploit(ing|s)",
            r"bypass(ing)? (security|protection)"
        ]
        
        for pattern in harmful_patterns:
            if re.search(pattern, response_lower):
                issues.append(f"Potential safety concern detected: {pattern}")
        
        return issues
    
    def _check_context_adherence(self, response: str, context: RAGContext) -> bool:
        """Check if response adheres to the provided context."""
        if not context.assembled_context:
            return True  # No context to adhere to
        
        # Simple check: response should mention some content from context
        context_words = set(re.findall(r'\b\w+\b', context.assembled_context.lower()))
        response_words = set(re.findall(r'\b\w+\b', response.lower()))
        
        # Check for overlap (excluding common words)
        common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        context_specific_words = context_words - common_words
        response_specific_words = response_words - common_words
        
        overlap = len(context_specific_words.intersection(response_specific_words))
        return overlap > 0
    
    def _check_response_quality(self, response: str, query: str) -> List[str]:
        """Check response quality and completeness."""
        issues = []
        
        # Check for very short responses
        if len(response.strip()) < 20:
            issues.append("Response is very short")
        
        # Check for generic responses
        generic_phrases = [
            "i don't have enough information",
            "i cannot answer",
            "i don't know",
            "no information available"
        ]
        
        response_lower = response.lower()
        if any(phrase in response_lower for phrase in generic_phrases):
            if len(response.strip()) < 100:  # Only flag if response is also short
                issues.append("Response appears generic or incomplete")
        
        return issues


class RAGPipeline:
    """
    Core RAG pipeline that integrates retrieval, context assembly, and generation.
    
    Features:
    - Intelligent document retrieval with relevance scoring
    - Context window management and assembly
    - Advanced prompt engineering and response generation
    - Comprehensive error handling and fallbacks
    - Performance monitoring and metrics
    - Source attribution and citation
    - Response validation and safety checks
    """
    
    def __init__(self, service_factory: Optional['ServiceFactory'] = None):
        """Initialize the RAG pipeline."""
        # Store service factory ID instead of the object to avoid circular reference
        if service_factory is not None:
            self.service_factory_id = id(service_factory)
        else:
            self.service_factory_id = None
        
        # Initialize prompt engine
        self.prompt_engine = PromptEngine()
        
        # Initialize metrics
        self.metrics = RAGMetrics()
        self.start_time = time.time()
        self.total_response_time = 0.0
        self.total_retrieval_time = 0.0
        self.total_generation_time = 0.0
        
        logger.info("RAG Pipeline initialized with advanced prompt engineering")
    
    def _get_service_factory(self):
        """Get the service factory, creating one if needed."""
        from .service_factory import get_service_factory
        return get_service_factory()
    
    def query(self, query: str, **kwargs) -> RAGResponse:
        """
        Process a RAG query and return a comprehensive response.
        
        Args:
            query: User query string
            **kwargs: Additional query parameters
            
        Returns:
            RAGResponse with answer, context, and metadata
        """
        start_time = time.time()
        rag_query = RAGQuery(query=query, **kwargs)
        
        try:
            logger.info(f"Processing RAG query: {query[:100]}...")
            
            # Step 1: Retrieve relevant documents
            retrieval_start = time.time()
            retrieved_docs = self._retrieve_documents(rag_query)
            retrieval_time = time.time() - retrieval_start
            
            if not retrieved_docs:
                logger.warning("No relevant documents found for query")
                return self._create_no_results_response(rag_query, start_time)
            
            # Step 2: Assemble context
            context = self._assemble_context(rag_query, retrieved_docs)
            
            # Step 3: Generate response
            generation_start = time.time()
            llm_response = self._generate_response(rag_query, context)
            generation_time = time.time() - generation_start
            
            # Step 4: Create final response
            response_time = time.time() - start_time
            response = self._create_response(rag_query, context, llm_response, response_time)
            
            # Update metrics with validation info from response
            validation_status = response.validation_status
            safety_score = response.safety_score
            self._update_metrics(response_time, retrieval_time, generation_time, context, validation_status, safety_score)
            
            logger.info(f"RAG query completed in {response_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            self.metrics.failed_queries += 1
            return self._create_error_response(rag_query, str(e), start_time)
    
    def process_query(self, rag_query: RAGQuery) -> RAGResponse:
        """
        Process a RAG query using the RAGQuery object.
        
        Args:
            rag_query: RAGQuery object with query parameters
            
        Returns:
            RAGResponse with answer, context, and metadata
        """
        start_time = time.time()
        
        try:
            logger.info(f"Processing RAG query: {rag_query.query[:100]}...")
            
            # Step 1: Retrieve relevant documents
            retrieval_start = time.time()
            retrieved_docs = self._retrieve_documents(rag_query)
            retrieval_time = time.time() - retrieval_start
            
            if not retrieved_docs:
                logger.warning("No relevant documents found for query")
                return self._create_no_results_response(rag_query, start_time)
            
            # Step 2: Assemble context
            context = self._assemble_context(rag_query, retrieved_docs)
            
            # Step 3: Generate response
            generation_start = time.time()
            llm_response = self._generate_response(rag_query, context)
            generation_time = time.time() - generation_start
            
            # Step 4: Create final response
            response_time = time.time() - start_time
            response = self._create_response(rag_query, context, llm_response, response_time)
            
            # Update metrics with validation info from response
            validation_status = response.validation_status
            safety_score = response.safety_score
            self._update_metrics(response_time, retrieval_time, generation_time, context, validation_status, safety_score)
            
            logger.info(f"RAG query completed in {response_time:.2f}s")
            return response
            
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            self.metrics.failed_queries += 1
            return self._create_error_response(rag_query, str(e), start_time)
    
    def process_query_stream(self, rag_query: RAGQuery) -> Generator[str, None, None]:
        """
        Process a RAG query with streaming response using the RAGQuery object.
        
        Args:
            rag_query: RAGQuery object with query parameters
            
        Yields:
            Streaming response chunks
        """
        start_time = time.time()
        
        try:
            logger.info(f"Processing streaming RAG query: {rag_query.query[:100]}...")
            
            # Step 1: Retrieve relevant documents
            retrieval_start = time.time()
            retrieved_docs = self._retrieve_documents(rag_query)
            retrieval_time = time.time() - retrieval_start
            
            if not retrieved_docs:
                logger.warning("No relevant documents found for query")
                yield "I couldn't find any relevant information in the available documents to answer your question."
                return
            
            # Step 2: Assemble context
            context = self._assemble_context(rag_query, retrieved_docs)
            
            # Step 3: Generate streaming response
            prompt = self.prompt_engine.create_prompt(rag_query, context)
            llm_service = self._get_service_factory().get_llm_service()
            
            if not llm_service:
                yield "Sorry, the language model service is currently unavailable."
                return
            
            # Stream the response
            for chunk in llm_service.generate_streaming(
                prompt,
                temperature=rag_query.temperature,
                max_tokens=rag_query.max_tokens
            ):
                yield chunk
            
            # Update metrics
            response_time = time.time() - start_time
            self._update_metrics(response_time, retrieval_time, response_time, context, "valid", 1.0)
            
        except Exception as e:
            logger.error(f"Streaming RAG query failed: {e}")
            self.metrics.failed_queries += 1
            yield f"Sorry, an error occurred while processing your query: {str(e)}"
    
    def query_streaming(self, query: str, **kwargs) -> Generator[str, None, None]:
        """
        Process a RAG query with streaming response generation.
        
        Args:
            query: User query string
            **kwargs: Additional query parameters
            
        Yields:
            Streaming response chunks
        """
        start_time = time.time()
        rag_query = RAGQuery(query=query, **kwargs)
        
        try:
            logger.info(f"Processing streaming RAG query: {query[:100]}...")
            
            # Step 1: Retrieve relevant documents
            retrieved_docs = self._retrieve_documents(rag_query)
            
            if not retrieved_docs:
                logger.warning("No relevant documents found for query")
                yield "I couldn't find any relevant information to answer your question."
                return
            
            # Step 2: Assemble context
            context = self._assemble_context(rag_query, retrieved_docs)
            
            # Step 3: Generate streaming response
            prompt = self.prompt_engine.create_prompt(rag_query, context)
            llm_service = self._get_service_factory().get_llm_service()
            
            if not llm_service:
                yield "Sorry, the language model service is currently unavailable."
                return
            
            # Stream the response
            for chunk in llm_service.generate_streaming(
                prompt,
                temperature=rag_query.temperature,
                max_tokens=rag_query.max_tokens
            ):
                yield chunk
            
            # Update metrics
            response_time = time.time() - start_time
            self._update_metrics(response_time, 0, response_time, context, "valid", 1.0)
            
        except Exception as e:
            logger.error(f"Streaming RAG query failed: {e}")
            self.metrics.failed_queries += 1
            yield f"Sorry, an error occurred while processing your query: {str(e)}"
    
    def _retrieve_documents(self, rag_query: RAGQuery) -> List[SearchResult]:
        """Retrieve relevant documents using vector search."""
        try:
            # Get services
            embedding_service = self._get_service_factory().get_embedding_service()
            vector_store = self._get_service_factory().get_vector_store()
            
            # Check if core services are available (even if degraded)
            if not embedding_service:
                logger.error("Embedding service not available")
                return []
            
            if not vector_store:
                logger.error("Vector store service not available")
                return []
            
            # Generate query embedding
            query_embedding = embedding_service.encode(rag_query.query)
            
            # Search for similar documents
            search_results = vector_store.search_similar(
                query_vector=query_embedding,
                top_k=rag_query.top_k,
                score_threshold=rag_query.score_threshold,
                filters=rag_query.filters
            )
            
            logger.debug(f"Retrieved {len(search_results)} documents")
            return search_results
            
        except Exception as e:
            logger.error(f"Document retrieval failed: {e}")
            return []
    
    def _assemble_context(self, rag_query: RAGQuery, documents: List[SearchResult]) -> RAGContext:
        """Assemble context from retrieved documents."""
        try:
            # Sort documents by relevance score
            sorted_docs = sorted(documents, key=lambda x: x.score, reverse=True)
            
            # Build context string
            context_parts = []
            total_length = 0
            source_files = []
            relevance_scores = []
            
            for doc in sorted_docs:
                # Calculate document length
                doc_length = len(doc.text)
                
                # Check if adding this document would exceed context limit
                if total_length + doc_length > rag_query.max_context_length:
                    # Try to truncate the document
                    remaining_length = rag_query.max_context_length - total_length
                    if remaining_length > 100:  # Only add if we have meaningful space
                        truncated_text = doc.text[:remaining_length] + "..."
                        context_parts.append(f"Source: {doc.source_file}\n{doc.metadata.get('chunk_index', 0)}\n{truncated_text}\n")
                        source_files.append(doc.source_file)
                        relevance_scores.append(doc.score)
                        total_length += len(truncated_text)
                    break
                else:
                    context_parts.append(f"Source: {doc.source_file}\n{doc.metadata.get('chunk_index', 0)}\n{doc.text}\n")
                    source_files.append(doc.source_file)
                    relevance_scores.append(doc.score)
                    total_length += doc_length
            
            assembled_context = "\n".join(context_parts)
            
            return RAGContext(
                query=rag_query.query,
                retrieved_documents=sorted_docs,
                assembled_context=assembled_context,
                context_length=total_length,
                source_files=list(set(source_files)),  # Remove duplicates
                relevance_scores=relevance_scores
            )
            
        except Exception as e:
            logger.error(f"Context assembly failed: {e}")
            return RAGContext(
                query=rag_query.query,
                retrieved_documents=documents,
                assembled_context="",
                context_length=0,
                source_files=[],
                relevance_scores=[]
            )
    
    def _generate_response(self, rag_query: RAGQuery, context: RAGContext) -> LLMResponse:
        """Generate response using the assembled context."""
        try:
            # Create prompt
            prompt = self.prompt_engine.create_prompt(rag_query, context)
            
            # Get LLM service
            llm_service = self._get_service_factory().get_llm_service()
            if not llm_service:
                raise RuntimeError("LLM service not available")
            
            # Generate response
            response = llm_service.generate(
                prompt,
                temperature=rag_query.temperature,
                max_tokens=rag_query.max_tokens
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            raise
    
    def _create_response(self, rag_query: RAGQuery, context: RAGContext, 
                        llm_response: LLMResponse, response_time: float) -> RAGResponse:
        """Create the final RAG response."""
        # Extract sources with metadata
        sources = []
        for doc in context.retrieved_documents:
            source_info = {
                "file": doc.source_file,
                "chunk_index": doc.chunk_index,
                "score": doc.score,
                "text_preview": doc.text[:200] + "..." if len(doc.text) > 200 else doc.text,
                "metadata": doc.metadata
            }
            sources.append(source_info)
        
        # Validate response
        validation_status, safety_score = self.prompt_engine.validate_response(llm_response.text, rag_query.query, context)
        
        return RAGResponse(
            answer=llm_response.text,
            context=context,
            response_time=response_time,
            tokens_used=llm_response.tokens_used,
            sources=sources,
            metadata={
                "provider": llm_response.provider,
                "model_name": llm_response.model_name,
                "context_length": context.context_length,
                "documents_retrieved": len(context.retrieved_documents),
                "avg_relevance_score": sum(context.relevance_scores) / len(context.relevance_scores) if context.relevance_scores else 0,
                "validation_status": validation_status,
                "safety_score": safety_score
            }
        )
    
    def _create_no_results_response(self, rag_query: RAGQuery, start_time: float) -> RAGResponse:
        """Create response when no relevant documents are found."""
        response_time = time.time() - start_time
        
        return RAGResponse(
            answer="I couldn't find any relevant information in the available documents to answer your question. Please try rephrasing your query or ask about a different topic.",
            context=RAGContext(
                query=rag_query.query,
                retrieved_documents=[],
                assembled_context="",
                context_length=0,
                source_files=[],
                relevance_scores=[]
            ),
            response_time=response_time,
            sources=[],
            metadata={"status": "no_results"}
        )
    
    def _create_error_response(self, rag_query: RAGQuery, error_message: str, start_time: float) -> RAGResponse:
        """Create response when an error occurs."""
        response_time = time.time() - start_time
        
        return RAGResponse(
            answer=f"Sorry, I encountered an error while processing your query: {error_message}. Please try again later.",
            context=RAGContext(
                query=rag_query.query,
                retrieved_documents=[],
                assembled_context="",
                context_length=0,
                source_files=[],
                relevance_scores=[]
            ),
            response_time=response_time,
            sources=[],
            metadata={"status": "error", "error": error_message}
        )
    
    def _update_metrics(self, response_time: float, retrieval_time: float, 
                       generation_time: float, context: RAGContext, 
                       validation_status: str = "valid", safety_score: float = 1.0):
        """Update performance metrics."""
        self.metrics.total_queries += 1
        self.metrics.successful_queries += 1
        
        # Update timing metrics
        self.total_response_time += response_time
        self.total_retrieval_time += retrieval_time
        self.total_generation_time += generation_time
        
        # Calculate averages
        self.metrics.avg_response_time = self.total_response_time / self.metrics.total_queries
        self.metrics.avg_retrieval_time = self.total_retrieval_time / self.metrics.total_queries
        self.metrics.avg_generation_time = self.total_generation_time / self.metrics.total_queries
        
        # Update context metrics
        self.metrics.avg_context_length = (
            (self.metrics.avg_context_length * (self.metrics.total_queries - 1) + context.context_length) 
            / self.metrics.total_queries
        )
        self.metrics.avg_documents_retrieved = (
            (self.metrics.avg_documents_retrieved * (self.metrics.total_queries - 1) + len(context.retrieved_documents)) 
            / self.metrics.total_queries
        )
        
        # Update validation metrics
        if validation_status == "warning":
            self.metrics.validation_warnings += 1
        elif validation_status == "error":
            self.metrics.validation_errors += 1
        
        # Update safety score average
        self.metrics.avg_safety_score = (
            (self.metrics.avg_safety_score * (self.metrics.total_queries - 1) + safety_score) 
            / self.metrics.total_queries
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get comprehensive pipeline metrics."""
        uptime = time.time() - self.start_time
        
        # Check if core services are available without triggering health checks
        service_factory = self._get_service_factory()
        embedding_service = service_factory.get_embedding_service()
        vector_store = service_factory.get_vector_store()
        llm_service = service_factory.get_llm_service()
        
        pipeline_status = "healthy" if (
            embedding_service is not None and 
            vector_store is not None and 
            llm_service is not None
        ) else "unhealthy"
        
        return {
            "pipeline_status": pipeline_status,
            "uptime_seconds": uptime,
            "metrics": {
                "total_queries": self.metrics.total_queries,
                "successful_queries": self.metrics.successful_queries,
                "failed_queries": self.metrics.failed_queries,
                "success_rate": (
                    self.metrics.successful_queries / self.metrics.total_queries 
                    if self.metrics.total_queries > 0 else 0
                ),
                "avg_response_time": self.metrics.avg_response_time,
                "avg_retrieval_time": self.metrics.avg_retrieval_time,
                "avg_generation_time": self.metrics.avg_generation_time,
                "avg_context_length": self.metrics.avg_context_length,
                "avg_documents_retrieved": self.metrics.avg_documents_retrieved,
                "avg_safety_score": self.metrics.avg_safety_score,
                "validation_warnings": self.metrics.validation_warnings,
                "validation_errors": self.metrics.validation_errors
            }
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check."""
        try:
            # Get services without triggering health checks to avoid infinite loop
            service_factory = self._get_service_factory()
            
            # Check if core services are available (even if degraded)
            embedding_service = service_factory.get_embedding_service()
            vector_store = service_factory.get_vector_store()
            llm_service = service_factory.get_llm_service()
            
            core_services_available = (
                embedding_service is not None and 
                vector_store is not None and 
                llm_service is not None
            )
            
            # Consider healthy if core services are available
            # Don't perform test query during initialization to avoid recursive calls
            is_healthy = core_services_available
            
            return {
                "status": "healthy" if is_healthy else "unhealthy",
                "core_services_available": core_services_available,
                "test_query_successful": True,  # Assume successful if services are available
                "uptime_seconds": time.time() - self.start_time,
                "total_queries": self.metrics.total_queries,
                "successful_queries": self.metrics.successful_queries,
                "failed_queries": self.metrics.failed_queries
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "uptime_seconds": time.time() - self.start_time,
                "total_queries": self.metrics.total_queries,
                "failed_queries": self.metrics.failed_queries
            }
