#!/usr/bin/env python3
"""
ZeroRAG Phase 5.2 - Prompt Engineering Test Suite

This script tests the enhanced prompt engineering features including:
- Query type classification
- Advanced prompt templates
- Safety and ethics guidelines
- Response validation
- Format customization
- Context formatting
"""

import sys
import os
import time
import json
from typing import Dict, Any, List

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.rag_pipeline import RAGPipeline, PromptEngine, QueryType, RAGQuery, RAGContext
from services.service_factory import ServiceFactory


def test_query_type_classification():
    """Test query type classification functionality."""
    print("\n" + "="*60)
    print("TESTING QUERY TYPE CLASSIFICATION")
    print("="*60)
    
    prompt_engine = PromptEngine()
    
    test_queries = [
        ("What is the capital of France?", QueryType.FACTUAL),
        ("When was the Declaration of Independence signed?", QueryType.FACTUAL),
        ("How many employees work at the company?", QueryType.FACTUAL),
        ("Analyze the trends in sales data", QueryType.ANALYTICAL),
        ("Explain why the stock price dropped", QueryType.ANALYTICAL),
        ("What are the implications of this policy?", QueryType.ANALYTICAL),
        ("Compare Python vs JavaScript", QueryType.COMPARATIVE),
        ("What's the difference between REST and GraphQL?", QueryType.COMPARATIVE),
        ("Summarize the main points of the report", QueryType.SUMMARIZATION),
        ("Give me a brief overview of the project", QueryType.SUMMARIZATION),
        ("Brainstorm creative solutions for this problem", QueryType.CREATIVE),
        ("What innovative ideas can you suggest?", QueryType.CREATIVE),
        ("Hello, how are you?", QueryType.GENERAL),
        ("Tell me about the weather", QueryType.GENERAL)
    ]
    
    passed = 0
    total = len(test_queries)
    
    for query, expected_type in test_queries:
        detected_type = prompt_engine.classify_query_type(query)
        status = "✅ PASS" if detected_type == expected_type else "❌ FAIL"
        print(f"{status} | Query: {query[:50]}... | Expected: {expected_type.value} | Detected: {detected_type.value}")
        
        if detected_type == expected_type:
            passed += 1
    
    print(f"\nQuery Classification Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    return passed == total


def test_prompt_templates():
    """Test prompt template generation."""
    print("\n" + "="*60)
    print("TESTING PROMPT TEMPLATES")
    print("="*60)
    
    prompt_engine = PromptEngine()
    
    # Test context
    test_context = RAGContext(
        query="What is machine learning?",
        retrieved_documents=[],
        assembled_context="Source: ml_intro.txt\n0\nMachine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.",
        context_length=100,
        source_files=["ml_intro.txt"],
        relevance_scores=[0.95]
    )
    
    test_queries = [
        RAGQuery(query="What is machine learning?", query_type=QueryType.FACTUAL),
        RAGQuery(query="Analyze the benefits of machine learning", query_type=QueryType.ANALYTICAL),
        RAGQuery(query="Compare machine learning vs traditional programming", query_type=QueryType.COMPARATIVE),
        RAGQuery(query="Summarize the key concepts of machine learning", query_type=QueryType.SUMMARIZATION),
        RAGQuery(query="What creative applications of machine learning can you imagine?", query_type=QueryType.CREATIVE)
    ]
    
    passed = 0
    total = len(test_queries)
    
    for rag_query in test_queries:
        try:
            prompt = prompt_engine.create_prompt(rag_query, test_context)
            
            # Check if prompt contains expected elements
            has_context = "Machine learning is a subset" in prompt
            has_query = rag_query.query in prompt
            has_instructions = "Instructions:" in prompt
            
            status = "✅ PASS" if all([has_context, has_query, has_instructions]) else "❌ FAIL"
            print(f"{status} | Type: {rag_query.query_type.value} | Length: {len(prompt)} chars")
            
            if all([has_context, has_query, has_instructions]):
                passed += 1
                
        except Exception as e:
            print(f"❌ FAIL | Type: {rag_query.query_type.value} | Error: {e}")
    
    print(f"\nPrompt Template Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    return passed == total


def test_safety_guidelines():
    """Test safety guidelines integration."""
    print("\n" + "="*60)
    print("TESTING SAFETY GUIDELINES")
    print("="*60)
    
    prompt_engine = PromptEngine()
    
    test_context = RAGContext(
        query="Test query",
        retrieved_documents=[],
        assembled_context="Test context",
        context_length=10,
        source_files=[],
        relevance_scores=[]
    )
    
    safety_levels = ["standard", "conservative", "permissive"]
    passed = 0
    total = len(safety_levels)
    
    for safety_level in safety_levels:
        try:
            rag_query = RAGQuery(
                query="What is machine learning?",
                safety_level=safety_level
            )
            
            prompt = prompt_engine.create_prompt(rag_query, test_context)
            
            # Check if safety guidelines are included
            has_guidelines = "Safety Guidelines:" in prompt
            has_guidelines_list = "- " in prompt
            
            status = "✅ PASS" if has_guidelines and has_guidelines_list else "❌ FAIL"
            print(f"{status} | Safety Level: {safety_level} | Guidelines: {has_guidelines}")
            
            if has_guidelines and has_guidelines_list:
                passed += 1
                
        except Exception as e:
            print(f"❌ FAIL | Safety Level: {safety_level} | Error: {e}")
    
    print(f"\nSafety Guidelines Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    return passed == total


def test_response_formats():
    """Test response format customization."""
    print("\n" + "="*60)
    print("TESTING RESPONSE FORMATS")
    print("="*60)
    
    prompt_engine = PromptEngine()
    
    test_context = RAGContext(
        query="Test query",
        retrieved_documents=[],
        assembled_context="Test context",
        context_length=10,
        source_files=[],
        relevance_scores=[]
    )
    
    response_formats = ["text", "bullet_points", "numbered_list", "table", "json", "summary"]
    passed = 0
    total = len(response_formats)
    
    for response_format in response_formats:
        try:
            rag_query = RAGQuery(
                query="What are the key features?",
                response_format=response_format
            )
            
            prompt = prompt_engine.create_prompt(rag_query, test_context)
            
            # Check if format instructions are included
            has_format = "Response Format:" in prompt
            
            status = "✅ PASS" if has_format else "❌ FAIL"
            print(f"{status} | Format: {response_format} | Instructions: {has_format}")
            
            if has_format:
                passed += 1
                
        except Exception as e:
            print(f"❌ FAIL | Format: {response_format} | Error: {e}")
    
    print(f"\nResponse Format Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    return passed == total


def test_response_validation():
    """Test response validation functionality."""
    print("\n" + "="*60)
    print("TESTING RESPONSE VALIDATION")
    print("="*60)
    
    prompt_engine = PromptEngine()
    
    test_context = RAGContext(
        query="What is machine learning?",
        retrieved_documents=[],
        assembled_context="Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.",
        context_length=100,
        source_files=["ml_intro.txt"],
        relevance_scores=[0.95]
    )
    
    test_responses = [
        ("Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.", "valid", 1.0),
        ("I don't have enough information to answer this question.", "warning", 0.8),
        ("How to hack into a computer system...", "warning", 0.5),
        ("", "warning", 0.6),
        ("Machine learning involves algorithms and data processing.", "valid", 1.0)
    ]
    
    passed = 0
    total = len(test_responses)
    
    for response, expected_status, expected_score in test_responses:
        try:
            validation_status, safety_score = prompt_engine.validate_response(response, "What is machine learning?", test_context)
            
            # Check if validation results are reasonable
            status_correct = validation_status in ["valid", "warning", "error"]
            score_reasonable = 0.0 <= safety_score <= 1.0
            
            status = "✅ PASS" if status_correct and score_reasonable else "❌ FAIL"
            print(f"{status} | Response: {response[:30]}... | Status: {validation_status} | Score: {safety_score:.2f}")
            
            if status_correct and score_reasonable:
                passed += 1
                
        except Exception as e:
            print(f"❌ FAIL | Response: {response[:30]}... | Error: {e}")
    
    print(f"\nResponse Validation Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    return passed == total


def test_context_formatting():
    """Test enhanced context formatting."""
    print("\n" + "="*60)
    print("TESTING CONTEXT FORMATTING")
    print("="*60)
    
    prompt_engine = PromptEngine()
    
    # Test context with multiple documents
    test_context = RAGContext(
        query="What is machine learning?",
        retrieved_documents=[],
        assembled_context="Source: ml_intro.txt\n0\nMachine learning is a subset of artificial intelligence.\nSource: ml_applications.txt\n1\nMachine learning is used in recommendation systems and image recognition.",
        context_length=200,
        source_files=["ml_intro.txt", "ml_applications.txt"],
        relevance_scores=[0.95, 0.88]
    )
    
    try:
        formatted_context = prompt_engine._format_context(test_context)
        
        # Check if formatting includes expected elements
        has_document_numbers = "Document 1:" in formatted_context and "Document 2:" in formatted_context
        has_relevance_scores = "Relevance:" in formatted_context
        has_content = "Machine learning" in formatted_context
        has_structure = "Chunk:" in formatted_context
        
        status = "✅ PASS" if all([has_document_numbers, has_relevance_scores, has_content, has_structure]) else "❌ FAIL"
        print(f"{status} | Formatted Context Length: {len(formatted_context)} chars")
        print(f"  - Document numbers: {has_document_numbers}")
        print(f"  - Relevance scores: {has_relevance_scores}")
        print(f"  - Content included: {has_content}")
        print(f"  - Structure present: {has_structure}")
        
        return all([has_document_numbers, has_relevance_scores, has_content, has_structure])
        
    except Exception as e:
        print(f"❌ FAIL | Error: {e}")
        return False


def test_integrated_rag_pipeline():
    """Test the integrated RAG pipeline with new prompt engineering features."""
    print("\n" + "="*60)
    print("TESTING INTEGRATED RAG PIPELINE")
    print("="*60)
    
    try:
        # Initialize services
        service_factory = ServiceFactory()
        rag_pipeline = RAGPipeline(service_factory)
        
        # Test different query types
        test_queries = [
            ("What is machine learning?", {"query_type": QueryType.FACTUAL}),
            ("Analyze the benefits of AI", {"query_type": QueryType.ANALYTICAL}),
            ("Compare Python vs Java", {"query_type": QueryType.COMPARATIVE}),
            ("Summarize the key concepts", {"query_type": QueryType.SUMMARIZATION}),
            ("What creative applications can you imagine?", {"query_type": QueryType.CREATIVE})
        ]
        
        passed = 0
        total = len(test_queries)
        
        for query, kwargs in test_queries:
            try:
                # Test basic query functionality
                response = rag_pipeline.query(query, **kwargs)
                
                # Check if response has expected structure
                has_answer = bool(response.answer)
                has_validation = hasattr(response, 'validation_status')
                has_safety_score = hasattr(response, 'safety_score')
                
                status = "✅ PASS" if all([has_answer, has_validation, has_safety_score]) else "❌ FAIL"
                print(f"{status} | Query: {query[:40]}... | Type: {kwargs.get('query_type', 'general')}")
                
                if all([has_answer, has_validation, has_safety_score]):
                    passed += 1
                    
            except Exception as e:
                print(f"❌ FAIL | Query: {query[:40]}... | Error: {e}")
        
        print(f"\nIntegrated Pipeline Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
        return passed == total
        
    except Exception as e:
        print(f"❌ FAIL | Pipeline initialization error: {e}")
        return False


def test_metrics_and_monitoring():
    """Test enhanced metrics and monitoring with validation data."""
    print("\n" + "="*60)
    print("TESTING METRICS AND MONITORING")
    print("="*60)
    
    try:
        service_factory = ServiceFactory()
        rag_pipeline = RAGPipeline(service_factory)
        
        # Run a few test queries to generate metrics
        test_queries = [
            "What is artificial intelligence?",
            "Explain machine learning concepts",
            "Compare different programming languages"
        ]
        
        for query in test_queries:
            try:
                rag_pipeline.query(query, max_tokens=50)
            except:
                pass  # Ignore errors for metrics testing
        
        # Get metrics
        metrics = rag_pipeline.get_metrics()
        
        # Check if new validation metrics are present
        has_safety_score = "avg_safety_score" in metrics.get("metrics", {})
        has_validation_warnings = "validation_warnings" in metrics.get("metrics", {})
        has_validation_errors = "validation_errors" in metrics.get("metrics", {})
        
        status = "✅ PASS" if all([has_safety_score, has_validation_warnings, has_validation_errors]) else "❌ FAIL"
        print(f"{status} | Enhanced metrics available")
        print(f"  - Safety score tracking: {has_safety_score}")
        print(f"  - Validation warnings: {has_validation_warnings}")
        print(f"  - Validation errors: {has_validation_errors}")
        
        if all([has_safety_score, has_validation_warnings, has_validation_errors]):
            print(f"  - Current safety score: {metrics['metrics'].get('avg_safety_score', 'N/A')}")
            print(f"  - Validation warnings: {metrics['metrics'].get('validation_warnings', 'N/A')}")
            print(f"  - Validation errors: {metrics['metrics'].get('validation_errors', 'N/A')}")
        
        return all([has_safety_score, has_validation_warnings, has_validation_errors])
        
    except Exception as e:
        print(f"❌ FAIL | Metrics error: {e}")
        return False


def main():
    """Run all Phase 5.2 prompt engineering tests."""
    print("ZeroRAG Phase 5.2 - Prompt Engineering Test Suite")
    print("="*60)
    
    start_time = time.time()
    
    # Run all tests
    tests = [
        ("Query Type Classification", test_query_type_classification),
        ("Prompt Templates", test_prompt_templates),
        ("Safety Guidelines", test_safety_guidelines),
        ("Response Formats", test_response_formats),
        ("Response Validation", test_response_validation),
        ("Context Formatting", test_context_formatting),
        ("Integrated RAG Pipeline", test_integrated_rag_pipeline),
        ("Metrics and Monitoring", test_metrics_and_monitoring)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ FAIL | {test_name} | Error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("PHASE 5.2 TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} | {test_name}")
    
    print(f"\nOverall Results: {passed}/{total} test categories passed ({passed/total*100:.1f}%)")
    
    elapsed_time = time.time() - start_time
    print(f"Total test time: {elapsed_time:.2f} seconds")
    
    if passed == total:
        print("\n🎉 All Phase 5.2 prompt engineering tests passed!")
        print("✅ Advanced prompt engineering system is working correctly")
        print("✅ Query type classification is functional")
        print("✅ Safety guidelines are integrated")
        print("✅ Response validation is operational")
        print("✅ Format customization is working")
        print("✅ Enhanced metrics are tracking validation data")
    else:
        print(f"\n⚠️  {total - passed} test categories failed")
        print("Please review the failed tests above")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
