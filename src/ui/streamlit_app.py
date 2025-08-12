"""
ZeroRAG Streamlit UI

This module provides the main Streamlit frontend for the ZeroRAG system.
It includes document upload, chat interface, and source display functionality.

Phase 7.1 Implementation:
- Basic Streamlit application structure
- Page configuration and layout
- Document upload interface with validation
- Upload progress and status display
"""

import streamlit as st
import requests
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="ZeroRAG - AI-Powered Document Q&A",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sidebar-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .upload-section {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .status-success {
        color: #28a745;
        font-weight: bold;
    }
    .status-error {
        color: #dc3545;
        font-weight: bold;
    }
    .status-warning {
        color: #ffc107;
        font-weight: bold;
    }
    .chat-message {
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 0.5rem;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .source-item {
        background-color: #fff3e0;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border-radius: 0.25rem;
        border-left: 3px solid #ff9800;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = "http://localhost:8000"
SUPPORTED_FORMATS = [".txt", ".md", ".pdf", ".csv", ".docx"]

def check_api_health() -> bool:
    """Check if the API is available."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def upload_document(file) -> Dict[str, Any]:
    """Upload a document to the API."""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(
            f"{API_BASE_URL}/documents/upload",
            files=files,
            timeout=30
        )
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Upload error: {e}")
        return {"error": str(e)}

def validate_file(file) -> Dict[str, Any]:
    """Validate a file before upload."""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(
            f"{API_BASE_URL}/documents/validate",
            files=files,
            timeout=10
        )
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Validation error: {e}")
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

def query_rag(question: str, stream: bool = False) -> Dict[str, Any]:
    """Send a query to the RAG system."""
    try:
        data = {"query": question, "stream": stream}
        response = requests.post(
            f"{API_BASE_URL}/query",
            json=data,
            timeout=60
        )
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Query error: {e}")
        return {"error": str(e)}

def main():
    """Main Streamlit application."""
    
    # Initialize session state
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "api_available" not in st.session_state:
        st.session_state.api_available = check_api_health()

    # Header
    st.markdown('<h1 class="main-header">🤖 ZeroRAG</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">AI-Powered Document Q&A System</p>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown('<h2 class="sidebar-header">📁 Document Management</h2>', unsafe_allow_html=True)
        
        # API Status
        api_status = "🟢 Connected" if st.session_state.api_available else "🔴 Disconnected"
        st.markdown(f"**API Status:** {api_status}")
        
        if not st.session_state.api_available:
            st.error("Cannot connect to ZeroRAG API. Please ensure the API server is running.")
            if st.button("🔄 Retry Connection"):
                st.session_state.api_available = check_api_health()
                st.rerun()
            return

        # Document Upload Section
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        st.markdown("**📤 Upload Documents**")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=SUPPORTED_FORMATS,
            help="Supported formats: TXT, MD, PDF, CSV, DOCX"
        )

        if uploaded_file is not None:
            # File validation
            with st.spinner("Validating file..."):
                validation_result = validate_file(uploaded_file)
            
            if "error" in validation_result:
                st.error(f"Validation failed: {validation_result['error']}")
            elif validation_result.get("valid", False):
                st.success("✅ File is valid!")
                
                # Upload button
                if st.button("🚀 Upload Document"):
                    with st.spinner("Uploading document..."):
                        upload_result = upload_document(uploaded_file)
                    
                    if "error" in upload_result:
                        st.error(f"Upload failed: {upload_result['error']}")
                    else:
                        st.success("✅ Document uploaded successfully!")
                        document_id = upload_result.get("document_id")
                        if document_id:
                            st.session_state.uploaded_files.append({
                                "name": uploaded_file.name,
                                "id": document_id,
                                "size": uploaded_file.size
                            })
                        
                        # Show upload progress
                        if document_id:
                            progress_placeholder = st.empty()
                            for i in range(10):  # Check progress for 10 seconds
                                time.sleep(1)
                                progress = get_upload_progress(document_id)
                                if progress.get("status") == "completed":
                                    progress_placeholder.success("✅ Processing completed!")
                                    break
                                elif progress.get("status") == "failed":
                                    progress_placeholder.error("❌ Processing failed!")
                                    break
                                else:
                                    progress_placeholder.info(f"⏳ Processing... {progress.get('progress', 0)}%")
            else:
                st.error("❌ File validation failed")
        
        st.markdown('</div>', unsafe_allow_html=True)

        # Uploaded Files List
        if st.session_state.uploaded_files:
            st.markdown("**📋 Uploaded Files**")
            for file_info in st.session_state.uploaded_files:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"📄 {file_info['name']}")
                with col2:
                    if st.button("🗑️", key=f"delete_{file_info['id']}"):
                        # TODO: Implement delete functionality
                        st.session_state.uploaded_files.remove(file_info)
                        st.rerun()

        # Clear Chat History
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()

    # Main Content Area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Chat Interface
        st.markdown("**💬 Chat with Your Documents**")
        
        # Chat history display
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message user-message">👤 **You:** {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message assistant-message">🤖 **Assistant:** {message["content"]}</div>', unsafe_allow_html=True)
                
                # Display sources if available
                if "sources" in message and message["sources"]:
                    st.markdown("**📚 Sources:**")
                    for source in message["sources"]:
                        st.markdown(f'<div class="source-item">📄 {source.get("title", "Unknown")} (Relevance: {source.get("score", 0):.2f})</div>', unsafe_allow_html=True)
        
        # Query input
        query = st.text_area(
            "Ask a question about your documents:",
            height=100,
            placeholder="Enter your question here..."
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🚀 Send Query", type="primary"):
                if query.strip():
                    # Add user message to history
                    st.session_state.chat_history.append({
                        "role": "user",
                        "content": query
                    })
                    
                    # Get response
                    with st.spinner("🤖 Thinking..."):
                        response = query_rag(query)
                    
                    if "error" in response:
                        st.error(f"Query failed: {response['error']}")
                    else:
                        # Add assistant response to history
                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": response.get("answer", "No answer generated"),
                            "sources": response.get("sources", [])
                        })
                    
                    st.rerun()
        
        with col2:
            if st.button("🔄 New Chat"):
                st.session_state.chat_history = []
                st.rerun()

    with col2:
        # System Information
        st.markdown("**ℹ️ System Info**")
        
        # Health check
        if st.session_state.api_available:
            try:
                health_response = requests.get(f"{API_BASE_URL}/health", timeout=5)
                if health_response.status_code == 200:
                    health_data = health_response.json()
                    st.success(f"✅ System: {health_data.get('status', 'Unknown')}")
                    
                    # Service status
                    services = health_data.get("services", {})
                    for service, info in services.items():
                        status = info.get("status", "unknown")
                        status_icon = "✅" if status == "healthy" else "⚠️" if status == "degraded" else "❌"
                        st.write(f"{status_icon} {service}: {status}")
                else:
                    st.error("❌ Health check failed")
            except requests.RequestException:
                st.error("❌ Cannot reach API")
        
        # Document count
        try:
            documents_response = requests.get(f"{API_BASE_URL}/documents", timeout=5)
            if documents_response.status_code == 200:
                documents_data = documents_response.json()
                doc_count = len(documents_data.get("documents", []))
                st.info(f"📚 Documents: {doc_count}")
        except requests.RequestException:
            st.write("📚 Documents: Unknown")

if __name__ == "__main__":
    main()
