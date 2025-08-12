# ZeroRAG API Error Codes

This document provides comprehensive information about all error codes returned by the ZeroRAG API, including descriptions, causes, and troubleshooting steps.

## Error Response Format

All API errors follow a standardized format:

```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "timestamp": 1703123456.789,
  "request_id": "req_abc123def456"
}
```

## HTTP Status Codes

### 2xx Success
- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **204 No Content**: Request successful, no content returned

### 4xx Client Errors
- **400 Bad Request**: Invalid request format or parameters
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Access denied
- **404 Not Found**: Resource not found
- **413 Payload Too Large**: Request body too large
- **422 Validation Error**: Request validation failed
- **429 Too Many Requests**: Rate limit exceeded

### 5xx Server Errors
- **500 Internal Server Error**: Unexpected server error
- **502 Bad Gateway**: Upstream service error
- **503 Service Unavailable**: Service temporarily unavailable

## Detailed Error Codes

### File Upload Errors

#### `FILE_TOO_LARGE`
- **HTTP Status**: 413
- **Description**: File size exceeds maximum allowed limit
- **Causes**:
  - File larger than 10MB limit
  - Configuration allows smaller limit
- **Solutions**:
  - Reduce file size to under 10MB
  - Split large documents into smaller files
  - Compress PDF files before upload
  - Check configuration for custom limits

#### `UNSUPPORTED_FORMAT`
- **HTTP Status**: 400
- **Description**: File format not supported
- **Causes**:
  - File extension not in supported list
  - Content type mismatch
  - Corrupted file header
- **Solutions**:
  - Convert to supported format (PDF, TXT, MD, CSV)
  - Check file integrity
  - Verify file extension matches content

#### `MALICIOUS_FILE_DETECTED`
- **HTTP Status**: 400
- **Description**: File appears to be malicious or suspicious
- **Causes**:
  - Suspicious file extension
  - Double extension detected
  - Known malicious patterns
- **Solutions**:
  - Verify file source
  - Scan file with antivirus
  - Use different file if safe

#### `FILE_VALIDATION_FAILED`
- **HTTP Status**: 400
- **Description**: File validation checks failed
- **Causes**:
  - Invalid file structure
  - Corrupted content
  - Unsupported encoding
- **Solutions**:
  - Check file integrity
  - Re-save file in supported format
  - Verify file encoding (UTF-8 recommended)

#### `UPLOAD_IN_PROGRESS`
- **HTTP Status**: 409
- **Description**: File upload already in progress
- **Causes**:
  - Duplicate upload request
  - Previous upload not completed
- **Solutions**:
  - Wait for current upload to complete
  - Check upload progress endpoint
  - Cancel previous upload if needed

### Query Processing Errors

#### `INVALID_QUERY`
- **HTTP Status**: 400
- **Description**: Query format or content is invalid
- **Causes**:
  - Query too short (< 1 character)
  - Query too long (> 1000 characters)
  - Invalid characters
  - Empty query
- **Solutions**:
  - Ensure query is 1-1000 characters
  - Remove invalid characters
  - Provide meaningful query content

#### `NO_DOCUMENTS_FOUND`
- **HTTP Status**: 404
- **Description**: No documents available for querying
- **Causes**:
  - No documents uploaded
  - All documents deleted
  - Documents not processed
- **Solutions**:
  - Upload documents first
  - Check document processing status
  - Verify document storage

#### `INSUFFICIENT_CONTEXT`
- **HTTP Status**: 400
- **Description**: Not enough relevant context found
- **Causes**:
  - Score threshold too high
  - Query too specific
  - Limited document content
- **Solutions**:
  - Lower score_threshold parameter
  - Broaden query scope
  - Add more relevant documents

#### `CONTEXT_TOO_LARGE`
- **HTTP Status**: 400
- **Description**: Retrieved context exceeds maximum size
- **Causes**:
  - max_context_length too high
  - Too many documents retrieved
  - Large document chunks
- **Solutions**:
  - Reduce max_context_length
  - Lower top_k parameter
  - Adjust chunking settings

### Service Errors

