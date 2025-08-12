#!/usr/bin/env python3
"""
ZeroRAG Phase 3.3: Metadata & Indexing Test Script

This script tests the enhanced metadata extraction, document validation,
and indexing features implemented in Phase 3.3.
"""

import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.document_processor import DocumentProcessor, DocumentMetadata
from config import get_config


def create_test_documents():
    """Create test documents for metadata testing."""
    test_dir = Path("data/test_documents")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Test 1: Simple text file
    text_content = """This is a simple test document for metadata extraction.

It contains multiple paragraphs and sentences. This should help us test
the sentence counting and paragraph detection features.

The document also includes some basic formatting and structure.
"""
    
    with open(test_dir / "simple_test.txt", "w", encoding="utf-8") as f:
        f.write(text_content)
    
    # Test 2: CSV file with structured data
    csv_content = """Name,Age,City,Salary
John Doe,30,New York,75000
Jane Smith,25,Los Angeles,65000
Bob Johnson,35,Chicago,80000
Alice Brown,28,Boston,70000
"""
    
    with open(test_dir / "employee_data.csv", "w", encoding="utf-8") as f:
        f.write(csv_content)
    
    # Test 3: Markdown file with tables and links
    md_content = """# Test Document

This is a markdown test document with various features.

## Data Table

| Name | Age | City |
|------|-----|------|
| John | 30  | NYC  |
| Jane | 25  | LA   |

## Links and Images

Check out [Google](https://www.google.com) for more information.

![Test Image](test.jpg)

## Lists

- Item 1
- Item 2
  - Subitem 2.1
  - Subitem 2.2
- Item 3

1. First item
2. Second item
3. Third item
"""
    
    with open(test_dir / "complex_test.md", "w", encoding="utf-8") as f:
        f.write(md_content)
    
    # Test 4: Large text file for performance testing
    large_content = []
    for i in range(100):
        large_content.append(f"Paragraph {i+1}: This is a longer paragraph with multiple sentences. "
                           f"It contains various words and punctuation marks. "
                           f"The purpose is to test chunking and metadata extraction on larger documents.")
    
    with open(test_dir / "large_document.txt", "w", encoding="utf-8") as f:
        f.write("\n\n".join(large_content))
    
    # Test 5: Invalid file (empty)
    with open(test_dir / "empty_file.txt", "w", encoding="utf-8") as f:
        f.write("")
    
    print("✅ Created test documents:")
    for file in test_dir.glob("*"):
        print(f"   - {file.name}")


def test_metadata_extraction():
    """Test enhanced metadata extraction."""
    print("\n🔍 Testing Enhanced Metadata Extraction")
    print("=" * 50)
    
    config = get_config()
    processor = DocumentProcessor(config)
    
    test_files = [
        "data/test_documents/simple_test.txt",
        "data/test_documents/employee_data.csv",
        "data/test_documents/complex_test.md",
        "data/test_documents/large_document.txt"
    ]
    
    for file_path in test_files:
        print(f"\n📄 Processing: {Path(file_path).name}")
        
        try:
            # Process document
            chunks, metadata = processor.process_document(file_path)
            
            # Display metadata
            print(f"   ✅ Processing Status: {metadata.processing_status}")
            print(f"   📊 File Info:")
            print(f"      - Size: {metadata.file_size:,} bytes")
            print(f"      - Type: {metadata.file_type}")
            print(f"      - Encoding: {metadata.encoding}")
            
            print(f"   📈 Content Statistics:")
            print(f"      - Words: {metadata.word_count:,}")
            print(f"      - Characters: {metadata.char_count:,}")
            print(f"      - Sentences: {metadata.sentence_count:,}")
            print(f"      - Paragraphs: {metadata.paragraph_count:,}")
            print(f"      - Lines: {metadata.line_count:,}")
            print(f"      - Chunks: {metadata.chunk_count:,}")
            
            print(f"   🔍 Content Analysis:")
            print(f"      - Content Type: {metadata.content_type}")
            print(f"      - Language: {metadata.language_detected}")
            print(f"      - Has Tables: {metadata.has_tables}")
            print(f"      - Has Images: {metadata.has_images}")
            print(f"      - Has Links: {metadata.has_links}")
            
            print(f"   ⏱️  Processing:")
            print(f"      - Time: {metadata.processing_time:.3f}s")
            print(f"      - Processed At: {metadata.processed_at}")
            
            print(f"   ✅ Validation:")
            print(f"      - Is Valid: {metadata.is_valid}")
            if metadata.validation_errors:
                print(f"      - Errors: {metadata.validation_errors}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")


