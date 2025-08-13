#!/usr/bin/env python3
"""
Check Vector Store Contents

This script checks what documents are actually stored in the vector store
to understand the grouping and deduplication behavior.

Usage:
    python scripts/check_vector_store.py
"""

import sys
import requests
from pathlib import Path
import json

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Configuration
API_BASE_URL = "http://localhost:8000"

def check_documents():
    """Check what documents are in the vector store."""
    try:
        # Get documents from API
        response = requests.get(f"{API_BASE_URL}/documents", timeout=10)
        if response.status_code == 200:
            documents_data = response.json()
            documents = documents_data.get("documents", [])
            total = documents_data.get("total", 0)
            
            print(f"📊 Vector Store Contents:")
            print(f"Total documents: {total}")
            print()
            
            if documents:
                print("📚 Documents in vector store:")
                for i, doc in enumerate(documents, 1):
                    print(f"{i}. {doc.get('filename', 'Unknown')}")
                    print(f"   ID: {doc.get('document_id', 'Unknown')}")
                    print(f"   Chunks: {doc.get('chunks_count', 0)}")
                    if doc.get('metadata'):
                        print(f"   Metadata: {json.dumps(doc['metadata'], indent=2)}")
                    print()
            else:
                print("❌ No documents found in vector store")
        else:
            print(f"❌ Failed to get documents: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ Error connecting to API: {e}")

def check_health():
    """Check API health."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print(f"🏥 API Health: {health_data.get('status', 'Unknown')}")
            print(f"⏱️ Uptime: {health_data.get('uptime', 0):.1f} seconds")
            
            services = health_data.get("services", {})
            print("🔧 Services:")
            for service, info in services.items():
                status = info.get("status", "unknown")
                status_icon = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"
                print(f"   {status_icon} {service}: {status}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            
    except requests.RequestException as e:
        print(f"❌ Error checking health: {e}")

def main():
    """Main function."""
    print("🔍 Checking ZeroRAG Vector Store Contents")
    print("=" * 50)
    
    # Check API health first
    check_health()
    print()
    
    # Check documents
    check_documents()

if __name__ == "__main__":
    main()
