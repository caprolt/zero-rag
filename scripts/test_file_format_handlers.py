#!/usr/bin/env python3
"""
Test File Format Handlers

This script tests the enhanced file format handlers for CSV and Markdown processing
in the ZeroRAG document processor.
"""

import sys
import os
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.document_processor import get_document_processor
from config import get_config


def test_csv_processing():
    """Test enhanced CSV processing features."""
    print("=" * 60)
    print("Testing Enhanced CSV Processing")
    print("=" * 60)
    
    config = get_config()
    processor = get_document_processor(config)
    
    # Test file path
    csv_file = Path("data/test_documents/test_data.csv")
    
    if not csv_file.exists():
        print(f"❌ Test CSV file not found: {csv_file}")
        return False
    
    try:
        print(f"📄 Processing CSV file: {csv_file.name}")
        start_time = time.time()
        
        # Process the document
        chunks, metadata = processor.process_document(csv_file)
        
        processing_time = time.time() - start_time
        
        print(f"✅ CSV processing completed in {processing_time:.3f}s")
        print(f"📊 Document metadata:")
        print(f"   - File size: {metadata.file_size} bytes")
        print(f"   - Word count: {metadata.word_count}")
        print(f"   - Character count: {metadata.char_count}")
        print(f"   - Chunks generated: {metadata.chunk_count}")
        print(f"   - Processing time: {metadata.processing_time:.3f}s")
        
        print(f"\n📋 Generated chunks ({len(chunks)}):")
        for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
            print(f"   Chunk {i+1}: {chunk.chunk_id}")
            print(f"   Text preview: {chunk.text[:100]}...")
            print(f"   Word count: {chunk.metadata['word_count']}")
            print()
        
        if len(chunks) > 3:
            print(f"   ... and {len(chunks) - 3} more chunks")
        
        # Validate CSV-specific features
        first_chunk_text = chunks[0].text if chunks else ""
        
        # Check for data type analysis
        if "Data Types:" in first_chunk_text:
            print("✅ Data type analysis detected")
        else:
            print("❌ Data type analysis not found")
        
        # Check for structured row formatting
        if "Name: " in first_chunk_text and "Age: " in first_chunk_text:
            print("✅ Structured row formatting detected")
        else:
            print("❌ Structured row formatting not found")
        
        # Check for summary information
        if "Total Rows:" in first_chunk_text and "Total Columns:" in first_chunk_text:
            print("✅ Summary information detected")
        else:
            print("❌ Summary information not found")
        
        return True
        
    except Exception as e:
        print(f"❌ CSV processing failed: {e}")
        return False


def test_markdown_processing():
    """Test enhanced Markdown processing features."""
    print("\n" + "=" * 60)
    print("Testing Enhanced Markdown Processing")
    print("=" * 60)
    
    config = get_config()
    processor = get_document_processor(config)
    
    # Test file path
    md_file = Path("data/test_documents/test_document.md")
    
    if not md_file.exists():
        print(f"❌ Test Markdown file not found: {md_file}")
        return False
    
    try:
        print(f"📄 Processing Markdown file: {md_file.name}")
        start_time = time.time()
        
        # Process the document
        chunks, metadata = processor.process_document(md_file)
        
        processing_time = time.time() - start_time
        
        print(f"✅ Markdown processing completed in {processing_time:.3f}s")
        print(f"📊 Document metadata:")
        print(f"   - File size: {metadata.file_size} bytes")
        print(f"   - Word count: {metadata.word_count}")
        print(f"   - Character count: {metadata.char_count}")
        print(f"   - Chunks generated: {metadata.chunk_count}")
        print(f"   - Processing time: {metadata.processing_time:.3f}s")
        
        print(f"\n📋 Generated chunks ({len(chunks)}):")
        for i, chunk in enumerate(chunks[:3]):  # Show first 3 chunks
            print(f"   Chunk {i+1}: {chunk.chunk_id}")
            print(f"   Text preview: {chunk.text[:100]}...")
            print(f"   Word count: {chunk.metadata['word_count']}")
            print()
        
        if len(chunks) > 3:
            print(f"   ... and {len(chunks) - 3} more chunks")
        
        # Validate Markdown-specific features
        all_text = " ".join(chunk.text for chunk in chunks)
        
        # Check for header hierarchy
        if "Test Markdown Document" in all_text and "=" in all_text:
            print("✅ Header hierarchy processing detected")
        else:
            print("❌ Header hierarchy processing not found")
        
        # Check for table processing
        if "Table:" in all_text and "|" in all_text:
            print("✅ Table processing detected")
        else:
            print("❌ Table processing not found")
        
        # Check for list processing
        if "• Feature" in all_text or "1. First step" in all_text:
            print("✅ List processing detected")
        else:
            print("❌ List processing not found")
        
        # Check for link processing
        if "(URL:" in all_text:
            print("✅ Link processing detected")
        else:
            print("❌ Link processing not found")
        
        # Check for code block processing
        if "[Code Block:" in all_text:
            print("✅ Code block processing detected")
        else:
            print("❌ Code block processing not found")
        
        # Check for quote processing
        if "Quote:" in all_text:
            print("✅ Quote processing detected")
        else:
            print("❌ Quote processing not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Markdown processing failed: {e}")
        return False