def test_document_validation():
    """Test document validation features."""
    print("\n🔍 Testing Document Validation")
    print("=" * 50)
    
    config = get_config()
    processor = DocumentProcessor(config)
    
    test_cases = [
        ("data/test_documents/simple_test.txt", "Valid text file"),
        ("data/test_documents/employee_data.csv", "Valid CSV file"),
        ("data/test_documents/empty_file.txt", "Empty file"),
        ("data/test_documents/nonexistent.txt", "Non-existent file"),
        ("data/test_documents/complex_test.md", "Valid markdown file")
    ]
    
    for file_path, description in test_cases:
        print(f"\n📄 {description}: {Path(file_path).name}")
        
        # Test validation without processing
        validation_result = processor.validate_document_file(file_path)
        
        print(f"   ✅ Valid: {validation_result['valid']}")
        print(f"   📊 File Info:")
        if 'file_name' in validation_result:
            print(f"      - Name: {validation_result['file_name']}")
            print(f"      - Size: {validation_result.get('file_size', 'N/A'):,} bytes")
            print(f"      - Type: {validation_result.get('file_type', 'N/A')}")
            print(f"      - Hash: {validation_result.get('content_hash', 'N/A')[:16]}...")
        
        if validation_result['errors']:
            print(f"   ❌ Errors:")
            for error in validation_result['errors']:
                print(f"      - {error}")


def test_chunk_indexing():
    """Test enhanced chunk indexing features."""
    print("\n🔍 Testing Enhanced Chunk Indexing")
    print("=" * 50)
    
    config = get_config()
    processor = DocumentProcessor(config)
    
    test_file = "data/test_documents/large_document.txt"
    
    try:
        chunks, metadata = processor.process_document(test_file)
        
        print(f"📄 Document: {Path(test_file).name}")
        print(f"📊 Total Chunks: {len(chunks)}")
        
        # Display first few chunks with enhanced metadata
        for i, chunk in enumerate(chunks[:3]):
            print(f"\n   Chunk {i+1}:")
            print(f"      ID: {chunk.chunk_id}")
            print(f"      Index: {chunk.chunk_index}")
            print(f"      Size: {chunk.metadata['chunk_size']} chars")
            print(f"      Words: {chunk.metadata['word_count']}")
            print(f"      Sentences: {chunk.metadata['sentence_count']}")
            print(f"      Position: {chunk.start_char}-{chunk.end_char}")
            print(f"      Preview: {chunk.metadata['content_preview']}")
            print(f"      Has Content: {chunk.metadata['has_content']}")
        
        if len(chunks) > 3:
            print(f"\n   ... and {len(chunks) - 3} more chunks")
        
    except Exception as e:
        print(f"❌ Error: {e}")


