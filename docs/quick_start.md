# ZeroRAG API Quick Start Guide

Get up and running with the ZeroRAG API in minutes. This guide will walk you through the essential steps to start using the API for document processing and AI-powered question answering.

## Prerequisites

- Python 3.8 or higher
- 4GB+ RAM (8GB+ recommended)
- 2GB+ free disk space
- Internet connection for model downloads

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-repo/zero-rag.git
cd zero-rag
```

### 2. Set Up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example configuration
cp env.example .env

# Edit configuration (optional)
# The default configuration works for most use cases
```

## Starting the API

### Development Mode

```bash
# Start the API server
python -m src.api.main

# Or use the provided script
python scripts/setup_dev.py
```

The API will be available at `http://localhost:8000`

### Production Mode

```bash
# Start with production settings
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Quick Start Examples

### 1. Check System Health

First, verify that all services are running properly:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": 1703123456.789,
  "services": {
    "document_processor": {"status": "healthy"},
    "vector_store": {"status": "healthy"},
    "llm_service": {"status": "healthy"}
  },
  "uptime": 3600.5,
  "version": "1.0.0"
}
```

### 2. Upload Your First Document

Upload a document to the knowledge base:

```bash
# Upload a PDF file
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@your_document.pdf" \
  -F 'metadata={"category": "manual", "department": "engineering"}'
```

Expected response:
```json
{
  "document_id": "doc_abc123def456",
  "filename": "your_document.pdf",
  "file_size": 2048576,
  "chunks_created": 25,
  "processing_time": 3.45,
  "status": "completed",
  "metadata": {
    "file_type": "pdf",
    "pages": 15,
    "language": "en"
  }
}
```

### 3. Ask Questions

Query your knowledge base:

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the main features described in the document?",
    "top_k": 5,
    "include_sources": true
  }'
```

Expected response:
```json
{
  "answer": "Based on the document, the main features include...",
  "sources": [
    {
      "document_id": "doc_abc123def456",
      "filename": "your_document.pdf",
      "content": "The system features include...",
      "score": 0.95,
      "page": 5
    }
  ],
  "response_time": 2.34,
  "tokens_used": 450,
  "metadata": {
    "documents_retrieved": 5,
    "context_length": 3200,
    "model_used": "llama2-7b"
  }
}
```

## Python Client Example

Here's a complete Python example:

```python
import requests
import json

class ZeroRAGClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def health_check(self):
        """Check system health"""
        response = requests.get(f"{self.base_url}/health")
        return response.json()
    
    def upload_document(self, file_path, metadata=None):
        """Upload a document"""
        files = {'file': open(file_path, 'rb')}
        data = {'metadata': json.dumps(metadata)} if metadata else {}
        
        response = requests.post(f"{self.base_url}/documents/upload", 
                               files=files, data=data)
        return response.json()
    
    def query(self, question, **kwargs):
        """Ask a question"""
        data = {'query': question, **kwargs}
        response = requests.post(f"{self.base_url}/query", json=data)
        return response.json()
    
    def list_documents(self):
        """List all documents"""
        response = requests.get(f"{self.base_url}/documents")
        return response.json()

# Usage example
if __name__ == "__main__":
    client = ZeroRAGClient()
    
    # Check health
    health = client.health_check()
    print(f"System status: {health['status']}")
    
    # Upload document
    result = client.upload_document("manual.pdf", {"category": "documentation"})
    print(f"Uploaded: {result['document_id']}")
    
    # Ask question
    answer = client.query("How do I configure the system?")
    print(f"Answer: {answer['answer']}")
    print(f"Sources: {len(answer['sources'])} documents")
```

## JavaScript Client Example

```javascript
class ZeroRAGClient {
    constructor(baseUrl = 'http://localhost:8000') {
        this.baseUrl = baseUrl;
    }
    
    async healthCheck() {
        const response = await fetch(`${this.baseUrl}/health`);
        return await response.json();
    }
    
    async uploadDocument(file, metadata = {}) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('metadata', JSON.stringify(metadata));
        
