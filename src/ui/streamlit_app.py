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
    /* Hide Streamlit UI elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stToolbar {display: none !important;}
    .stDeployButton {display: none !important;}
    
    /* Main layout styling */
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
    
    /* Status indicators */
    .status-success {color: #28a745; font-weight: bold;}
    .status-error {color: #dc3545; font-weight: bold;}
    .status-warning {color: #ffc107; font-weight: bold;}
    
    /* Chat interface styling */
    .chat-message-bubble {
        max-width: 80%;
        padding: 0.75rem 1rem;
        border-radius: 1rem;
        margin-bottom: 0.5rem;
        word-wrap: break-word;
    }
    
    .chat-message-user {
        background-color: #1f77b4;
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 0.25rem;
    }
    
    .chat-message-assistant {
        background-color: #f0f0f0;
        color: #333;
        margin-right: auto;
        border-bottom-left-radius: 0.25rem;
    }
    
    .chat-message-time {
        font-size: 0.75rem;
        color: #999;
        margin-top: 0.25rem;
        text-align: right;
    }
    
    .chat-message-sources {
        margin-top: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px solid #e0e0e0;
    }
    
    .chat-source-item {
        font-size: 0.8rem;
        color: #666;
        margin-bottom: 0.25rem;
        padding: 0.25rem 0.5rem;
        background-color: #f8f9fa;
        border-radius: 0.25rem;
        border-left: 3px solid #1f77b4;
    }
    
    /* Loading spinner */
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
    
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        text-align: center;
    }
    
    /* Document card styling */
    .document-card {
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 0.75rem;
        margin-bottom: 0.5rem;
        background-color: #fafafa;
    }
    
    .document-card h4 {
        margin: 0 0 0.5rem 0;
        color: #1f77b4;
        font-size: 0.9rem;
    }
    
    .document-card p {
        margin: 0.25rem 0;
        font-size: 0.8rem;
        color: #666;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .chat-message-bubble {
            max-width: 95%;
        }
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
        self.check_interval = 5
        self.connection_attempts = 0
        self.max_attempts = 3
        self.documents_cache = {}
        self.documents_cache_time = 0
        self.documents_cache_interval = 30
        
    def get_status(self) -> Dict[str, Any]:
        """Get current API status with caching and dynamic updates."""
        current_time = time.time()
        
        if current_time - self.last_check > self.check_interval:
            self._update_status()
            self.last_check = current_time
        
        return self.status_cache
    
    def _update_status(self):
        """Update the API status cache with simplified logic."""
        try:
            # First try a quick ping
            ping_response = requests.get(f"{API_BASE_URL}/health/ping", timeout=2)
            ping_ok = ping_response.status_code == 200
            
            if ping_ok:
                # If ping works, try full health check
                try:
                    health_response = requests.get(f"{API_BASE_URL}/health/", timeout=5)
                    health_ok = health_response.status_code == 200
                    health_data = health_response.json() if health_ok else None
                    
                    if health_ok and health_data and health_data.get('status') == 'healthy':
                        self.status_cache = {
                            "status": "connected",
                            "ping_ok": True,
                            "health_ok": True,
                            "docs_ready": True,
                            "health_data": health_data,
                            "last_check": time.time(),
                            "error": None
                        }
                        self.connection_attempts = 0
                    else:
                        # API is responding but not fully ready
                        self.connection_attempts += 1
                        self.status_cache = {
                            "status": "starting",
                            "ping_ok": True,
                            "health_ok": False,
                            "docs_ready": False,
                            "health_data": health_data,
                            "last_check": time.time(),
                            "error": "API is starting up, please wait 30-40 seconds"
                        }
                except requests.RequestException:
                    # API is responding but health check failed
                    self.connection_attempts += 1
                    self.status_cache = {
                        "status": "starting",
                        "ping_ok": True,
                        "health_ok": False,
                        "docs_ready": False,
                        "health_data": None,
                        "last_check": time.time(),
                        "error": "API is starting up, please wait 30-40 seconds"
                    }
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
        
        if (current_time - self.documents_cache_time < self.documents_cache_interval and 
            self.documents_cache):
            return self.documents_cache
        
        try:
            documents_response = requests.get(f"{API_BASE_URL}/documents", timeout=30)
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
        self.documents_cache_time = 0
        self._update_status()
        return self.status_cache

# Global API status manager
api_status_manager = APIStatusManager()

def check_api_health() -> bool:
    """Simple API health check using the status manager."""
    status = api_status_manager.get_status()
    return status.get("status") == "connected"

def display_api_status():
    """Display dynamic API status with real-time updates."""
    status = api_status_manager.get_status()
    
    if status.get("error"):
        if status.get("status") == "starting":
            st.warning(f"🔄 {status['error']}")
        else:
            st.error(f"Connection Error: {status['error']}")
    
    return status.get("status", "disconnected")

def upload_document(file) -> Dict[str, Any]:
    """Upload a document to the API."""
    try:
        files = {"file": (file.name, file.getvalue(), file.type)}
        response = requests.post(
            f"{API_BASE_URL}/documents/upload",
            files=files,
            timeout=60
        )
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Upload error: {e}")
        return {"error": str(e)}

def validate_file(file) -> Dict[str, Any]:
    """Validate a file before upload."""
    try:
        data = {
            "filename": file.name,
            "file_size": file.size,
            "content_type": file.type
        }
        response = requests.post(
            f"{API_BASE_URL}/documents/validate",
            json=data,
            timeout=30
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

def query_rag(question: str, stream: bool = False, document_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    """Send a query to the RAG system."""
    try:
        data = {"query": question, "stream": stream}
        
        # Add document filtering if specified
        if document_ids:
            data["document_ids"] = document_ids
        
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
    if "selected_documents" not in st.session_state:
        st.session_state.selected_documents = set()
    
    # Show immediate loading state
    if "app_loaded" not in st.session_state:
        st.session_state.app_loaded = False
        with st.spinner("🚀 Initializing ZeroRAG..."):
            api_status_manager.get_status()
            st.session_state.app_loaded = True
        st.rerun()
    
    # Sidebar - Document Management
    with st.sidebar:
        
        uploaded_file = st.file_uploader(
            "Upload a file to chat about",
            type=SUPPORTED_FORMATS,
            help="Supported formats: TXT, MD, PDF, CSV, DOCX",
            key="sidebar_uploader"
        )

        if uploaded_file is not None:
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
                
                if st.button("🚀 Upload Document", key="sidebar_upload_btn", use_container_width=True):
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
                        
                        if document_id:
                            progress_placeholder = st.empty()
                            for i in range(10):
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

        # Document Selection Section
        st.markdown("### 📚 Available Documents")
        
        documents_data = api_status_manager.get_documents()
        
        if "error" not in documents_data:
            documents = documents_data.get("documents", [])
            
            if documents:
                st.markdown("**Select documents to include in chat context:**")
                
                # Create a clean list with checkboxes
                for doc in documents:
                    filename = doc.get("filename", "Unknown")
                    doc_id = doc.get("document_id", "")
                    
                    # Create a unique key for the checkbox
                    checkbox_key = f"doc_select_{doc_id}"
                    
                    # Check if this document is currently selected
                    is_selected = doc_id in st.session_state.selected_documents
                    
                    # Create checkbox with document name
                    if st.checkbox(
                        f"📄 {filename}",
                        value=is_selected,
                        key=checkbox_key,
                        help=f"Select to include {filename} in chat context"
                    ):
                        st.session_state.selected_documents.add(doc_id)
                    else:
                        # Remove from selected if unchecked
                        st.session_state.selected_documents.discard(doc_id)
                
                # Show selection summary
                selected_count = len(st.session_state.selected_documents)
                if selected_count > 0:
                    st.success(f"✅ {selected_count} document(s) selected for chat context")
                else:
                    st.info("ℹ️ No documents selected - chat will use all available documents")
                
                # Add a clear selection button
                if selected_count > 0:
                    if st.button("🗑️ Clear Selection", key="clear_doc_selection", use_container_width=True):
                        st.session_state.selected_documents.clear()
                        st.rerun()
            else:
                st.info("📚 No documents available yet. Upload some documents to get started!")
        else:
            st.warning(f"⚠️ Could not fetch documents: {documents_data['error']}")
            if st.button("🔄 Retry", key="sidebar_retry_docs"):
                api_status_manager.force_refresh()
                st.rerun()

        # Chat Management Section
        st.markdown("### 💬 Chat Management")
        
        if st.session_state.uploaded_files:
            st.markdown("**📋 Recently Uploaded Files**")
            for file_info in st.session_state.uploaded_files:
                st.markdown(f"""
                <div style="
                    border: 1px solid #e0e0e0;
                    border-radius: 0.5rem;
                    padding: 0.5rem;
                    margin-bottom: 0.5rem;
                    background-color: #f8f9fa;
                ">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 500; font-size: 0.9rem;">📄 {file_info['name']}</span>
                        <span style="font-size: 0.7rem; color: #666;">{file_info['size']} bytes</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("🗑️ Remove", key=f"sidebar_delete_{file_info['id']}", use_container_width=True):
                    st.session_state.uploaded_files.remove(file_info)
                    st.rerun()
        else:
            st.info("📋 No recently uploaded files")
        
        st.markdown("**🗂️ Chat History**")
        chat_count = len(st.session_state.chat_history)
        st.metric("Messages", chat_count)
        
        if st.button("🗑️ Clear Chat History", key="sidebar_clear_chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
        
        if st.button("🔄 New Chat", key="sidebar_new_chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

        # API Status in Sidebar
        st.markdown("### ⚡ API Status")
        api_status = display_api_status()
        
        if api_status == "connected":
            st.success("🟢 Connected")
        elif api_status == "starting":
            st.warning("🟡 Starting up...")
            st.info("⏳ Please wait 30-40 seconds for full startup")
        else:
            st.error("🔴 Disconnected")
            if st.button("🔄 Retry Connection", key="sidebar_retry_connection"):
                api_status_manager.force_refresh()
                st.rerun()

    # Main Content Area - Chat Interface
    st.markdown('<h1 class="main-header">🤖 ZeroRAG</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #666;">AI-Powered Document Q&A System</p>', unsafe_allow_html=True)
    st.markdown("---")

    # Chat Interface Section
    st.markdown("### 💬 Chat with Your Documents")
    
    if "show_file_uploader" not in st.session_state:
        st.session_state.show_file_uploader = False
    
    chat_container = st.container()
    
    with chat_container:
        # Chat messages area
        messages_container = st.container()
        
        with messages_container:
            for i, message in enumerate(st.session_state.chat_history):
                timestamp = datetime.now().strftime("%H:%M")
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="chat-message-bubble chat-message-user">
                        {message["content"]}
                        <div class="chat-message-time">{timestamp}</div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="chat-message-bubble chat-message-assistant">
                        {message["content"]}
                        <div class="chat-message-time">{timestamp}</div>
                    """, unsafe_allow_html=True)
                    
                    if "sources" in message and message["sources"]:
                        st.markdown('<div class="chat-message-sources">', unsafe_allow_html=True)
                        for source in message["sources"]:
                            st.markdown(f'<div class="chat-source-item">📄 {source.get("title", "Unknown")} (Relevance: {source.get("score", 0):.2f})</div>', unsafe_allow_html=True)
                        st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat input area
        input_container = st.container()
        
        with input_container:
            col1, col2 = st.columns([8, 1])
            
            with col1:
                query = st.text_area(
                    "Type your message...",
                    height=100,
                    placeholder="Ask a question about your documents...",
                    key="chat_text_input",
                    label_visibility="collapsed"
                )
            
            with col2:
                if st.button("➤", key="send_button", help="Send message"):
                    if query.strip():
                        st.session_state.chat_history.append({
                            "role": "user",
                            "content": query
                        })
                        
                        # Get selected document IDs for filtering
                        selected_doc_ids = list(st.session_state.selected_documents) if st.session_state.selected_documents else None
                        
                        response = query_rag(query, document_ids=selected_doc_ids)
                        
                        if "error" in response:
                            st.error(f"Query failed: {response['error']}")
                        else:
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": response.get("answer", "No answer generated"),
                                "sources": response.get("sources", [])
                            })
                        
                        st.rerun()
        
        # Quick Actions
        st.markdown("### 📁 Quick Actions")
        
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            if st.button("📁 Upload File", key="quick_upload", use_container_width=True):
                st.session_state.show_file_uploader = True
                st.rerun()
        
        with col2:
            if st.button("🔄 New Chat", key="quick_new_chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        with col3:
            if st.button("🗑️ Clear History", key="quick_clear", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        with col4:
            st.empty()
        
        # File uploader
        if st.session_state.get("show_file_uploader", False):
            upload_container = st.container()
            
            with upload_container:
                st.markdown("### 📁 Upload File")
                uploaded_file = st.file_uploader(
                    "Choose a file to upload",
                    type=SUPPORTED_FORMATS,
                    key="chat_file_uploader",
                    help="Upload a document to chat about"
                )
                
                if uploaded_file is not None:
                    with st.spinner("Validating file..."):
                        validation_result = validate_file(uploaded_file)
                    
                    if "error" not in validation_result and validation_result.get("is_valid", False):
                        with st.spinner("Uploading file..."):
                            upload_result = upload_document(uploaded_file)
                        
                        if "error" not in upload_result:
                            st.success(f"✅ {uploaded_file.name} uploaded successfully!")
                            st.session_state.uploaded_files.append({
                                "name": uploaded_file.name,
                                "id": upload_result.get("document_id", ""),
                                "size": uploaded_file.size
                            })
                            st.session_state.show_file_uploader = False
                            st.rerun()
                        else:
                            st.error(f"❌ Upload failed: {upload_result['error']}")
                    else:
                        st.error(f"❌ File validation failed: {validation_result}")
                
                if st.button("❌ Close", key="close_uploader"):
                    st.session_state.show_file_uploader = False
                    st.rerun()

if __name__ == "__main__":
    main()
