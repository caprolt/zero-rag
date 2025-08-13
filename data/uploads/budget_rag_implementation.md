# Budget-Friendly RAG System Implementation Plan

## 🎯 Project Overview

Build a production-ready RAG system using **entirely free/open-source components** that can run on modest hardware (even a laptop with 8GB+ RAM).

**Total estimated cost: $0-10/month** (optional VPS for demo hosting)

---

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Document      │    │   Embedding     │    │   Vector DB     │
│   Processing    │───▶│   Service       │───▶│   (Qdrant)      │
│   (FastAPI)     │    │   (CPU-based)   │    │   (Local/Free)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                              │
         ▼                                              ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web UI        │    │   RAG API       │    │   Retrieval     │
│   (Streamlit)   │◀──▶│   (FastAPI)     │◀──▶│   Service       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                      ┌─────────────────┐
                      │   LLM Service   │
                      │   (Ollama/HF)   │
                      └─────────────────┘
```

---

## 📋 Phase 1: Core Setup (Week 1)

### 1.1 Environment Setup

```bash
# Create project directory
mkdir budget-rag-system
cd budget-rag-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install core dependencies
pip install fastapi uvicorn streamlit
pip install sentence-transformers transformers torch
pip install qdrant-client pandas numpy
pip install python-multipart aiofiles
```

### 1.2 Docker Setup (Optional but Recommended)

Create `docker-compose.yml`:

```yaml
version: '3.8'
services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
    environment:
      - QDRANT__SERVICE__HTTP_PORT=6333

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  qdrant_data:
  redis_data:
```

### 1.3 Project Structure

```
budget-rag-system/
├── docker-compose.yml
├── requirements.txt
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── embeddings.py
│   │   └── llm.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── document_processor.py
│   │   ├── vector_store.py
│   │   └── rag_pipeline.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── main.py
│   └── ui/
│       └── streamlit_app.py
├── data/
│   └── documents/
└── tests/
```

---

## 🔧 Phase 2: Core Components (Week 1-2)

### 2.1 Configuration (`src/config.py`)

```python
import os
from pathlib import Path

class Config:
    # Model settings
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Small, fast, free
    LLM_MODEL = "microsoft/DialoGPT-medium"  # Fallback, or use Ollama
    
    # Vector DB settings
    QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
    COLLECTION_NAME = "documents"
    
    # Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    DOCUMENTS_DIR = DATA_DIR / "documents"
    
    # Performance settings
    CHUNK_SIZE = 512
    CHUNK_OVERLAP = 50
    MAX_TOKENS = 1000
    TOP_K = 5
    
    # Redis settings (optional caching)
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
```

### 2.2 Embedding Service (`src/models/embeddings.py`)

```python
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
import logging

logger = logging.getLogger(__name__)

class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize with a lightweight, CPU-friendly model"""
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_sentence_embedding_dimension()
        
    def encode(self, texts: List[str]) -> np.ndarray:
        """Encode texts to embeddings"""
        if not texts:
            return np.array([])
        
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,  # Better for cosine similarity
            show_progress_bar=True
        )
        return embeddings
    
    def encode_single(self, text: str) -> np.ndarray:
        """Encode single text to embedding"""
        return self.encode([text])[0]
```

### 2.3 LLM Service (`src/models/llm.py`)

```python
import requests
import json
from typing import Generator, Optional
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self, use_ollama: bool = True):
        self.use_ollama = use_ollama
        if use_ollama:
            self.base_url = "http://localhost:11434"
            self.model_name = "llama3.2:1b"  # Smallest Llama model
        else:
            # Fallback to Hugging Face Transformers (CPU)
            from transformers import pipeline
            self.pipe = pipeline(
                "text-generation",
                model="microsoft/DialoGPT-small",
                device=-1  # CPU
            )
    
    def generate_stream(self, prompt: str, max_tokens: int = 500) -> Generator[str, None, None]:
        """Generate streaming response"""
        if self.use_ollama:
            yield from self._ollama_stream(prompt, max_tokens)
        else:
            yield from self._hf_generate(prompt, max_tokens)
    
    def _ollama_stream(self, prompt: str, max_tokens: int) -> Generator[str, None, None]:
        """Stream from Ollama"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": True,
                    "options": {"num_predict": max_tokens}
                },
                stream=True
            )
            
            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    if "response" in data:
                        yield data["response"]
                        
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            yield "Error generating response. Please try again."
    
    def _hf_generate(self, prompt: str, max_tokens: int) -> Generator[str, None, None]:
        """Fallback HuggingFace generation"""
        try:
            result = self.pipe(prompt, max_length=max_tokens, do_sample=True)
            yield result[0]["generated_text"][len(prompt):]
        except Exception as e:
            logger.error(f"HuggingFace error: {e}")
            yield "Error generating response. Please try again."
