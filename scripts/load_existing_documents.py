#!/usr/bin/env python3
"""
Load Existing Documents Script

This script loads documents from the data/test_documents and data/uploads directories
into the ZeroRAG vector store so they appear in the UI.

Usage:
    python scripts/load_existing_documents.py
"""

import os
import sys
import time
import requests
from pathlib import Path
from typing import List, Dict, Any
import logging

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
API_BASE_URL = "http://localhost:8000"
SUPPORTED_FORMATS = [".txt", ".md", ".csv", ".docx", ".pdf"]

def check_api_health() -> bool:
    """Check if the API is available."""
    try:
        response = requests.get(f"{API_BASE_URL}/health/ping", timeout=5)
        return response.status_code == 200
    except requests.RequestException as e:
        logger.error(f"API health check failed: {e}")
        return False

def upload_document(file_path: Path) -> Dict[str, Any]:
    """Upload a document to the API."""
    try:
        with open(file_path, 'rb') as f:
            files = {"file": (file_path.name, f, "application/octet-stream")}
            response = requests.post(
                f"{API_BASE_URL}/documents/upload",
                files=files,
                timeout=60
            )
            return response.json()
    except requests.RequestException as e:
        logger.error(f"Upload error for {file_path}: {e}")
        return {"error": str(e)}

def validate_file(file_path: Path) -> Dict[str, Any]:
    """Validate a file before upload."""
    try:
        data = {
            "filename": file_path.name,
            "file_size": file_path.stat().st_size,
            "content_type": "application/octet-stream"
        }
        response = requests.post(
            f"{API_BASE_URL}/documents/validate",
            json=data,
            timeout=30
        )
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Validation error for {file_path}: {e}")
        return {"error": str(e)}

def get_upload_progress(document_id: str) -> Dict[str, Any]:
    """Get upload progress for a document."""
    try:
        response = requests.get(
            f"{API_BASE_URL}/documents/upload/{document_id}/progress",
            timeout=5
        )
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Progress check error: {e}")
        return {"error": str(e)}

def find_documents(directory: Path) -> List[Path]:
    """Find all supported documents in a directory."""
    documents = []
    if directory.exists():
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_FORMATS:
                documents.append(file_path)
    return documents

def load_documents_from_directory(directory: Path, directory_name: str) -> None:
    """Load all documents from a specific directory."""
    logger.info(f"Scanning {directory_name} directory: {directory}")
    
    documents = find_documents(directory)
    if not documents:
        logger.info(f"No supported documents found in {directory_name}")
        return
    
    logger.info(f"Found {len(documents)} documents in {directory_name}")
    
    for i, file_path in enumerate(documents, 1):
        logger.info(f"Processing {i}/{len(documents)}: {file_path.name}")
        
        # Validate file
        validation_result = validate_file(file_path)
        if "error" in validation_result:
            logger.error(f"Validation failed for {file_path.name}: {validation_result['error']}")
            continue
        
        if not validation_result.get("is_valid", False):
            logger.warning(f"File {file_path.name} is not valid: {validation_result}")
            continue
        
        # Upload file
        logger.info(f"Uploading {file_path.name}...")
        upload_result = upload_document(file_path)
        
        if "error" in upload_result:
            logger.error(f"Upload failed for {file_path.name}: {upload_result['error']}")
            continue
        
        document_id = upload_result.get("document_id")
        if document_id:
            logger.info(f"Successfully uploaded {file_path.name} (ID: {document_id})")
            
            # Wait for processing to complete
            logger.info(f"Waiting for processing to complete...")
            for attempt in range(30):  # Wait up to 30 seconds
                time.sleep(1)
                progress = get_upload_progress(document_id)
                if progress.get("status") == "completed":
                    logger.info(f"✅ Processing completed for {file_path.name}")
                    break
                elif progress.get("status") == "failed":
                    logger.error(f"❌ Processing failed for {file_path.name}")
                    break
                else:
                    logger.info(f"⏳ Processing... {progress.get('progress', 0)}%")
        else:
            logger.error(f"Upload succeeded but no document ID returned for {file_path.name}")

def main():
    """Main function to load existing documents."""
    logger.info("🚀 Starting document loading process...")
    
    # Check if API is available
    logger.info("Checking API availability...")
    if not check_api_health():
        logger.error("❌ API is not available. Please start the API server first.")
        logger.info("💡 Start the API server with: python start_app.py")
        return
    
    logger.info("✅ API is available")
    
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    
    # Load documents from test_documents directory
    test_docs_dir = project_root / "data" / "test_documents"
    load_documents_from_directory(test_docs_dir, "test_documents")
    
    # Load documents from uploads directory
    uploads_dir = project_root / "data" / "uploads"
    load_documents_from_directory(uploads_dir, "uploads")
    
    # Check final document count
    try:
        response = requests.get(f"{API_BASE_URL}/documents", timeout=10)
        if response.status_code == 200:
            documents_data = response.json()
            total_documents = documents_data.get("total", 0)
            logger.info(f"🎉 Document loading complete! Total documents in system: {total_documents}")
        else:
            logger.warning("Could not retrieve final document count")
    except requests.RequestException as e:
        logger.warning(f"Could not retrieve final document count: {e}")
    
    logger.info("✅ Document loading process completed!")

if __name__ == "__main__":
    main()
