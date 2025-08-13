#!/usr/bin/env python3
"""
Show All Chunks in Vector Store

This script shows all individual chunks in the vector store without grouping
by source file, to see what was actually uploaded.

Usage:
    python scripts/show_all_chunks.py
"""

import sys
import requests
from pathlib import Path
import json

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Configuration
API_BASE_URL = "http://localhost:8000"

def get_all_chunks():
    """Get all chunks from the vector store without grouping."""
    try:
        # Try to get raw data from Qdrant directly
        response = requests.get(f"{API_BASE_URL}/advanced/storage/stats", timeout=10)
        if response.status_code == 200:
            stats_data = response.json()
            print("📊 Storage Statistics:")
            print(json.dumps(stats_data, indent=2))
            print()
        
        # Try to get documents with a very high limit to see all
        response = requests.get(f"{API_BASE_URL}/documents?limit=1000", timeout=10)
        if response.status_code == 200:
            documents_data = response.json()
            documents = documents_data.get("documents", [])
            total = documents_data.get("total", 0)
            
            print(f"📊 Documents (grouped by source file):")
            print(f"Total document groups: {total}")
            print()
            
            if documents:
                print("📚 Document groups:")
                for i, doc in enumerate(documents, 1):
                    print(f"{i}. {doc.get('filename', 'Unknown')}")
                    print(f"   ID: {doc.get('document_id', 'Unknown')}")
                    print(f"   Chunks: {doc.get('chunks_count', 0)}")
                    print(f"   Source: {doc.get('source_file', 'Unknown')}")
                    if doc.get('metadata'):
                        print(f"   Metadata: {json.dumps(doc['metadata'], indent=2)}")
                    print()
            else:
                print("❌ No documents found in vector store")
        else:
            print(f"❌ Failed to get documents: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ Error connecting to API: {e}")

def check_qdrant_directly():
    """Try to check Qdrant directly for more detailed information."""
    try:
        # Try to get collection info from Qdrant
        response = requests.get("http://localhost:6333/collections/zero_rag_documents", timeout=5)
        if response.status_code == 200:
            collection_info = response.json()
            print("🔍 Qdrant Collection Info:")
            print(f"Collection: {collection_info.get('name', 'Unknown')}")
            print(f"Status: {collection_info.get('status', 'Unknown')}")
            print(f"Points count: {collection_info.get('points_count', 0)}")
            print(f"Vectors count: {collection_info.get('vectors_count', 0)}")
            print()
            
            # Try to get some points
            scroll_response = requests.post(
                "http://localhost:6333/collections/zero_rag_documents/points/scroll",
                json={"limit": 10, "with_payload": True},
                timeout=10
            )
            if scroll_response.status_code == 200:
                scroll_data = scroll_response.json()
                points = scroll_data.get("result", {}).get("points", [])
                print(f"🔍 Sample Points ({len(points)} found):")
                for i, point in enumerate(points, 1):
                    print(f"{i}. ID: {point.get('id', 'Unknown')}")
                    print(f"   Source: {point.get('payload', {}).get('source_file', 'Unknown')}")
                    print(f"   Text preview: {point.get('payload', {}).get('text', '')[:50]}...")
                    print()
        else:
            print(f"❌ Failed to get Qdrant collection info: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ Error connecting to Qdrant: {e}")

def main():
    """Main function."""
    print("🔍 Checking All Chunks in ZeroRAG Vector Store")
    print("=" * 60)
    
    # Check Qdrant directly
    check_qdrant_directly()
    
    # Get all chunks
    get_all_chunks()

if __name__ == "__main__":
    main()
