"""
ZeroRAG Streamlit UI

This module provides the main Streamlit frontend for the ZeroRAG system.
It includes document upload, chat interface, and source display functionality.

Phase 7.1 Implementation:
- Basic Streamlit application structure
- Page configuration and layout
- Document upload interface with validation
- Upload progress and status display
- Dynamic API status loading with real-time updates
"""

import streamlit as st
import requests
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
import threading
from datetime import datetime, timedelta

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
        font-size: 1.8rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
        text-align: center;
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
    
    /* Loading Spinner */
    .loader {
        width: 90px;
        height: 14px;
        box-shadow: 0 3px 0 #fff;
        position: relative;
        display: grid;
        clip-path: inset(-60px 0 -5px);
        margin: 20px auto;
    }
    .loader:after {
        content: "";
        position: relative;
        background: repeating-linear-gradient(90deg,#0000 0 calc(50% - 8px), #ccc 0 calc(50% + 8px), #0000 0 100%) 0 0/calc(100%/3) 100%;
        animation: l6-1 1s infinite;
    } 
    .loader:before {
        content: "";
        position: absolute;
        width: 14px;
        aspect-ratio: 1;
        left: calc(50% - 7px);
        bottom: 0;
        border-radius: 50%;
        background: lightblue;
        animation: l6-2 1s infinite;
    }
    @keyframes l6-1 {
        50%,100% {background-position: calc(100%/2) 0}
    }
    @keyframes l6-2 {
        0%,50% {transform:translateY(-80px)}
    }
    
    /* Loading container for better centering */
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        text-align: center;
    }
    
    /* API Status Styles */
    .api-status-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border: 2px solid #e0e0e0;
        transition: all 0.3s ease;
    }
    
    .api-status-container.connected {
        border-color: #28a745;
        background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
    }
    
    .api-status-container.connecting {
        border-color: #ffc107;
        background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%);
        animation: pulse 2s infinite;
    }
    
    .api-status-container.disconnected {
        border-color: #dc3545;
        background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.7; }
        100% { opacity: 1; }
    }
    
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        animation: blink 1.5s infinite;
    }
    
    .status-indicator.connected {
        background-color: #28a745;
        animation: none;
    }
    
    .status-indicator.connecting {
        background-color: #ffc107;
    }
    
    .status-indicator.disconnected {
        background-color: #dc3545;
        animation: none;
    }
    
    @keyframes blink {
        0%, 50% { opacity: 1; }
        51%, 100% { opacity: 0.3; }
    }
    
    .status-text {
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    
    .status-details {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.5rem;
    }
    
    .progress-bar {
        width: 100%;
        height: 6px;
        background-color: #e0e0e0;
        border-radius: 3px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #4CAF50, #8BC34A);
        border-radius: 3px;
        transition: width 0.3s ease;
    }
    
    /* Replace Streamlit's default loading spinner */
    .stSpinner > div {
        display: none !important;
    }
    
    /* Custom global loading spinner */
    .stSpinner::before {
        content: "";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 30px;
        aspect-ratio: 1;
        background: #554236;
        display: grid;
        animation: l4-0 1s infinite linear;
    }
    
    .stSpinner::after {
        content: "";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 30px;
        aspect-ratio: 1;
        background: #f77825;
        display: grid;
        animation: l4-1 1s infinite linear;
    }
    
    /* Alternative approach for global spinner replacement */
    .stSpinner > div:first-child {
        width: 30px !important;
        height: 30px !important;
        background: #554236 !important;
        display: grid !important;
        animation: l4-0 1s infinite linear !important;
        border: none !important;
        border-radius: 0 !important;
    }
    
    .stSpinner > div:first-child::before,
    .stSpinner > div:first-child::after {
        content: "" !important;
        grid-area: 1/1 !important;
        background: #f77825 !important;
        animation: inherit !important;
        animation-name: l4-1 !important;
    }
    
    .stSpinner > div:first-child::after {
        background: #60B99A !important;
        --s: 60deg !important;
    }
    
    @keyframes l4-0 {
        0%,20% {transform: rotate(0)}
        100%   {transform: rotate(90deg)}
    }
    
    @keyframes l4-1 {
        50% {transform: rotate(var(--s,30deg))}
        100% {transform: rotate(0)}
    }
    
    /* Hide Streamlit toolbar completely */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Alternative selectors for different Streamlit versions */
    .stToolbar {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    .stDeployButton {display: none !important;}
    [data-testid="stDeployButton"] {display: none !important;}
    
    /* Hide the hamburger menu and all toolbar elements */
    .stApp > header {display: none !important;}
    .stApp > footer {display: none !important;}
    .stApp > div[data-testid="stToolbar"] {display: none !important;}
    
    /* Hide the "Made with Streamlit" footer */
    .stApp > footer {display: none !important;}
    .stApp > div[data-testid="stDecoration"] {display: none !important;}
    
    /* Sidebar improvements */
    .css-1d391kg {
        padding-top: 1rem;
    }
    
    /* Better spacing for sidebar sections */
    .css-1d391kg > div {
        margin-bottom: 1.5rem;
    }
    
    /* Compact buttons */
    .stButton > button {
        border-radius: 0.5rem;
        font-weight: 500;
    }
    
    /* Better file uploader styling */
    .stFileUploader {
        border: 2px dashed #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        background-color: #fafafa;
    }
    
    /* Compact expander styling */
    .streamlit-expanderHeader {
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Better status container spacing */
    .api-status-container {
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Configuration
API_BASE_URL = "http://localhost:8000"
SUPPORTED_FORMATS = [".txt", ".md", ".pdf", ".csv", ".docx"]

class APIStatusManager:
    """Manages API status with dynamic updates and caching."""
    
    def __init__(self):
        self.status_cache = {}
        self.last_check = 0
        self.check_interval = 5  # Increased from 2 to 5 seconds (less aggressive)
        self.connection_attempts = 0
        self.max_attempts = 3  # Reduced from 5
        self.documents_cache = {}
        self.documents_cache_time = 0
        self.documents_cache_interval = 30  # Cache documents for 30 seconds
        
    def get_status(self) -> Dict[str, Any]:
        """Get current API status with caching and dynamic updates."""
        current_time = time.time()
        
        # Check if we need to update the status
        if current_time - self.last_check > self.check_interval:
            self._update_status()
            self.last_check = current_time
        
        return self.status_cache
    
    def _update_status(self):
        """Update the API status cache with simplified logic."""
        try:
            # Simple ping check - this should be instantaneous if API is ready
            ping_response = requests.get(f"{API_BASE_URL}/health/ping", timeout=0.5)  # Reduced timeout to 0.5 seconds
            ping_ok = ping_response.status_code == 200
            
            if ping_ok:
                # API is responding - that's all we need to know!
                # Since services are started before Streamlit, if ping works, everything is ready
                self.status_cache = {
                    "status": "connected",
                    "ping_ok": True,
                    "health_ok": True,
                    "docs_ready": True,  # Assume ready if ping works
                    "health_data": None,  # Don't fetch unless needed
                    "last_check": time.time(),
                    "error": None
                }
                self.connection_attempts = 0
            else:
                self.connection_attempts += 1
                self.status_cache = {
                    "status": "disconnected",
                    "ping_ok": False,
                    "health_ok": False,
                    "docs_ready": False,
                    "health_data": None,
                    "last_check": time.time(),
                    "error": f"Ping failed with status {ping_response.status_code}"
                }
                
        except requests.RequestException as e:
            self.connection_attempts += 1
            self.status_cache = {
                "status": "disconnected",
                "ping_ok": False,
                "health_ok": False,
                "docs_ready": False,
                "health_data": None,
                "last_check": time.time(),
                "error": str(e)
            }
    
    def get_documents(self) -> Dict[str, Any]:
        """Get documents with caching to avoid repeated API calls."""
        current_time = time.time()
        
        # Return cached documents if still valid
        if (current_time - self.documents_cache_time < self.documents_cache_interval and 
            self.documents_cache):
            return self.documents_cache
        
        # Fetch fresh documents
        try:
            documents_response = requests.get(f"{API_BASE_URL}/documents", timeout=10)  # Reduced from 15 to 5 seconds
            if documents_response.status_code == 200:
                self.documents_cache = documents_response.json()
                self.documents_cache_time = current_time
                return self.documents_cache
            else:
                return {"error": f"Documents fetch returned {documents_response.status_code}"}
        except requests.RequestException as e:
            return {"error": f"Documents fetch failed: {str(e)}"}
    
    def force_refresh(self):
        """Force a status refresh."""
        self.last_check = 0
        self.documents_cache_time = 0  # Clear documents cache too
        self._update_status()
        return self.status_cache
    
    def get_detailed_health(self) -> Dict[str, Any]:
        """Get detailed health info only when needed."""
        try:
            health_response = requests.get(f"{API_BASE_URL}/health", timeout=3)  # Reduced from 10 to 3 seconds
            if health_response.status_code == 200:
                return health_response.json()
            else:
                return {"error": f"Health check returned {health_response.status_code}"}
        except requests.RequestException as e:
            return {"error": f"Health check failed: {str(e)}"}

# Global API status manager
api_status_manager = APIStatusManager()

def check_api_health() -> bool:
    """Simple API health check using the status manager."""
    status = api_status_manager.get_status()
    return status.get("status") == "connected"

def get_detailed_health_status() -> Dict[str, Any]:
    """Get detailed health status from the API."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=15)
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Health check returned status code: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Health check failed: {str(e)}"}

def display_api_status():
    """Display dynamic API status with real-time updates."""
    status = api_status_manager.get_status()
    
    # Determine status class and icon
    status_class = status.get("status", "disconnected")
    
    # Show error details if available
    if status.get("error"):
        st.error(f"Connection Error: {status['error']}")
    
    return status_class

def upload_document(file) -> Dict[str, Any]:
    """Upload a document to the API."""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(
            f"{API_BASE_URL}/documents/upload",
            files=files,
            timeout=60  # Increased timeout from 30 to 60 seconds
        )
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Upload error: {e}")
        return {"error": str(e)}

def validate_file(file) -> Dict[str, Any]:
    """Validate a file before upload."""
    try:
        # Create JSON request with file metadata
        data = {
            "filename": file.name,
            "file_size": file.size,
            "content_type": file.type
        }
        response = requests.post(
            f"{API_BASE_URL}/documents/validate",
            json=data,
            timeout=30  # Increased timeout from 10 to 30 seconds
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

def display_loading_spinner(message: str = "Loading..."):
    """Display the custom loading spinner with a message."""
    st.markdown(f"""
    <div class="loading-container">
        <div class="loader"></div>
        <p style="margin-top: 1rem; color: #666;">{message}</p>
    </div>
    """, unsafe_allow_html=True)

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
    
    # Show immediate loading state
    if "app_loaded" not in st.session_state:
        st.session_state.app_loaded = False
        with st.spinner("🚀 Initializing ZeroRAG..."):
            # Quick API check
            api_status_manager.get_status()
            st.session_state.app_loaded = True
        st.rerun()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 ZeroRAG</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">AI-Powered Document Q&A System</p>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        # Header with better styling
        st.markdown('<h2 class="sidebar-header">🤖 ZeroRAG</h2>', unsafe_allow_html=True)
        st.markdown('<p style="font-size: 0.9rem; color: #666; margin-bottom: 2rem;">AI-Powered Document Q&A System</p>', unsafe_allow_html=True)
        
        # Simple API status display
        api_status = display_api_status()

        # Show appropriate messages based on status
        if api_status == "disconnected":
            st.error("❌ Cannot connect to API")
            st.info("💡 **Start the API server:** `python start_app.py`")
            
            if st.button("🔄 Retry Connection", use_container_width=True):
                api_status_manager.force_refresh()
                st.rerun()
            
            # Link to health page for diagnostics
            st.markdown("---")
            st.markdown("**🔍 Need help?**")
            st.markdown("Visit the [Health Status Page](http://localhost:8501/health_page) for detailed diagnostics.")
            return
        
        elif api_status == "connected":
            st.success("✅ API Connected")
            
            # Simple status with link to health page
            st.info("💡 For detailed system status, visit the Health Status page")
            if st.button("🏥 Open Health Status", use_container_width=True):
                st.markdown("🔗 [Open Health Status Page](http://localhost:8501/health_page)")

        # Divider
        st.markdown("---")
        
        # Document Management Section
        st.markdown("### 📁 Document Management")
        
        # Document Upload Section with better styling
        st.markdown("**📤 Upload Documents**")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=SUPPORTED_FORMATS,
            help="Supported formats: TXT, MD, PDF, CSV, DOCX",
            label_visibility="collapsed"
        )

        if uploaded_file is not None:
            # File validation
            validation_placeholder = st.empty()
            with validation_placeholder.container():
                display_loading_spinner("Validating file...")
            
            validation_result = validate_file(uploaded_file)
            validation_placeholder.empty()

            if "error" in validation_result:
                error_msg = validation_result['error']
                if "timeout" in error_msg.lower():
                    st.error(f"❌ Validation timeout")
                    st.info("💡 API server might be overloaded")
                else:
                    st.error(f"❌ Validation failed: {error_msg}")
            elif validation_result.get("is_valid", False):
                st.success("✅ File is valid!")
                
                # Upload button
                if st.button("🚀 Upload Document", use_container_width=True):
                    upload_placeholder = st.empty()
                    with upload_placeholder.container():
                        display_loading_spinner("Uploading document...")
                    
                    upload_result = upload_document(uploaded_file)
                    upload_placeholder.empty()
                    
                    if "error" in upload_result:
                        error_msg = upload_result['error']
                        if "timeout" in error_msg.lower():
                            st.error(f"❌ Upload timeout")
                            st.info("💡 File might be too large or server overloaded")
                        else:
                            st.error(f"❌ Upload failed: {error_msg}")
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
                st.error(f"❌ File validation failed: {validation_result}")

        # Available Documents List
        if api_status == "connected":
            # Use cached documents to avoid repeated API calls
            documents_data = api_status_manager.get_documents()
            
            if "error" not in documents_data:
                documents = documents_data.get("documents", [])
                
                if documents:
                    st.markdown("**📚 Available Documents**")
                    for doc in documents:
                        filename = doc.get("filename", "Unknown")
                        doc_id = doc.get("document_id", "")
                        chunks = doc.get("chunks_count", 0)
                        
                        # Create expandable section for each document
                        with st.expander(f"📄 {filename} ({chunks} chunks)"):
                            st.write(f"**ID:** {doc_id}")
                            st.write(f"**Chunks:** {chunks}")
                            if doc.get("metadata"):
                                st.write("**Metadata:**")
                                st.json(doc["metadata"])
                            
                            # Delete button for each document
                            if st.button("🗑️ Delete", key=f"delete_doc_{doc_id}"):
                                # TODO: Implement delete functionality
                                st.info("Delete functionality coming soon!")
                else:
                    st.info("📚 No documents available yet. Upload some documents to get started!")
            else:
                st.warning(f"⚠️ Could not fetch documents: {documents_data['error']}")
                if st.button("🔄 Retry", key="retry_docs"):
                    api_status_manager.force_refresh()
                    st.rerun()
        
        # Show message when API is disconnected
        elif api_status == "disconnected":
            st.info("⏳ **API is not connected...**")
            st.write("The API server is not responding. Please ensure the API server is running.")
            
            if st.button("🔄 Check Connection", key="check_connection"):
                api_status_manager.force_refresh()
                st.rerun()
        
        # Divider
        st.markdown("---")
        
        # Chat Management Section
        st.markdown("### 💬 Chat Management")
        
        # Uploaded Files List (session state) - simplified
        if st.session_state.uploaded_files:
            st.markdown("**📋 Recently Uploaded**")
            for file_info in st.session_state.uploaded_files:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"📄 {file_info['name']}")
                with col2:
                    if st.button("🗑️", key=f"delete_{file_info['id']}"):
                        # TODO: Implement delete functionality
                        st.session_state.uploaded_files.remove(file_info)
                        st.rerun()

        # Clear Chat History
        if st.button("🗑️ Clear Chat History", use_container_width=True):
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
                    query_placeholder = st.empty()
                    with query_placeholder.container():
                        display_loading_spinner("🤖 Thinking...")
                    
                    response = query_rag(query)
                    query_placeholder.empty()
                    
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
        # Quick Status Panel
        st.markdown("### ⚡ Quick Status")
        
        if api_status == "connected":
            st.success("🟢 API Connected")
            st.info("💡 System is ready for queries")
            
            # Link to health page
            st.markdown("---")
            st.markdown("**🔍 Need detailed status?**")
            st.markdown("[🏥 Health Status Page](http://localhost:8501/health_page)")
        else:
            st.error("🔴 API Disconnected")
            st.warning("⚠️ Check API server status")
            
            # Link to health page for diagnostics
            st.markdown("---")
            st.markdown("**🔍 Troubleshooting:**")
            st.markdown("[🏥 Health Status Page](http://localhost:8501/health_page)")



if __name__ == "__main__":
    main()