def test_text_processing():
    """Test basic text processing."""
    print("\n" + "=" * 60)
    print("Testing Text Processing")
    print("=" * 60)
    
    config = get_config()
    processor = get_document_processor(config)
    
    # Test file path
    txt_file = Path("data/test_documents/test_document.txt")
    
    if not txt_file.exists():
        print(f"❌ Test text file not found: {txt_file}")
        return False
    
    try:
        print(f"📄 Processing text file: {txt_file.name}")
        start_time = time.time()
        
        # Process the document
        chunks, metadata = processor.process_document(txt_file)
        
        processing_time = time.time() - start_time
        
        print(f"✅ Text processing completed in {processing_time:.3f}s")
        print(f"📊 Document metadata:")
        print(f"   - File size: {metadata.file_size} bytes")
        print(f"   - Word count: {metadata.word_count}")
        print(f"   - Character count: {metadata.char_count}")
        print(f"   - Chunks generated: {metadata.chunk_count}")
        print(f"   - Processing time: {metadata.processing_time:.3f}s")
        
        print(f"\n📋 Generated chunks ({len(chunks)}):")
        for i, chunk in enumerate(chunks[:2]):  # Show first 2 chunks
            print(f"   Chunk {i+1}: {chunk.chunk_id}")
            print(f"   Text preview: {chunk.text[:100]}...")
            print(f"   Word count: {chunk.metadata['word_count']}")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Text processing failed: {e}")
        return False


def test_error_handling():
    """Test error handling for unsupported files."""
    print("\n" + "=" * 60)
    print("Testing Error Handling")
    print("=" * 60)
    
    config = get_config()
    processor = get_document_processor(config)
    
    # Test with non-existent file
    try:
        processor.process_document("non_existent_file.txt")
        print("❌ Should have raised error for non-existent file")
        return False
    except ValueError as e:
        print(f"✅ Correctly handled non-existent file: {e}")
    
    # Test with unsupported file type
    try:
        # Create a temporary unsupported file
        unsupported_file = Path("data/test_documents/test.unsupported")
        unsupported_file.write_text("test content")
        
        processor.process_document(unsupported_file)
        print("❌ Should have raised error for unsupported file type")
        
        # Clean up
        unsupported_file.unlink()
        return False
    except ValueError as e:
        print(f"✅ Correctly handled unsupported file type: {e}")
        # Clean up
        if unsupported_file.exists():
            unsupported_file.unlink()
    
    return True


def test_performance_metrics():
    """Test performance metrics collection."""
    print("\n" + "=" * 60)
    print("Testing Performance Metrics")
    print("=" * 60)
    
    config = get_config()
    processor = get_document_processor(config)
    
    # Get initial metrics
    initial_metrics = processor.get_processing_metrics()
    print(f"📊 Initial metrics:")
    print(f"   - Total documents: {initial_metrics['total_documents']}")
    print(f"   - Total chunks: {initial_metrics['total_chunks']}")
    print(f"   - Total processing time: {initial_metrics['total_processing_time']:.3f}s")
    
    # Process a test document to update metrics
    test_file = Path("data/test_documents/test_document.txt")
    if test_file.exists():
        try:
            processor.process_document(test_file)
            
            # Get updated metrics
            updated_metrics = processor.get_processing_metrics()
            print(f"\n📊 Updated metrics:")
            print(f"   - Total documents: {updated_metrics['total_documents']}")
            print(f"   - Total chunks: {updated_metrics['total_chunks']}")
            print(f"   - Total processing time: {updated_metrics['total_processing_time']:.3f}s")
            print(f"   - Average time per document: {updated_metrics['average_time_per_document']:.3f}s")
            print(f"   - Average chunks per document: {updated_metrics['average_chunks_per_document']:.1f}")
            print(f"   - Error count: {updated_metrics['error_count']}")
            
            print("✅ Performance metrics collection working")
            return True
            
        except Exception as e:
            print(f"❌ Failed to update metrics: {e}")
            return False
    else:
        print("❌ Test file not found for metrics testing")
        return False


def test_health_check():
    """Test health check functionality."""
    print("\n" + "=" * 60)
    print("Testing Health Check")
    print("=" * 60)
    
    config = get_config()
    processor = get_document_processor(config)
    
    try:
        health_status = processor.health_check()
        
        print(f"📊 Health check results:")
        print(f"   - Status: {health_status['status']}")
        print(f"   - Supported formats: {health_status['supported_formats']}")
        print(f"   - Configuration:")
        for key, value in health_status['configuration'].items():
            print(f"     * {key}: {value}")
        
        print("✅ Health check working")
        return True
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False


def main():
    """Run all tests."""
    print("🚀 Starting File Format Handlers Testing")
    print("=" * 80)
    
    # Track test results
    test_results = []
    
    # Run tests
    test_results.append(("CSV Processing", test_csv_processing()))
    test_results.append(("Markdown Processing", test_markdown_processing()))
    test_results.append(("Text Processing", test_text_processing()))
    test_results.append(("Error Handling", test_error_handling()))
    test_results.append(("Performance Metrics", test_performance_metrics()))
    test_results.append(("Health Check", test_health_check()))
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 Test Summary")
    print("=" * 80)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📊 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! File format handlers are working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1


if __name__ == "__main__":
    exit(main())