        const response = await fetch(`${this.baseUrl}/documents/upload`, {
            method: 'POST',
            body: formData
        });
        
        return await response.json();
    }
    
    async query(question, options = {}) {
        const response = await fetch(`${this.baseUrl}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: question,
                ...options
            })
        });
        
        return await response.json();
    }
    
    async listDocuments() {
        const response = await fetch(`${this.baseUrl}/documents`);
        return await response.json();
    }
}

// Usage example
async function example() {
    const client = new ZeroRAGClient();
    
    // Check health
    const health = await client.healthCheck();
    console.log(`System status: ${health.status}`);
    
    // Upload document
    const fileInput = document.getElementById('file-input');
    const result = await client.uploadDocument(fileInput.files[0], {
        category: 'documentation'
    });
    console.log(`Uploaded: ${result.document_id}`);
    
    // Ask question
    const answer = await client.query('How do I configure the system?');
    console.log(`Answer: ${answer.answer}`);
    console.log(`Sources: ${answer.sources.length} documents`);
}
```

## Interactive Documentation

Once the API is running, you can access:

- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

The interactive documentation allows you to:
- Test all endpoints directly in the browser
- View request/response examples
- Understand parameter requirements
- Try different configurations

## Common Use Cases

### 1. Document Q&A

```python
# Upload multiple documents
documents = [
    "product_manual.pdf",
    "technical_specs.pdf", 
    "user_guide.pdf"
]

for doc in documents:
    client.upload_document(doc, {"category": "product"})

# Ask questions
questions = [
    "What are the system requirements?",
    "How do I install the software?",
    "What troubleshooting steps are available?"
]

for question in questions:
    answer = client.query(question)
    print(f"Q: {question}")
    print(f"A: {answer['answer']}\n")
```

### 2. Content Summarization

```python
# Upload a long document
client.upload_document("research_paper.pdf")

# Get summary
summary = client.query(
    "Provide a comprehensive summary of this document",
    response_format="bullet_points",
    max_tokens=500
)
print(summary['answer'])
```

### 3. Information Extraction

```python
# Extract specific information
extraction = client.query(
    "Extract all contact information, addresses, and phone numbers from this document",
    response_format="json",
    top_k=10
)
print(extraction['answer'])
```

## Troubleshooting

### Common Issues

1. **Service Not Starting**
   ```bash
   # Check if port is in use
   netstat -an | grep 8000
   
   # Kill process if needed
   kill -9 <PID>
   ```

2. **Model Download Issues**
   ```bash
   # Check internet connection
   ping google.com
   
   # Clear model cache
   rm -rf data/cache/models/*
   ```

3. **Memory Issues**
   ```bash
   # Check available memory
   free -h
   
   # Reduce model size in config
   # Use smaller models like llama2-7b instead of llama2-13b
   ```

4. **File Upload Fails**
   ```bash
   # Check file size
   ls -lh your_file.pdf
   
   # Check file format
   file your_file.pdf
   ```

### Getting Help

- **Logs**: Check console output for error messages
- **Health Check**: Use `/health` endpoint to diagnose issues
- **Documentation**: Visit `/docs` for detailed API reference
- **Community**: Join our forum for support

## Next Steps

1. **Explore Advanced Features**:
   - Streaming responses
   - File validation
   - Progress tracking
   - Cleanup tools

2. **Production Deployment**:
   - Set up reverse proxy (nginx)
   - Configure SSL certificates
   - Implement authentication
   - Set up monitoring

3. **Integration**:
   - Build web applications
   - Create chatbots
   - Develop mobile apps
   - Integrate with existing systems

4. **Customization**:
   - Fine-tune models
   - Customize prompts
   - Adjust chunking strategies
   - Optimize performance

## Support

- **Documentation**: `/docs` - Interactive API documentation
- **Health Check**: `/health` - System status
- **Metrics**: `/metrics` - Performance monitoring
- **Community**: Join our forum for discussions and help

---

*This quick start guide covers the essentials. For detailed information, refer to the full API documentation at `/docs`.*