```

---

## 📄 Phase 3: Document Processing (Week 2)

### 3.1 Document Processor (`src/services/document_processor.py`)

```python
import os
import re
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from io import StringIO

class DocumentProcessor:
    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Process a single file into chunks"""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Extract text based on file type
        if file_path.suffix.lower() == '.txt':
            text = self._read_txt(file_path)
        elif file_path.suffix.lower() == '.csv':
            text = self._read_csv(file_path)
        elif file_path.suffix.lower() in ['.md', '.markdown']:
            text = self._read_markdown(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_path.suffix}")
        
        # Split into chunks
        chunks = self._split_text(text)
        
        # Create documents
        documents = []
        for i, chunk in enumerate(chunks):
            documents.append({
                "id": f"{file_path.stem}_{i}",
                "text": chunk,
                "source": str(file_path),
                "chunk_index": i,
                "metadata": {
                    "filename": file_path.name,
                    "file_type": file_path.suffix,
                    "chunk_count": len(chunks)
                }
            })
        
        return documents
    
    def _read_txt(self, file_path: Path) -> str:
        """Read plain text file"""
        return file_path.read_text(encoding='utf-8')
    
    def _read_csv(self, file_path: Path) -> str:
        """Convert CSV to readable text"""
        df = pd.read_csv(file_path)
        return df.to_string(index=False)
    
    def _read_markdown(self, file_path: Path) -> str:
        """Read markdown file (treat as plain text for now)"""
        return file_path.read_text(encoding='utf-8')
    
    def _split_text(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        # Clean text
        text = re.sub(r'\s+', ' ', text.strip())
        
        if len(text) <= self.chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings near the chunk boundary
                for i in range(end, max(start + self.chunk_size // 2, end - 100), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
            if start >= len(text):
                break
        
        return chunks
```

---

## 🗄️ Phase 4: Vector Store (Week 2-3)

### 4.1 Vector Store Service (`src/services/vector_store.py`)

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict, Any, Optional
import uuid
import logging

logger = logging.getLogger(__name__)

class VectorStore:
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = None
    
    def create_collection(self, name: str, vector_size: int):
        """Create or recreate collection"""
        self.collection_name = name
        
        # Check if collection exists
        try:
            collections = self.client.get_collections().collections
            if any(col.name == name for col in collections):
                logger.info(f"Collection {name} already exists")
                return
        except Exception:
            pass
        
        # Create collection
        self.client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=vector_size,
                distance=Distance.COSINE
            )
        )
        logger.info(f"Created collection: {name}")
    
    def add_documents(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]):
        """Add documents with embeddings to the vector store"""
        if not self.collection_name:
            raise ValueError("Collection not initialized")
        
        points = []
        for doc, embedding in zip(documents, embeddings):
            point_id = str(uuid.uuid4())
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload={
                    "text": doc["text"],
                    "source": doc["source"],
                    "chunk_index": doc["chunk_index"],
                    "metadata": doc["metadata"]
                }
            )
            points.append(point)
        
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        logger.info(f"Added {len(points)} documents to {self.collection_name}")
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        if not self.collection_name:
            raise ValueError("Collection not initialized")
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            with_payload=True
        )
        
        documents = []
        for result in results:
            documents.append({
                "text": result.payload["text"],
                "source": result.payload["source"],
                "score": result.score,
                "metadata": result.payload["metadata"]
            })
        
        return documents
    
    def count_documents(self) -> int:
        """Get total number of documents"""
        if not self.collection_name:
            return 0
        
        try:
            info = self.client.get_collection(self.collection_name)
            return info.points_count
        except Exception:
            return 0
```

---

## 🔄 Phase 5: RAG Pipeline (Week 3)

### 5.1 RAG Pipeline (`src/services/rag_pipeline.py`)

```python
from typing import List, Dict, Any, Generator
import logging
from ..models.embeddings import EmbeddingService
from ..models.llm import LLMService
from .vector_store import VectorStore

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self, embedding_service: EmbeddingService, 
                 llm_service: LLMService, vector_store: VectorStore):
        self.embedding_service = embedding_service
        self.llm_service = llm_service
        self.vector_store = vector_store
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Retrieve relevant documents for a query"""
        # Get query embedding
        query_embedding = self.embedding_service.encode_single(query)
        
        # Search vector store
        documents = self.vector_store.search(query_embedding.tolist(), top_k)
        
        logger.info(f"Retrieved {len(documents)} documents for query: {query[:50]}...")
        return documents
    
    def generate_prompt(self, query: str, documents: List[Dict[str, Any]]) -> str:
        """Generate prompt with context from retrieved documents"""
        context_parts = []
        for i, doc in enumerate(documents, 1):
            context_parts.append(f"Document {i}:\n{doc['text']}\n")
        
        context = "\n".join(context_parts)
        
        prompt = f"""Based on the following context documents, please answer the question.

Context:
{context}

Question: {query}

Please provide a helpful and accurate answer based on the context provided. If the context doesn't contain enough information to answer the question, please say so.

Answer:"""
        
        return prompt
    
    def generate_response(self, query: str, top_k: int = 5, 
                         max_tokens: int = 500) -> Generator[str, None, None]:
        """Generate streaming RAG response"""
        try:
            # Retrieve relevant documents
            documents = self.retrieve(query, top_k)
            
            if not documents:
                yield "I couldn't find any relevant information to answer your question."
                return
            
            # Generate prompt
            prompt = self.generate_prompt(query, documents)
            
            # Generate response
            yield from self.llm_service.generate_stream(prompt, max_tokens)
            
        except Exception as e:
            logger.error(f"Error in RAG pipeline: {e}")
            yield f"Sorry, I encountered an error while processing your question: {str(e)}"
    
    def get_sources(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Get source documents for a query"""
        documents = self.retrieve(query, top_k)
        
        sources = []
        for doc in documents:
            sources.append({
                "source": doc["source"],
                "score": doc["score"],
                "preview": doc["text"][:200] + "..." if len(doc["text"]) > 200 else doc["text"]
            })
        
        return sources
```

---

## 🚀 Phase 6: API & UI (Week 3-4)

### 6.1 FastAPI Backend (`src/api/main.py`)

```python
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import tempfile
from pathlib import Path

from ..config import Config
from ..models.embeddings import EmbeddingService
from ..models.llm import LLMService
from ..services.vector_store import VectorStore
from ..services.document_processor import DocumentProcessor
from ..services.rag_pipeline import RAGPipeline

# Initialize services
config = Config()
embedding_service = EmbeddingService(config.EMBEDDING_MODEL)
llm_service = LLMService()
vector_store = VectorStore(config.QDRANT_HOST, config.QDRANT_PORT)
document_processor = DocumentProcessor(config.CHUNK_SIZE, config.CHUNK_OVERLAP)
rag_pipeline = RAGPipeline(embedding_service, llm_service, vector_store)

app = FastAPI(title="Budget RAG System", version="1.0.0")

# Initialize collection
vector_store.create_collection(config.COLLECTION_NAME, embedding_service.dimension)

class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5
    max_tokens: Optional[int] = 500

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f"_{file.filename}") as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)
        
        # Process document
        documents = document_processor.process_file(tmp_path)
        
        # Generate embeddings
        texts = [doc["text"] for doc in documents]
        embeddings = embedding_service.encode(texts)
        
        # Add to vector store
        vector_store.add_documents(documents, embeddings.tolist())
        
        # Cleanup
        tmp_path.unlink()
        
        return {
            "message": f"Successfully processed {file.filename}",
            "chunks": len(documents),
            "total_documents": vector_store.count_documents()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query_documents(request: QueryRequest):
    """Query documents and get response"""
    try:
        def generate():
            for chunk in rag_pipeline.generate_response(
                request.query, request.top_k, request.max_tokens
            ):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            yield f"data: {json.dumps({'done': True})}\n\n"
        
        return StreamingResponse(
            generate(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sources/{query}")
async def get_sources(query: str, top_k: int = 5):
    """Get source documents for a query"""
    try:
        sources = rag_pipeline.get_sources(query, top_k)
        return {"sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "total_documents": vector_store.count_documents(),
        "embedding_model": config.EMBEDDING_MODEL
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 6.2 Streamlit UI (`src/ui/streamlit_app.py`)

```python
import streamlit as st
import requests
import json
import time
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="Budget RAG System",
    page_icon="🔍",
    layout="wide"
)

# API base URL
API_BASE = "http://localhost:8000"

def main():
    st.title("🔍 Budget RAG System")
    st.markdown("Upload documents and ask questions about them!")
    
    # Sidebar for document upload
    with st.sidebar:
        st.header("📁 Document Upload")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['txt', 'csv', 'md'],
            help="Supported formats: TXT, CSV, Markdown"
        )
        
        if uploaded_file and st.button("Upload Document"):
            with st.spinner("Processing document..."):
                try:
                    files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                    response = requests.post(f"{API_BASE}/upload", files=files)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success(f"✅ {result['message']}")
                        st.info(f"Created {result['chunks']} chunks")
                        st.info(f"Total documents: {result['total_documents']}")
                    else:
                        st.error("Failed to upload document")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        # System status
        st.header("📊 System Status")
        try:
            health = requests.get(f"{API_BASE}/health").json()
            st.metric("Total Documents", health['total_documents'])
            st.success("✅ System Healthy")
        except:
            st.error("❌ API Unavailable")
    
    # Main chat interface
    st.header("💬 Ask Questions")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                with st.expander("📚 Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"**Source {i}** (Score: {source['score']:.3f})")
                        st.markdown(f"File: `{Path(source['source']).name}`")
                        st.markdown(f"Preview: {source['preview']}")
                        st.divider()
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your documents..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                # Stream response
                response = requests.post(
                    f"{API_BASE}/query",
                    json={"query": prompt, "top_k": 5},
                    stream=True
                )
                
                for line in response.iter_lines():
                    if line:
                        line = line.decode('utf-8')
                        if line.startswith('data: '):
                            data = json.loads(line[6:])
                            if 'content' in data:
                                full_response += data['content']
                                response_placeholder.markdown(full_response + "▌")
                            elif data.get('done'):
                                break
                
                response_placeholder.markdown(full_response)
                
                # Get sources
                sources_response = requests.get(f"{API_BASE}/sources/{prompt}")
                sources = sources_response.json().get("sources", [])
                
                # Add to chat history
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": full_response,
                    "sources": sources
                })
                
                # Show sources
                if sources:
                    with st.expander("📚 Sources"):
                        for i, source in enumerate(sources, 1):
                            st.markdown(f"**Source {i}** (Score: {source['score']:.3f})")
                            st.markdown(f"File: `{Path(source['source']).name}`")
                            st.markdown(f"Preview: {source['preview']}")
                            st.divider()
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
```

---

## 🚀 Phase 7: Deployment & Testing (Week 4)

### 7.1 Setup Instructions

Create `setup.sh`:

```bash
#!/bin/bash

# Install Ollama (for LLM)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull small model
ollama pull llama3.2:1b

# Start services
docker-compose up -d

# Install Python dependencies
pip install -r requirements.txt

echo "Setup complete! Run the following commands:"
echo "1. Start API: python -m src.api.main"
echo "2. Start UI: streamlit run src/ui/streamlit_app.py"
```

### 7.2 Quick Start Guide

Create `README.md`:

```markdown
# Budget RAG System

A production-ready RAG system built with free/open-source components.

## Quick Start

1. **Install dependencies:**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

2. **Start services:**
   ```bash
   # Terminal 1: Start Qdrant & Redis
   docker-compose up -d
   
   # Terminal 2: Start API
   python -m src.api.main
   
   # Terminal 3: Start UI
   streamlit run src/ui/streamlit_app.py
   ```

3. **Use the system:**
   - Open http://localhost:8501
   - Upload documents (TXT, CSV, MD)
   - Ask questions!

## Cost Breakdown

- **Development:** $0 (all open source)
- **Hosting (optional):** $5-10/month for small VPS
- **Total:** $0-10/month

## Architecture

- **Frontend:** Streamlit (Free)
- **Backend:** FastAPI (Free)
- **Vector DB:** Qdrant (Free tier: 1M vectors)
- **LLM:** Ollama + Llama3.2:1b (Free)
- **Embeddings:** sentence-transformers (Free)
```

### 7.3 Testing & Validation

Create `test_rag.py`:

```python
import requests
import time

def test_system():
    """Test the RAG system end-to-end"""
    base_url = "http://localhost:8000"
    
    # Test health
    print("Testing health endpoint...")
    response = requests.get(f"{base_url}/health")
    assert response.status_code == 200
    print("✅ Health check passed")
    
    # Test upload (create a test file)
    print("Testing document upload...")
    test_content = """
    This is a test document about artificial intelligence.
    AI systems can process natural language and generate responses.
    Machine learning is a subset of AI that learns from data.
    """
    
    files = {"file": ("test.txt", test_content, "text/plain")}
    response = requests.post(f"{base_url}/upload", files=files)
    assert response.status_code == 200
    print("✅ Document upload passed")
    
    # Test query
    print("Testing query...")
    query_data = {"query": "What is artificial intelligence?", "top_k": 3}
    response = requests.post(f"{base_url}/query", json=query_data, stream=True)
    assert response.status_code == 200
    print("✅ Query test passed")
    
    print("🎉 All tests passed!")

if __name__ == "__main__":
    test_system()
```

---

## 📈 Phase 8: Optimization & Scaling (Ongoing)

### 8.1 Performance Improvements

- **Caching:** Add Redis for frequent queries
- **Batch processing:** Process multiple documents at once
- **Async operations:** Use async for better concurrency

### 8.2 Cost Optimization Tips

1. **Use smaller models initially:** Start with 1-3B parameter models
2. **Optimize chunk sizes:** Balance accuracy vs. speed
3. **Cache embeddings:** Store computed embeddings to avoid recomputation
4. **Use quantized models:** INT8 quantization for faster inference

### 8.3 Production Deployment

For production deployment on a budget:

1. **Digital Ocean Droplet:** $10/month (2GB RAM, 1 vCPU)
2. **Use Qdrant Cloud free tier:** 1M vectors free
3. **Optimize Docker images:** Multi-stage builds
4. **Set up monitoring:** Simple health checks

---

## 🎯 Success Metrics

After completion, you should have:

- ✅ Working RAG system with web UI
- ✅ Document upload and processing
- ✅ Real-time query responses  
- ✅ Source attribution
- ✅ Streaming responses
- ✅ Docker containerization
- ✅ API documentation
- ✅ Cost under $10/month

## 🚀 Next Steps

1. **Add more file formats:** PDF, DOCX support
2. **Improve retrieval:** Hybrid search, reranking
3. **Better UI:** Chat history, user management
4. **Monitoring:** Add Prometheus metrics
5. **Scale up:** Multi-user support, authentication

---

*Total implementation time: 3-4 weeks*  
*Total cost: $0-10/month*  
*Perfect for portfolio demonstration!*