#### `SERVICE_UNAVAILABLE`
- **HTTP Status**: 503
- **Description**: Required service is not available
- **Causes**:
  - Service crashed
  - Service not started
  - Resource exhaustion
  - Network issues
- **Solutions**:
  - Check service health at `/health`
  - Restart application
  - Check system resources
  - Review service logs

#### `DOCUMENT_PROCESSOR_ERROR`
- **HTTP Status**: 502
- **Description**: Document processing service error
- **Causes**:
  - Processing queue full
  - Memory exhaustion
  - File parsing errors
  - Embedding service down
- **Solutions**:
  - Check processor health
  - Clear processing queue
  - Restart document processor
  - Check memory usage

#### `VECTOR_STORE_ERROR`
- **HTTP Status**: 502
- **Description**: Vector database error
- **Causes**:
  - Database connection lost
  - Index corruption
  - Disk space full
  - Memory issues
- **Solutions**:
  - Check vector store health
  - Verify disk space
  - Rebuild index if needed
  - Restart vector store service

#### `LLM_SERVICE_ERROR`
- **HTTP Status**: 502
- **Description**: Language model service error
- **Causes**:
  - Model not loaded
  - GPU memory full
  - Model file corrupted
  - Service timeout
- **Solutions**:
  - Check LLM service health
  - Restart LLM service
  - Verify model files
  - Check GPU memory

### Rate Limiting Errors

#### `RATE_LIMIT_EXCEEDED`
- **HTTP Status**: 429
- **Description**: Too many requests in time period
- **Causes**:
  - Exceeded rate limit
  - Burst requests
  - Multiple clients
- **Solutions**:
  - Wait before retrying
  - Implement exponential backoff
  - Reduce request frequency
  - Check rate limit headers

#### `UPLOAD_RATE_LIMIT_EXCEEDED`
- **HTTP Status**: 429
- **Description**: Too many upload requests
- **Causes**:
  - Multiple file uploads
  - Large file uploads
  - Upload endpoint abuse
- **Solutions**:
  - Wait between uploads
  - Batch uploads
  - Use smaller files
  - Implement upload queue

### Validation Errors

#### `VALIDATION_ERROR`
- **HTTP Status**: 422
- **Description**: Request validation failed
- **Causes**:
  - Invalid parameter values
  - Missing required fields
  - Type mismatches
  - Constraint violations
- **Solutions**:
  - Check parameter values
  - Provide required fields
  - Verify data types
  - Review API documentation

#### `INVALID_PARAMETER`
- **HTTP Status**: 400
- **Description**: Invalid parameter value
- **Causes**:
  - Out of range values
  - Invalid formats
  - Unsupported options
- **Solutions**:
  - Check parameter ranges
  - Use supported formats
  - Review parameter documentation

### Authentication & Authorization

#### `UNAUTHORIZED`
- **HTTP Status**: 401
- **Description**: Authentication required
- **Causes**:
  - Missing API key
  - Invalid credentials
  - Expired token
- **Solutions**:
  - Provide valid API key
  - Check credentials
  - Refresh token if needed

#### `FORBIDDEN`
- **HTTP Status**: 403
- **Description**: Access denied
- **Causes**:
  - Insufficient permissions
  - IP blocked
  - Resource access denied
- **Solutions**:
  - Check permissions
  - Verify IP whitelist
  - Contact administrator

### Resource Errors

#### `RESOURCE_NOT_FOUND`
- **HTTP Status**: 404
- **Description**: Requested resource not found
- **Causes**:
  - Invalid document ID
  - Deleted resource
  - Wrong endpoint
- **Solutions**:
  - Check resource ID
  - Verify resource exists
  - Use correct endpoint

#### `RESOURCE_ALREADY_EXISTS`
- **HTTP Status**: 409
- **Description**: Resource already exists
- **Causes**:
  - Duplicate upload
  - Existing document
  - Conflict in creation
- **Solutions**:
  - Use different identifier
  - Update existing resource
  - Handle conflict appropriately

### Streaming Errors

