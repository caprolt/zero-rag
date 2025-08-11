#!/usr/bin/env python3
"""
ZeroRAG Document Processor Test Script

This script tests the document processor functionality including:
- Multi-format document processing (TXT, CSV, MD)
- Text chunking and normalization
- Metadata extraction
- Performance metrics

Usage:
    python scripts/test_document_processor.py
"""

import sys
import time
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.document_processor import DocumentProcessor, get_document_processor
from config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_documents():
    """Create test documents for processing."""
    test_dir = Path("data/test_documents")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Create test text file
    text_content = """
    This is a test document for the ZeroRAG system. It contains multiple sentences to test the chunking functionality.
    
    The document processor should be able to handle various text formats and create appropriate chunks for embedding.
    Each chunk should maintain semantic coherence while staying within the specified size limits.
    
    This paragraph contains additional information about the system's capabilities. The processor supports multiple file formats including TXT, CSV, and Markdown files.
    
    The chunking algorithm uses intelligent sentence boundary detection to ensure that chunks don't break sentences inappropriately. This helps maintain the semantic meaning of the content.
    
    Finally, this document includes metadata extraction capabilities that track file information, processing statistics, and performance metrics.
    """
    
    with open(test_dir / "test_document.txt", "w", encoding="utf-8") as f:
        f.write(text_content)
    
    # Create test CSV file
    csv_content = """Name,Age,City,Occupation
John Doe,30,New York,Engineer
Jane Smith,25,Los Angeles,Designer
Bob Johnson,35,Chicago,Manager
Alice Brown,28,Boston,Developer
Charlie Wilson,32,Seattle,Analyst"""
    
    with open(test_dir / "test_data.csv", "w", encoding="utf-8", newline="") as f:
        f.write(csv_content)
    
    # Create test markdown file
    md_content = """# Test Markdown Document

This is a **test markdown document** for the ZeroRAG system.

## Features

The document processor supports:
- *Text formatting* removal
- [Link text](http://example.com) extraction
- Code block handling
- Header processing

### Code Example

```python
def process_document(file_path):
    return "processed content"
```

## Summary

This document tests the markdown processing capabilities of the system.
"""
    
    with open(test_dir / "test_document.md", "w", encoding="utf-8") as f:
        f.write(md_content)
    
    print(f"✅ Created test documents in {test_dir}")
    return test_dir


def test_document_processor_initialization():
    """Test document processor initialization."""
    print("\n" + "="*60)
    print("TESTING DOCUMENT PROCESSOR INITIALIZATION")
    print("="*60)
    
    try:
        # Initialize processor
        start_time = time.time()
        processor = DocumentProcessor()
        init_time = time.time() - start_time
        
        print(f"✅ Document processor initialized successfully in {init_time:.2f}s")
        
        # Check configuration
        print(f"   Max chunk size: {processor.max_chunk_size}")
        print(f"   Chunk overlap: {processor.chunk_overlap}")
        print(f"   Min chunk size: {processor.min_chunk_size}")
        print(f"   Supported formats: {list(processor.supported_extensions.keys())}")
        
        return processor
        
    except Exception as e:
        print(f"❌ Document processor initialization failed: {e}")
        return None


def test_text_file_processing(processor, test_dir):
    """Test text file processing."""
    print("\n" + "="*60)
    print("TESTING TEXT FILE PROCESSING")
    print("="*60)
    
    try:
        file_path = test_dir / "test_document.txt"
        
        # Process document
        start_time = time.time()
        chunks, metadata = processor.process_document(file_path)
        processing_time = time.time() - start_time
        
        print(f"✅ Text file processed successfully in {processing_time:.2f}s")
        print(f"   File: {metadata.file_name}")
        print(f"   Size: {metadata.file_size} bytes")
        print(f"   Word count: {metadata.word_count}")
        print(f"   Character count: {metadata.char_count}")
        print(f"   Chunks generated: {metadata.chunk_count}")
        print(f"   Processing time: {metadata.processing_time:.2f}s")
        
        # Show chunk details
        print(f"\n   CHUNK DETAILS:")
        for i, chunk in enumerate(chunks):
            print(f"     Chunk {i+1}: {len(chunk.text)} chars, {len(chunk.text.split())} words")
            print(f"       Preview: {chunk.text[:100]}...")
        
        return chunks, metadata
        
    except Exception as e:
        print(f"❌ Text file processing failed: {e}")
        return None, None


