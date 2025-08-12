#!/usr/bin/env python3
"""
File Format Handlers Demo

This script demonstrates the enhanced file format handlers for CSV and Markdown processing.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from services.document_processor import get_document_processor
from config import get_config


def demo_csv_processing():
    """Demonstrate enhanced CSV processing."""
    print("=" * 80)
    print("CSV Processing Demo")
    print("=" * 80)
    
    config = get_config()
    processor = get_document_processor(config)
    
    csv_file = Path("data/test_documents/test_data.csv")
    
    if not csv_file.exists():
        print("❌ Test CSV file not found")
        return
    
    print(f"📄 Processing: {csv_file.name}")
    print(f"📊 Original file size: {csv_file.stat().st_size} bytes")
    
    # Show original content
    print("\n📋 Original CSV Content:")
    print("-" * 40)
    with open(csv_file, 'r') as f:
        print(f.read())
    
    # Process and show result
    print("\n🔄 Processed Output:")
    print("-" * 40)
    chunks, metadata = processor.process_document(csv_file)
    
    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i+1} ---")
        print(chunk.text)
        print(f"Word count: {chunk.metadata['word_count']}")
        print(f"Character count: {chunk.metadata['char_count']}")


def demo_markdown_processing():
    """Demonstrate enhanced Markdown processing."""
    print("\n" + "=" * 80)
    print("Markdown Processing Demo")
    print("=" * 80)
    
    config = get_config()
    processor = get_document_processor(config)
    
    md_file = Path("data/test_documents/test_document.md")
    
    if not md_file.exists():
        print("❌ Test Markdown file not found")
        return
    
    print(f"📄 Processing: {md_file.name}")
    print(f"📊 Original file size: {md_file.stat().st_size} bytes")
    
    # Show original content
    print("\n📋 Original Markdown Content:")
    print("-" * 40)
    with open(md_file, 'r') as f:
        print(f.read())
    
    # Process and show result
    print("\n🔄 Processed Output:")
    print("-" * 40)
    chunks, metadata = processor.process_document(md_file)
    
    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i+1} ---")
        print(chunk.text)
        print(f"Word count: {chunk.metadata['word_count']}")
        print(f"Character count: {chunk.metadata['char_count']}")


def demo_text_processing():
    """Demonstrate basic text processing."""
    print("\n" + "=" * 80)
    print("Text Processing Demo")
    print("=" * 80)
    
    config = get_config()
    processor = get_document_processor(config)
    
    txt_file = Path("data/test_documents/test_document.txt")
    
    if not txt_file.exists():
        print("❌ Test text file not found")
        return
    
    print(f"📄 Processing: {txt_file.name}")
    print(f"📊 Original file size: {txt_file.stat().st_size} bytes")
    
    # Show original content
    print("\n📋 Original Text Content:")
    print("-" * 40)
    with open(txt_file, 'r') as f:
        print(f.read())
    
    # Process and show result
    print("\n🔄 Processed Output:")
    print("-" * 40)
    chunks, metadata = processor.process_document(txt_file)
    
    for i, chunk in enumerate(chunks):
        print(f"\n--- Chunk {i+1} ---")
        print(chunk.text)
        print(f"Word count: {chunk.metadata['word_count']}")
        print(f"Character count: {chunk.metadata['char_count']}")


def demo_health_check():
    """Demonstrate health check functionality."""
    print("\n" + "=" * 80)
    print("Health Check Demo")
    print("=" * 80)
    
    config = get_config()
    processor = get_document_processor(config)
    
    health_status = processor.health_check()
    
    print("📊 Document Processor Health Status:")
    print(f"   Status: {health_status['status']}")
    print(f"   Supported Formats: {', '.join(health_status['supported_formats'])}")
    
    print("\n⚙️  Configuration:")
    for key, value in health_status['configuration'].items():
        print(f"   {key}: {value}")
    
    print("\n📈 Processing Metrics:")
    metrics = health_status['processing_metrics']
    for key, value in metrics.items():
        if key != 'errors':  # Skip error details for demo
            print(f"   {key}: {value}")


def main():
    """Run all demos."""
    print("🎯 File Format Handlers Demonstration")
    print("=" * 80)
    
    # Run demos
    demo_csv_processing()
    demo_markdown_processing()
    demo_text_processing()
    demo_health_check()
    
    print("\n" + "=" * 80)
    print("✅ Demo completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
