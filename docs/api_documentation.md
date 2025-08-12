# ZeroRAG API Documentation

## Overview

The ZeroRAG API is a production-ready Retrieval-Augmented Generation (RAG) system that provides comprehensive document processing, vector search, and AI-powered question answering capabilities. This documentation covers all API endpoints, request/response formats, error handling, and usage examples.

## Table of Contents

1. [Authentication](#authentication)
2. [Base URL](#base-url)
3. [Rate Limiting](#rate-limiting)
4. [Error Handling](#error-handling)
5. [Health & Monitoring](#health--monitoring)
6. [Documents](#documents)
7. [Query Processing](#query-processing)
8. [Advanced Features](#advanced-features)
9. [Troubleshooting](#troubleshooting)
10. [Examples](#examples)

## Authentication

Currently, the API does not require authentication for development use. For production deployments, consider implementing:

- API key authentication
- JWT tokens
- OAuth 2.0
- Rate limiting per user/IP

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://api.zerorag.com`

## Rate Limiting

The API implements configurable rate limiting to prevent abuse:

- **Default**: 100 requests per minute per IP
- **Upload endpoints**: 10 requests per minute per IP
- **Query endpoints**: 50 requests per minute per IP

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

## Error Handling

All API endpoints return standardized error responses:

### Error Response Format

```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "timestamp": 1703123456.789,
  "request_id": "req_abc123def456"
}
```

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 413 | Payload Too Large |
| 422 | Validation Error |
| 429 | Too Many Requests |
| 500 | Internal Server Error |
| 502 | Bad Gateway |
| 503 | Service Unavailable |

### Common Error Codes

| Error Code | Description | Solution |
|------------|-------------|----------|
| `FILE_TOO_LARGE` | File size exceeds maximum allowed | Reduce file size or split into smaller files |
| `UNSUPPORTED_FORMAT` | File format not supported | Convert to supported format (PDF, TXT, MD, CSV) |
| `INVALID_QUERY` | Query is too short or contains invalid characters | Ensure query is 1-1000 characters |
| `SERVICE_UNAVAILABLE` | Required service is down | Check system health and retry |
| `RATE_LIMIT_EXCEEDED` | Too many requests | Wait and retry with exponential backoff |

## Health & Monitoring

### Get System Health

**Endpoint**: `GET /health`

**Description**: Comprehensive system health check including all services.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": 1703123456.789,
  "services": {
    "document_processor": {
      "status": "healthy",
      "last_check": 1703123456.789,
      "error_count": 0,
      "health_data": {"queue_size": 0}
    },
    "vector_store": {
      "status": "healthy",
      "last_check": 1703123456.789,
      "error_count": 0,
      "health_data": {"document_count": 150}
    },
    "llm_service": {
      "status": "healthy",
      "last_check": 1703123456.789,
      "error_count": 0,
      "health_data": {"model_loaded": true}
    }
  },
  "uptime": 3600.5,
  "version": "1.0.0"
}
```

**Status Values**:
- `healthy`: All services operational
- `degraded`: Some services have issues but system is functional
- `unhealthy`: Critical services are down

### Get Service Health

**Endpoint**: `GET /health/services/{service_name}`

**Description**: Individual service health check.

**Parameters**:
- `service_name` (path): Name of the service (document_processor, vector_store, llm_service)

**Response**:
```json
{
  "service": "document_processor",
  "status": "healthy",
  "health_data": {
    "queue_size": 0,
    "memory_usage_mb": 128.5,
    "cpu_usage_percent": 15.2
  },
  "last_check": 1703123456.789,
  "error_count": 0
}
```

### Get System Metrics

**Endpoint**: `GET /metrics`

**Description**: System performance and usage metrics.

**Response**:
```json
{
  "total_requests": 1250,
  "failed_requests": 23,
  "success_rate": 0.982,
  "uptime": 86400.5,
  "services": {
    "document_processor": {
      "documents_processed": 150,
      "average_processing_time": 2.34,
      "queue_size": 0
    },
    "vector_store": {
      "total_documents": 150,
      "total_chunks": 3750,
      "index_size_mb": 45.2
    },
    "llm_service": {
      "queries_processed": 1250,
      "average_response_time": 1.87,
      "tokens_generated": 45000
    }
  }
}
```

## Documents

### Upload Document

**Endpoint**: `POST /documents/upload`

**Description**: Upload and process a document for RAG queries.

**Request**: Multipart form data
- `file` (required): Document file (PDF, TXT, MD, CSV)
- `metadata` (optional): JSON string with additional metadata

**Supported Formats**:
- PDF (`.pdf`)
- Text (`.txt`)
- Markdown (`.md`)
- CSV (`.csv`)

**File Size Limits**:
- Maximum: 10MB
- Recommended: < 5MB for optimal performance

**Response**:
```json
{
  "document_id": "doc_abc123def456",
  "filename": "product_manual.pdf",
  "file_size": 2048576,
  "chunks_created": 25,
  "processing_time": 3.45,
  "status": "completed",
  "metadata": {
    "file_type": "pdf",
    "pages": 15,
    "language": "en",
    "processing_steps": ["upload", "validation", "parsing", "chunking", "embedding", "storage"]
  }
}
```

**Example cURL**:
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf" \
  -F 'metadata={"category": "manual", "department": "engineering"}'
```

### Validate File

**Endpoint**: `POST /documents/validate`

**Description**: Validate a file before upload to check compatibility and estimate processing time.

**Request**:
```json
{
  "filename": "document.pdf",
  "file_size": 1048576,
  "content_type": "application/pdf"
}
```

**Response**:
```json
{
  "is_valid": true,
  "errors": [],
  "warnings": ["Large file size may take longer to process"],
  "estimated_processing_time": 45.2,
  "supported_features": ["text_extraction", "metadata_extraction", "chunking", "embedding"]
}
```

### Get Upload Progress

**Endpoint**: `GET /documents/upload/{document_id}/progress`

**Description**: Get real-time progress of document processing.

**Parameters**:
- `document_id` (path): Document identifier

**Response**:
```json
{
  "document_id": "doc_abc123def456",
  "status": "processing",
  "progress": 75.5,
  "current_step": "embedding",
  "estimated_time_remaining": 15.2,
  "error_message": null,
  "metadata": {
    "steps_completed": ["upload", "validation", "parsing", "chunking"],
    "current_step_progress": 60.0,
    "total_steps": 6
  }
}
```

### List Documents

**Endpoint**: `GET /documents`

**Description**: Get paginated list of all documents.

**Query Parameters**:
- `limit` (optional): Number of documents to return (default: 20, max: 100)
- `offset` (optional): Number of documents to skip (default: 0)
- `status` (optional): Filter by status (active, archived, deleted, processing, failed)

**Response**:
```json
{
  "documents": [
    {
      "document_id": "doc_abc123def456",
      "filename": "product_manual.pdf",
      "file_size": 2048576,
      "upload_timestamp": 1703123456.789,
      "chunks_count": 25,
      "status": "active",
      "metadata": {
        "file_type": "pdf",
        "pages": 15,
        "language": "en"
      }
    }
  ],
  "total": 150,
  "limit": 20,
  "offset": 0
}
```

### Get Document Details

**Endpoint**: `GET /documents/{document_id}`

**Description**: Get detailed information about a specific document.

**Parameters**:
- `document_id` (path): Document identifier

**Response**: Same as document in list response

### Delete Document

**Endpoint**: `DELETE /documents/{document_id}`

**Description**: Delete a document and its associated data.

**Parameters**:
- `document_id` (path): Document identifier

**Response**: 204 No Content

## Query Processing

### Process Query

**Endpoint**: `POST /query`

**Description**: Process a RAG query and return an AI-generated answer.

**Request**:
```json
{
  "query": "What are the key features of our product?",
  "top_k": 5,
  "score_threshold": 0.7,
  "max_context_length": 4000,
  "temperature": 0.7,
  "max_tokens": 1024,
  "include_sources": true,
  "response_format": "text",
  "safety_level": "standard"
}
```

**Parameters**:
- `query` (required): User query (1-1000 characters)
- `top_k` (optional): Number of documents to retrieve (1-20, default: 5)
- `score_threshold` (optional): Minimum similarity score (0.0-1.0, default: 0.7)
- `max_context_length` (optional): Maximum context length (1000-8000, default: 4000)
- `temperature` (optional): Response creativity (0.0-2.0, default: 0.7)
- `max_tokens` (optional): Maximum response tokens (100-4096, default: 1024)
- `include_sources` (optional): Include source documents (default: true)
- `response_format` (optional): Response format (text, json, bullet_points, table, default: text)
- `safety_level` (optional): Content safety (standard, conservative, permissive, default: standard)

**Response**:
```json
{
  "answer": "Our product offers several key features including advanced AI capabilities, real-time processing, and comprehensive analytics. The system is designed for scalability and ease of use.",
  "sources": [
    {
      "document_id": "doc_123",
      "filename": "product_manual.pdf",
      "content": "The product features include advanced AI capabilities...",
      "score": 0.95,
      "page": 5
    },
    {
      "document_id": "doc_124",
      "filename": "technical_specs.pdf",
      "content": "Real-time processing capabilities...",
      "score": 0.87,
      "page": 12
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

**Example cURL**:
```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key features of our product?",
    "top_k": 5,
    "include_sources": true
  }'
```

### Streaming Query

**Endpoint**: `GET /query/stream`

**Description**: Process a RAG query with streaming response using Server-Sent Events (SSE).

**Query Parameters**: Same as POST /query

**Response**: Server-Sent Events stream

**Event Types**:
- `content`: Generated answer chunks
- `sources`: Source document information
- `progress`: Processing progress updates
- `error`: Error messages
- `end`: Stream completion

**Example JavaScript**:
```javascript
const eventSource = new EventSource('/query/stream?query=What are the key features?');

eventSource.onmessage = function(event) {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'content':
      console.log('Content:', data.content);
      break;
    case 'sources':
      console.log('Sources:', data.sources);
      break;
    case 'end':
      eventSource.close();
      break;
  }
};
```

## Advanced Features

### List Streaming Connections

**Endpoint**: `GET /advanced/connections`

**Description**: List all active streaming connections.

**Response**:
```json
[
  {
    "connection_id": "conn_abc123def456",
    "created_at": 1703123456.789,
    "last_activity": 1703123500.123,
    "status": "active",
    "metadata": {
      "user_agent": "Mozilla/5.0...",
      "ip_address": "192.168.1.100",
      "query_type": "rag"
    }
  }
]
```

### Close Streaming Connection

**Endpoint**: `DELETE /advanced/connections/{connection_id}`

**Description**: Close a specific streaming connection.

**Parameters**:
- `connection_id` (path): Connection identifier

**Response**: 204 No Content

### Document Cleanup

**Endpoint**: `POST /advanced/cleanup`

**Description**: Clean up documents and files based on criteria.

**Request**:
```json
{
  "document_ids": ["doc_123", "doc_456"],
  "older_than_days": 30,
  "failed_uploads_only": false,
  "dry_run": true
}
```

**Parameters**:
- `document_ids` (optional): Specific document IDs to cleanup
- `older_than_days` (optional): Cleanup documents older than N days
- `failed_uploads_only` (optional): Cleanup only failed uploads (default: false)
- `dry_run` (optional): Perform dry run without deletion (default: false)

**Response**:
```json
{
  "deleted_documents": 15,
  "deleted_files": 15,
  "freed_space_bytes": 52428800,
  "errors": [],
  "dry_run": false
}
```

### Storage Statistics

**Endpoint**: `GET /advanced/storage/stats`

**Description**: Get storage usage statistics.

**Response**:
```json
{
  "total_documents": 150,
  "total_chunks": 3750,
  "total_size_bytes": 524288000,
  "index_size_bytes": 47185920,
  "available_space_bytes": 107374182400,
  "storage_efficiency": 0.91
}
```

## Troubleshooting

### Common Issues

#### 1. File Upload Fails

**Symptoms**: 400 Bad Request with "FILE_TOO_LARGE" error

**Solutions**:
- Reduce file size to under 10MB
- Split large documents into smaller files
- Compress PDF files before upload

#### 2. Query Returns No Results

**Symptoms**: Empty sources array or generic responses

**Solutions**:
- Check if documents are properly uploaded and processed
- Lower the `score_threshold` parameter
- Increase the `top_k` parameter
- Verify document content is relevant to the query

#### 3. Slow Response Times

**Symptoms**: High response times (>10 seconds)

**Solutions**:
- Check system health at `/health`
- Monitor system metrics at `/metrics`
- Reduce `max_context_length` parameter
- Consider upgrading hardware resources

#### 4. Streaming Connection Drops

**Symptoms**: SSE connection closes unexpectedly

**Solutions**:
- Implement reconnection logic in client
- Check network stability
- Monitor connection status at `/advanced/connections`
- Increase client timeout settings

#### 5. Service Unavailable

**Symptoms**: 503 Service Unavailable errors

**Solutions**:
- Check individual service health at `/health/services/{service}`
- Restart the application
- Check system resources (CPU, memory, disk)
- Review application logs

### Performance Optimization

#### For Document Uploads
- Use supported file formats (PDF, TXT, MD, CSV)
- Keep file sizes under 5MB for optimal performance
- Batch upload multiple documents
- Monitor upload progress for large files

#### For Queries
- Use specific, focused queries
- Adjust `score_threshold` based on your needs
- Use `response_format` to get structured responses
- Implement caching for repeated queries

#### For Production Deployment
- Enable rate limiting
- Configure proper CORS settings
- Set up monitoring and alerting
- Implement proper error handling and logging
- Use load balancing for high availability

## Examples

### Complete Workflow Example

```bash
# 1. Check system health
curl http://localhost:8000/health

# 2. Upload a document
curl -X POST "http://localhost:8000/documents/upload" \
  -F "file=@manual.pdf" \
  -F 'metadata={"category": "documentation"}'

# 3. Wait for processing and check progress
curl http://localhost:8000/documents/upload/doc_abc123/progress

# 4. Query the knowledge base
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I configure the system?"}'

# 5. Monitor system metrics
curl http://localhost:8000/metrics
```

### Python Client Example

```python
import requests
import json

# Base URL
BASE_URL = "http://localhost:8000"

# Upload document
def upload_document(file_path, metadata=None):
    files = {'file': open(file_path, 'rb')}
    data = {'metadata': json.dumps(metadata)} if metadata else {}
    
    response = requests.post(f"{BASE_URL}/documents/upload", files=files, data=data)
    return response.json()

# Query the system
def query_system(query, **kwargs):
    data = {'query': query, **kwargs}
    response = requests.post(f"{BASE_URL}/query", json=data)
    return response.json()

# Example usage
if __name__ == "__main__":
    # Upload a document
    result = upload_document("manual.pdf", {"category": "documentation"})
    print(f"Uploaded document: {result['document_id']}")
    
    # Query the system
    answer = query_system("How do I configure the system?", top_k=5)
    print(f"Answer: {answer['answer']}")
    print(f"Sources: {len(answer['sources'])} documents found")
```

### JavaScript Client Example

```javascript
// Upload document
async function uploadDocument(file, metadata = {}) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('metadata', JSON.stringify(metadata));
    
    const response = await fetch('/documents/upload', {
        method: 'POST',
        body: formData
    });
    
    return await response.json();
}

// Query with streaming
function queryWithStreaming(query, onChunk) {
    const eventSource = new EventSource(`/query/stream?query=${encodeURIComponent(query)}`);
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        onChunk(data);
        
        if (data.type === 'end') {
            eventSource.close();
        }
    };
    
    return eventSource;
}

// Example usage
document.getElementById('upload-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    const file = document.getElementById('file-input').files[0];
    const result = await uploadDocument(file);
    console.log('Uploaded:', result);
});

document.getElementById('query-form').addEventListener('submit', (e) => {
    e.preventDefault();
    const query = document.getElementById('query-input').value;
    
    queryWithStreaming(query, (chunk) => {
        if (chunk.type === 'content') {
            document.getElementById('answer').textContent += chunk.content;
        }
    });
});
```

## Support

For additional support:

- **Documentation**: Visit `/docs` for interactive API documentation
- **Health Check**: Use `/health` to verify system status
- **Issues**: Check application logs for detailed error information
- **Community**: Join our community forum for discussions and help

---

*This documentation is generated automatically and reflects the current API version. For the most up-to-date information, always refer to the interactive documentation at `/docs`.*