def test_csv_file_processing(processor, test_dir):
    """Test CSV file processing."""
    print("\n" + "="*60)
    print("TESTING CSV FILE PROCESSING")
    print("="*60)
    
    try:
        file_path = test_dir / "test_data.csv"
        
        # Process document
        start_time = time.time()
        chunks, metadata = processor.process_document(file_path)
        processing_time = time.time() - start_time
        
        print(f"✅ CSV file processed successfully in {processing_time:.2f}s")
        print(f"   File: {metadata.file_name}")
        print(f"   Size: {metadata.file_size} bytes")
        print(f"   Word count: {metadata.word_count}")
        print(f"   Character count: {metadata.char_count}")
        print(f"   Chunks generated: {metadata.chunk_count}")
        
        # Show chunk details
        print(f"\n   CHUNK DETAILS:")
        for i, chunk in enumerate(chunks):
            print(f"     Chunk {i+1}: {len(chunk.text)} chars")
            print(f"       Preview: {chunk.text[:150]}...")
        
        return chunks, metadata
        
    except Exception as e:
        print(f"❌ CSV file processing failed: {e}")
        return None, None


def test_markdown_file_processing(processor, test_dir):
    """Test markdown file processing."""
    print("\n" + "="*60)
    print("TESTING MARKDOWN FILE PROCESSING")
    print("="*60)
    
    try:
        file_path = test_dir / "test_document.md"
        
        # Process document
        start_time = time.time()
        chunks, metadata = processor.process_document(file_path)
        processing_time = time.time() - start_time
        
        print(f"✅ Markdown file processed successfully in {processing_time:.2f}s")
        print(f"   File: {metadata.file_name}")
        print(f"   Size: {metadata.file_size} bytes")
        print(f"   Word count: {metadata.word_count}")
        print(f"   Character count: {metadata.char_count}")
        print(f"   Chunks generated: {metadata.chunk_count}")
        
        # Show chunk details
        print(f"\n   CHUNK DETAILS:")
        for i, chunk in enumerate(chunks):
            print(f"     Chunk {i+1}: {len(chunk.text)} chars, {len(chunk.text.split())} words")
            print(f"       Preview: {chunk.text[:100]}...")
        
        return chunks, metadata
        
    except Exception as e:
        print(f"❌ Markdown file processing failed: {e}")
        return None, None


def test_performance_metrics(processor):
    """Test performance metrics collection."""
    print("\n" + "="*60)
    print("TESTING PERFORMANCE METRICS")
    print("="*60)
    
    try:
        metrics = processor.get_processing_metrics()
        
        print(f"✅ Performance metrics collected")
        print(f"   Total documents: {metrics['total_documents']}")
        print(f"   Total chunks: {metrics['total_chunks']}")
        print(f"   Total processing time: {metrics['total_processing_time']:.2f}s")
        print(f"   Average time per document: {metrics['average_time_per_document']:.2f}s")
        print(f"   Average chunks per document: {metrics['average_chunks_per_document']:.1f}")
        print(f"   Error count: {metrics['error_count']}")
        
        if metrics['errors']:
            print(f"   Recent errors: {metrics['errors']}")
        
        return metrics
        
    except Exception as e:
        print(f"❌ Performance metrics collection failed: {e}")
        return None


def test_health_check(processor):
    """Test health check functionality."""
    print("\n" + "="*60)
    print("TESTING HEALTH CHECK")
    print("="*60)
    
    try:
        health = processor.health_check()
        
        print(f"✅ Health check completed")
        print(f"   Status: {health['status']}")
        print(f"   Supported formats: {health['supported_formats']}")
        print(f"   Configuration:")
        for key, value in health['configuration'].items():
            print(f"     {key}: {value}")
        
        return health
        
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return None


def test_error_handling(processor):
    """Test error handling for invalid files."""
    print("\n" + "="*60)
    print("TESTING ERROR HANDLING")
    print("="*60)
    
    try:
        # Test non-existent file
        print("   Testing non-existent file...")
        try:
            processor.process_document("non_existent_file.txt")
            print("   ❌ Should have raised an error")
        except ValueError as e:
            print(f"   ✅ Correctly handled non-existent file: {e}")
        
        # Test unsupported file type
        print("   Testing unsupported file type...")
        test_file = Path("data/test_documents/test.unsupported")
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("test content")
        
        try:
            processor.process_document(test_file)
            print("   ❌ Should have raised an error")
        except ValueError as e:
            print(f"   ✅ Correctly handled unsupported file type: {e}")
        
        # Clean up
        test_file.unlink()
        
        print("✅ Error handling tests completed")
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")


def main():
    """Main test function."""
    print("🚀 ZeroRAG Document Processor Test")
    print("="*60)
    
    # Create test documents
    test_dir = create_test_documents()
    
    # Test initialization
    processor = test_document_processor_initialization()
    if not processor:
        print("❌ Cannot continue without processor")
        return
    
    # Test file processing
    test_text_file_processing(processor, test_dir)
    test_csv_file_processing(processor, test_dir)
    test_markdown_file_processing(processor, test_dir)
    
    # Test performance and health
    test_performance_metrics(processor)
    test_health_check(processor)
    
    # Test error handling
    test_error_handling(processor)
    
    print("\n" + "="*60)
    print("🎉 Document Processor test completed!")
    print("="*60)


if __name__ == "__main__":
    main()
