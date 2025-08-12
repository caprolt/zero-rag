#!/usr/bin/env python3
"""
Simple Test API Server for ZeroRAG

This is a minimal API server to test the Streamlit UI functionality.
It provides basic endpoints that the UI expects.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List
import time
import uuid

app = FastAPI(
    title="ZeroRAG Test API",
    description="Simple test API for ZeroRAG Streamlit UI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501", "http://127.0.0.1:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for testing
documents = {}
upload_progress = {}

class QueryRequest(BaseModel):
    query: str
    stream: bool = False

class QueryResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    processing_time: float

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "services": {
            "api": {
                "status": "healthy",
                "last_check": time.time(),
                "error_count": 0
            }
        },
        "uptime": 0,
        "version": "1.0.0"
    }

@app.get("/documents")
async def list_documents():
    """List all documents."""
    return {
        "documents": [
            {
                "id": doc_id,
                "name": doc_info["name"],
                "size": doc_info["size"],
                "uploaded_at": doc_info["uploaded_at"]
            }
            for doc_id, doc_info in documents.items()
        ]
    }

@app.post("/documents/validate")
async def validate_document(file):
    """Validate a document before upload."""
    return {
        "valid": True,
        "filename": file.filename,
        "size": len(file.file.read()),
        "message": "File is valid"
    }

@app.post("/documents/upload")
async def upload_document(file):
    """Upload a document."""
    doc_id = str(uuid.uuid4())
    file_content = file.file.read()
    
    documents[doc_id] = {
        "name": file.filename,
        "size": len(file_content),
        "uploaded_at": time.time(),
        "content": file_content.decode('utf-8', errors='ignore')
    }
    
    # Initialize progress
    upload_progress[doc_id] = {
        "status": "processing",
        "progress": 0
    }
    
    # Simulate processing
    for i in range(10):
        upload_progress[doc_id]["progress"] = (i + 1) * 10
        time.sleep(0.1)
    
    upload_progress[doc_id]["status"] = "completed"
    upload_progress[doc_id]["progress"] = 100
    
    return {
        "document_id": doc_id,
        "filename": file.filename,
        "size": len(file_content),
        "message": "Document uploaded successfully"
    }

@app.get("/documents/upload/{document_id}/progress")
async def get_upload_progress(document_id: str):
    """Get upload progress for a document."""
    if document_id not in upload_progress:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return upload_progress[document_id]

@app.post("/query")
async def query_documents(request: QueryRequest):
    """Process a query."""
    start_time = time.time()
    
    # Simple response based on available documents
    if documents:
        answer = f"I found {len(documents)} document(s) in the system. "
        answer += "This is a test response from the ZeroRAG API server. "
        answer += f"Your query was: '{request.query}'"
        
        sources = [
            {
                "title": doc_info["name"],
                "content": doc_info["content"][:200] + "...",
                "score": 0.95
            }
            for doc_info in documents.values()
        ]
    else:
        answer = "No documents found in the system. Please upload some documents first."
        sources = []
    
    processing_time = time.time() - start_time
    
    return QueryResponse(
        answer=answer,
        sources=sources,
        processing_time=processing_time
    )

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting ZeroRAG Test API Server...")
    print("📱 API will be available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print("⏹️  Press Ctrl+C to stop")
    print("-" * 50)
    
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