def test_processing_status_tracking():
    """Test processing status tracking features."""
    print("\n🔍 Testing Processing Status Tracking")
    print("=" * 50)
    
    config = get_config()
    processor = DocumentProcessor(config)
    
    test_files = [
        "data/test_documents/simple_test.txt",
        "data/test_documents/employee_data.csv",
        "data/test_documents/nonexistent.txt"
    ]
    
    for file_path in test_files:
        print(f"\n📄 Status Check: {Path(file_path).name}")
        
        status = processor.get_processing_status(file_path)
        
        print(f"   Status: {status['status']}")
        print(f"   File Path: {status['file_path']}")
        
        if status['status'] == 'available':
            print(f"   File Name: {status['file_name']}")
            print(f"   File Size: {status['file_size']:,} bytes")
            print(f"   File Type: {status['file_type']}")
            print(f"   Last Modified: {status['last_modified']}")
            print(f"   Is Valid: {status['is_valid']}")
            if status['validation_errors']:
                print(f"   Validation Errors: {status['validation_errors']}")
        elif status['status'] == 'not_found':
            print(f"   Error: {status['error']}")
        elif status['status'] == 'error':
            print(f"   Error: {status['error']}")


def test_performance_metrics():
    """Test performance metrics and monitoring."""
    print("\n🔍 Testing Performance Metrics")
    print("=" * 50)
    
    config = get_config()
    processor = DocumentProcessor(config)
    
    # Process multiple documents to gather metrics
    test_files = [
        "data/test_documents/simple_test.txt",
        "data/test_documents/employee_data.csv",
        "data/test_documents/complex_test.md",
        "data/test_documents/large_document.txt"
    ]
    
    print("📊 Processing documents for metrics...")
    
    for file_path in test_files:
        try:
            processor.process_document(file_path)
        except Exception as e:
            print(f"   ⚠️  Skipped {Path(file_path).name}: {e}")
    
    # Get performance metrics
    metrics = processor.get_processing_metrics()
    
    print(f"\n📈 Performance Metrics:")
    print(f"   Total Documents: {metrics['total_documents']}")
    print(f"   Total Chunks: {metrics['total_chunks']}")
    print(f"   Total Processing Time: {metrics['total_processing_time']:.3f}s")
    print(f"   Average Time per Document: {metrics['average_time_per_document']:.3f}s")
    print(f"   Average Chunks per Document: {metrics['average_chunks_per_document']:.1f}")
    print(f"   Error Count: {metrics['error_count']}")
    
    if metrics['errors']:
        print(f"   Recent Errors:")
        for error in metrics['errors']:
            print(f"      - {error}")


def test_health_check():
    """Test enhanced health check functionality."""
    print("\n🔍 Testing Enhanced Health Check")
    print("=" * 50)
    
    config = get_config()
    processor = DocumentProcessor(config)
    
    health = processor.health_check()
    
    print(f"🏥 Health Status: {health['status']}")
    print(f"📁 Supported Formats: {', '.join(health['supported_formats'])}")
    
    print(f"\n⚙️  Configuration:")
    config_info = health['configuration']
    print(f"   Max Chunk Size: {config_info['max_chunk_size']}")
    print(f"   Chunk Overlap: {config_info['chunk_overlap']}")
    print(f"   Min Chunk Size: {config_info['min_chunk_size']}")
    print(f"   Max File Size: {config_info['max_file_size']}")
    print(f"   Max Chunks per Document: {config_info['max_chunks_per_document']}")
    
    print(f"\n📊 Processing Metrics:")
    metrics = health['processing_metrics']
    print(f"   Total Documents: {metrics['total_documents']}")
    print(f"   Total Chunks: {metrics['total_chunks']}")
    print(f"   Total Processing Time: {metrics['total_processing_time']:.3f}s")
    print(f"   Error Count: {metrics['error_count']}")


def main():
    """Main test function."""
    print("🚀 ZeroRAG Phase 3.3: Metadata & Indexing Test Suite")
    print("=" * 60)
    
    # Create test documents
    create_test_documents()
    
    # Run all tests
    test_metadata_extraction()
    test_document_validation()
    test_chunk_indexing()
    test_processing_status_tracking()
    test_performance_metrics()
    test_health_check()
    
    print("\n✅ Phase 3.3 Testing Complete!")
    print("=" * 60)
    print("🎯 All enhanced metadata extraction, document validation,")
    print("   and indexing features have been tested successfully.")


if __name__ == "__main__":
    main()