#### `STREAMING_CONNECTION_ERROR`
- **HTTP Status**: 500
- **Description**: Streaming connection failed
- **Causes**:
  - Connection timeout
  - Network issues
  - Server overload
- **Solutions**:
  - Check network stability
  - Implement reconnection
  - Reduce server load

#### `STREAMING_TIMEOUT`
- **HTTP Status**: 408
- **Description**: Streaming request timeout
- **Causes**:
  - Long processing time
  - Network latency
  - Server overload
- **Solutions**:
  - Increase timeout settings
  - Optimize query parameters
  - Check server performance

## Error Handling Best Practices

### Client-Side Error Handling

```python
import requests
from requests.exceptions import RequestException

def api_request(url, method='GET', **kwargs):
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            # Rate limit exceeded
            retry_after = int(e.response.headers.get('Retry-After', 60))
            print(f"Rate limited. Retry after {retry_after} seconds")
        elif e.response.status_code == 413:
            # File too large
            print("File size exceeds limit. Reduce file size.")
        elif e.response.status_code == 503:
            # Service unavailable
            print("Service temporarily unavailable. Retry later.")
        else:
            error_data = e.response.json()
            print(f"Error: {error_data.get('error')}")
            print(f"Detail: {error_data.get('detail')}")
    except RequestException as e:
        print(f"Network error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
```

### JavaScript Error Handling

```javascript
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, options);
        
        if (!response.ok) {
            const errorData = await response.json();
            
            switch (response.status) {
                case 429:
                    const retryAfter = response.headers.get('Retry-After') || 60;
                    console.log(`Rate limited. Retry after ${retryAfter} seconds`);
                    break;
                case 413:
                    console.log('File size exceeds limit. Reduce file size.');
                    break;
                case 503:
                    console.log('Service temporarily unavailable. Retry later.');
                    break;
                default:
                    console.log(`Error: ${errorData.error}`);
                    console.log(`Detail: ${errorData.detail}`);
            }
            
            throw new Error(errorData.error);
        }
        
        return await response.json();
    } catch (error) {
        if (error.name === 'TypeError') {
            console.log('Network error. Check connection.');
        } else {
            console.log(`Request failed: ${error.message}`);
        }
        throw error;
    }
}
```

### Retry Logic

```python
import time
import random

def api_request_with_retry(url, max_retries=3, **kwargs):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                # Rate limit - exponential backoff
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Rate limited. Waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            elif e.response.status_code == 503:
                # Service unavailable - exponential backoff
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Service unavailable. Waiting {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                # Don't retry other errors
                raise
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            wait_time = (2 ** attempt) + random.uniform(0, 1)
            print(f"Request failed. Retrying in {wait_time:.2f} seconds...")
            time.sleep(wait_time)
    
    raise Exception("Max retries exceeded")
```

## Monitoring and Debugging

### Error Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def log_api_error(error_response, request_info=None):
    logger.error(f"API Error: {error_response.get('error')}")
    logger.error(f"Detail: {error_response.get('detail')}")
    logger.error(f"Request ID: {error_response.get('request_id')}")
    if request_info:
        logger.error(f"Request: {request_info}")
```

### Health Monitoring

```python
def monitor_api_health(base_url):
    try:
        response = requests.get(f"{base_url}/health")
        health_data = response.json()
        
        if health_data['status'] == 'healthy':
            print("✅ API is healthy")
        elif health_data['status'] == 'degraded':
            print("⚠️ API is degraded")
            for service, info in health_data['services'].items():
                if info['status'] != 'healthy':
                    print(f"  - {service}: {info['status']}")
        else:
            print("❌ API is unhealthy")
            
        return health_data
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return None
```

## Getting Help

If you encounter errors not covered in this documentation:

1. **Check the logs**: Review application logs for detailed error information
2. **Health check**: Use `/health` endpoint to verify system status
3. **Interactive docs**: Visit `/docs` for API testing and examples
4. **Community support**: Join our community forum for help
5. **Issue reporting**: Report bugs with error details and request IDs

---

*This error documentation is maintained with the API. For the most current information, always refer to the interactive documentation at `/docs`.*
