# ZeroRAG System Architecture Diagram

## High-Level Architecture Overview

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Streamlit UI<br/>Port 8501]
        API_DOC[API Documentation<br/>OpenAPI/Swagger]
    end
    
    subgraph "API Gateway Layer"
        API[FastAPI REST API<br/>Port 8000]
        CORS[CORS Middleware]
        HEALTH[Health Check Endpoints]
        METRICS[Metrics & Monitoring]
    end
    
    subgraph "Service Layer"
        SF[Service Factory<br/>Singleton Pattern]
        RAG[RAG Pipeline Service]
        DOC_PROC[Document Processor]
        EMBED[Embedding Service]
        LLM[LLM Service]
        VS[Vector Store Service]
        HM[Health Monitor]
    end
    
    subgraph "AI/ML Models"
        ST[SentenceTransformers<br/>all-MiniLM-L6-v2]
        OLLAMA[Ollama LLM<br/>llama3.2:1b]
        HF[HuggingFace Fallback]
    end
    
    subgraph "Data Storage Layer"
        QDRANT[(Qdrant Vector DB<br/>Port 6333)]
        REDIS[(Redis Cache<br/>Port 6379)]
        FILES[Local File System<br/>Documents & Uploads]
        LOGS[Log Files<br/>JSON Format]
    end
    
    subgraph "Infrastructure Layer"
        DOCKER[Docker Compose<br/>Infrastructure]
        RAILWAY[Railway Cloud<br/>Deployment]
        HEALTH_CHECK[Health Checks<br/>& Monitoring]
    end
    
    subgraph "Configuration Layer"
        CONFIG[Pydantic Config<br/>Environment Variables]
        ENV[.env Files<br/>Environment Settings]
    end
    
    %% Frontend connections
    UI --> API
    API_DOC --> API
    
    %% API Gateway connections
    API --> CORS
    API --> HEALTH
    API --> METRICS
    API --> SF
    
    %% Service Layer connections
    SF --> RAG
    SF --> DOC_PROC
    SF --> EMBED
    SF --> LLM
    SF --> VS
    SF --> HM
    
    RAG --> EMBED
    RAG --> LLM
    RAG --> VS
    DOC_PROC --> EMBED
    DOC_PROC --> VS
    
    %% AI/ML Model connections
    EMBED --> ST
    LLM --> OLLAMA
    LLM --> HF
    
    %% Data Storage connections
    VS --> QDRANT
    API --> REDIS
    DOC_PROC --> FILES
    HM --> LOGS
    
    %% Infrastructure connections
    DOCKER --> QDRANT
    DOCKER --> REDIS
    RAILWAY --> API
    HEALTH_CHECK --> HEALTH
    
    %% Configuration connections
    CONFIG --> SF
    CONFIG --> ENV
    
    %% Styling
    classDef frontend fill:#e1f5fe
    classDef api fill:#f3e5f5
    classDef service fill:#e8f5e8
    classDef ai fill:#fff3e0
    classDef storage fill:#fce4ec
    classDef infra fill:#f1f8e9
    classDef config fill:#fff8e1
    
    class UI,API_DOC frontend
    class API,CORS,HEALTH,METRICS api
    class SF,RAG,DOC_PROC,EMBED,LLM,VS,HM service
    class ST,OLLAMA,HF ai
    class QDRANT,REDIS,FILES,LOGS storage
    class DOCKER,RAILWAY,HEALTH_CHECK infra
    class CONFIG,ENV config
```

## Data Flow Architecture

```mermaid
sequenceDiagram
    participant User
    participant Streamlit as Streamlit UI
    participant FastAPI as FastAPI Backend
    participant RAG as RAG Pipeline
    participant Embed as Embedding Service
    participant Vector as Vector Store
    participant LLM as LLM Service
    participant Qdrant as Qdrant DB
    
    Note over User,Qdrant: Document Upload Flow
    User->>Streamlit: Upload Document
    Streamlit->>FastAPI: POST /documents/upload
    FastAPI->>RAG: Process Document
    RAG->>Embed: Generate Embeddings
    Embed->>Vector: Store Embeddings
    Vector->>Qdrant: Save Vectors
    Qdrant-->>Vector: Confirm Storage
    Vector-->>RAG: Success Response
    RAG-->>FastAPI: Processing Complete
    FastAPI-->>Streamlit: Upload Success
    Streamlit-->>User: Show Success Message
    
    Note over User,Qdrant: Query Processing Flow
    User->>Streamlit: Ask Question
    Streamlit->>FastAPI: POST /query
    FastAPI->>RAG: Process Query
    RAG->>Embed: Generate Query Embedding
    RAG->>Vector: Search Similar Documents
    Vector->>Qdrant: Vector Search
    Qdrant-->>Vector: Return Results
    Vector-->>RAG: Document Chunks
    RAG->>LLM: Generate Response with Context
    LLM-->>RAG: Generated Answer
    RAG-->>FastAPI: RAG Response
    FastAPI-->>Streamlit: Stream Response
    Streamlit-->>User: Display Answer + Sources
```

## Component Layer Architecture

```mermaid
graph LR
    subgraph "Presentation Layer"
        A[Streamlit UI]
        B[API Documentation]
    end
    
    subgraph "API Layer"
        C[FastAPI Routes]
        D[Middleware Stack]
        E[Error Handlers]
    end
    
    subgraph "Business Logic Layer"
        F[RAG Pipeline]
        G[Document Processor]
        H[Prompt Engine]
        I[Service Factory]
    end
    
    subgraph "Integration Layer"
        J[Embedding Service]
        K[LLM Service] 
        L[Vector Store Service]
        M[Health Monitor]
    end
    
    subgraph "Data Access Layer"
        N[Qdrant Client]
        O[Redis Client]
        P[File System]
        Q[Configuration]
    end
    
    subgraph "External Services"
        R[SentenceTransformers]
        S[Ollama]
        T[HuggingFace]
    end
    
    A --> C
    B --> C
    C --> D
    D --> E
    C --> F
    F --> G
    F --> H
    F --> I
    I --> J
    I --> K
    I --> L
    I --> M
    J --> N
    K --> N
    L --> N
    M --> O
    G --> P
    I --> Q
    J --> R
    K --> S
    K --> T
```

## Service Dependency Graph

```mermaid
graph TD
    subgraph "Core Services"
        SF[Service Factory<br/>Singleton]
        RAG[RAG Pipeline]
        DP[Document Processor]
        VS[Vector Store]
        ES[Embedding Service]
        LLM[LLM Service]
        HM[Health Monitor]
    end
    
    subgraph "External Dependencies"
        QDRANT[(Qdrant)]
        REDIS[(Redis)]
        MODELS[AI Models]
        FS[File System]
    end
    
    SF --> RAG
    SF --> DP
    SF --> VS
    SF --> ES
    SF --> LLM
    SF --> HM
    
    RAG --> ES
    RAG --> LLM
    RAG --> VS
    
    DP --> ES
    DP --> VS
    DP --> FS
    
    VS --> QDRANT
    ES --> MODELS
    LLM --> MODELS
    HM --> REDIS
    
    %% Dependency relationships
    RAG -.-> DP
    VS -.-> ES
    
    classDef core fill:#e3f2fd
    classDef external fill:#fff3e0
    
    class SF,RAG,DP,VS,ES,LLM,HM core
    class QDRANT,REDIS,MODELS,FS external
```

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development Environment"
        DEV_API[FastAPI Dev Server<br/>Hot Reload]
        DEV_UI[Streamlit Dev Server<br/>Hot Reload]
        DEV_DOCKER[Docker Compose<br/>Local Infrastructure]
    end
    
    subgraph "Production Environment"
        PROD_API[Uvicorn ASGI Server<br/>Multi-worker]
        PROD_UI[Streamlit Production<br/>Single Process]
        PROD_DOCKER[Docker Production<br/>Optimized Images]
    end
    
    subgraph "Cloud Deployment (Railway)"
        RAILWAY_API[Railway App Instance<br/>Auto-scaling]
        RAILWAY_DB[Railway Database<br/>Managed Services]
        RAILWAY_REDIS[Railway Redis<br/>Managed Cache]
    end
    
    subgraph "Monitoring & Observability"
        HEALTH[Health Endpoints]
        METRICS[Performance Metrics]
        LOGS[Structured Logging]
        ALERTS[Error Tracking]
    end
    
    DEV_API --> DEV_DOCKER
    DEV_UI --> DEV_API
    
    PROD_API --> PROD_DOCKER
    PROD_UI --> PROD_API
    
    RAILWAY_API --> RAILWAY_DB
    RAILWAY_API --> RAILWAY_REDIS
    
    PROD_API --> HEALTH
    PROD_API --> METRICS
    PROD_API --> LOGS
    LOGS --> ALERTS
    
    classDef dev fill:#e8f5e8
    classDef prod fill:#fff3e0
    classDef cloud fill:#e3f2fd
    classDef monitor fill:#fce4ec
    
    class DEV_API,DEV_UI,DEV_DOCKER dev
    class PROD_API,PROD_UI,PROD_DOCKER prod
    class RAILWAY_API,RAILWAY_DB,RAILWAY_REDIS cloud
    class HEALTH,METRICS,LOGS,ALERTS monitor
```

## Security Architecture

```mermaid
graph LR
    subgraph "Security Layers"
        A[Input Validation<br/>Pydantic Models]
        B[File Validation<br/>Security Checks]
        C[CORS Configuration<br/>Origin Control]
        D[Rate Limiting<br/>API Protection]
        E[Authentication<br/>API Keys Optional]
        F[Content Filtering<br/>Safety Checks]
    end
    
    subgraph "Data Protection"
        G[Local Storage<br/>No External Data]
        H[Vector Encryption<br/>At Rest]
        I[Session Management<br/>Redis Cache]
        J[Secure Headers<br/>HTTPS Ready]
    end
    
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    
    G --> H
    H --> I
    I --> J
    
    classDef security fill:#ffebee
    classDef data fill:#e8f5e8
    
    class A,B,C,D,E,F security
    class G,H,I,J data
```

## Performance & Scalability Architecture

```mermaid
graph TB
    subgraph "Performance Optimizations"
        CACHE[Redis Caching<br/>Query Results]
        BATCH[Batch Processing<br/>Document Chunks]
        STREAM[Streaming Responses<br/>Real-time Output]
        POOL[Connection Pooling<br/>Database Connections]
    end
    
    subgraph "Scalability Features"
        WORKER[Multi-worker Setup<br/>Uvicorn Workers]
        ASYNC[Async Processing<br/>FastAPI Async/Await]
        QUEUE[Background Tasks<br/>Document Processing]
        HEALTH[Health Monitoring<br/>Auto-recovery]
    end
    
    subgraph "Resource Management"
        MEMORY[Memory Monitoring<br/>Threshold Management]
        GC[Garbage Collection<br/>Periodic Cleanup]
        LIMITS[Resource Limits<br/>File Size/Context]
        METRICS[Performance Metrics<br/>Real-time Monitoring]
    end
    
    CACHE --> WORKER
    BATCH --> ASYNC
    STREAM --> QUEUE
    POOL --> HEALTH
    
    WORKER --> MEMORY
    ASYNC --> GC
    QUEUE --> LIMITS
    HEALTH --> METRICS
    
    classDef perf fill:#e1f5fe
    classDef scale fill:#f3e5f5
    classDef resource fill:#e8f5e8
    
    class CACHE,BATCH,STREAM,POOL perf
    class WORKER,ASYNC,QUEUE,HEALTH scale
    class MEMORY,GC,LIMITS,METRICS resource
```

## Technology Stack Architecture

```mermaid
mindmap
  root((ZeroRAG<br/>Technology Stack))
    Frontend
      Streamlit
        Interactive UI
        Real-time Updates
        File Upload
        Chat Interface
      OpenAPI
        Auto-generated Docs
        Interactive Testing
        Schema Validation
    Backend
      FastAPI
        Async/Await Support
        Automatic OpenAPI
        Type Validation
        Dependency Injection
      Uvicorn
        ASGI Server
        Multi-worker Support
        Hot Reload
        Production Ready
    AI/ML
      SentenceTransformers
        all-MiniLM-L6-v2
        384-dim Embeddings
        Fast Inference
        CPU Optimized
      Ollama
        Local LLM Hosting
        llama3.2:1b Model
        No API Costs
        Privacy Focused
      HuggingFace
        Fallback Models
        Transformers Library
        Model Hub Access
        Pipeline Support
    Data Storage
      Qdrant
        Vector Database
        Similarity Search
        HNSW Indexing
        RESTful API
      Redis
        Caching Layer
        Session Storage
        Fast Access
        Memory Efficient
      Local Files
        Document Storage
        Upload Processing
        File Validation
        Organized Structure
    Infrastructure
      Docker
        Containerization
        Service Isolation
        Easy Deployment
        Development Parity
      Railway
        Cloud Deployment
        Auto-scaling
        CI/CD Pipeline
        Managed Services
      Nixpacks
        Build System
        Dependency Resolution
        Optimization
        Cloud Native
```

## Configuration & Environment Architecture

```mermaid
graph TB
    subgraph "Configuration Management"
        A[Pydantic Settings<br/>Type Validation]
        B[Environment Variables<br/>.env Files]
        C[Default Values<br/>Fallback Configuration]
        D[Validation Rules<br/>Schema Enforcement]
    end
    
    subgraph "Environment Separation"
        E[Development Config<br/>Debug + Hot Reload]
        F[Production Config<br/>Optimized Settings]
        G[Cloud Config<br/>Railway Environment]
        H[Test Config<br/>Test Isolation]
    end
    
    subgraph "Configuration Categories"
        I[Database Config<br/>Qdrant + Redis]
        J[AI Model Config<br/>LLM + Embeddings]
        K[API Config<br/>Server + Security]
        L[Document Config<br/>Processing Rules]
        M[RAG Config<br/>Pipeline Settings]
        N[Performance Config<br/>Optimization]
        O[Logging Config<br/>Monitoring]
    end
    
    A --> B
    B --> C
    C --> D
    
    D --> E
    D --> F
    D --> G
    D --> H
    
    E --> I
    E --> J
    E --> K
    F --> L
    F --> M
    G --> N
    H --> O
    
    classDef config fill:#fff8e1
    classDef env fill:#f3e5f5
    classDef category fill:#e8f5e8
    
    class A,B,C,D config
    class E,F,G,H env
    class I,J,K,L,M,N,O category
```

## Error Handling & Recovery Architecture

```mermaid
graph TD
    subgraph "Error Detection"
        A[Service Health Checks<br/>Continuous Monitoring]
        B[Exception Handling<br/>Try/Catch Blocks]
        C[Validation Errors<br/>Input Validation]
        D[Resource Monitoring<br/>Memory/CPU Limits]
    end
    
    subgraph "Error Recovery"
        E[Service Restart<br/>Automatic Recovery]
        F[Graceful Degradation<br/>Fallback Options]
        G[Circuit Breaker<br/>Failure Prevention]
        H[Retry Mechanisms<br/>Exponential Backoff]
    end
    
    subgraph "Error Reporting"
        I[Structured Logging<br/>JSON Format]
        J[Error Responses<br/>Standard Format]
        K[Health Endpoints<br/>Status Reporting]
        L[Metrics Collection<br/>Performance Data]
    end
    
    A --> E
    B --> F
    C --> G
    D --> H
    
    E --> I
    F --> J
    G --> K
    H --> L
    
    classDef detection fill:#ffebee
    classDef recovery fill:#e8f5e8
    classDef reporting fill:#e3f2fd
    
    class A,B,C,D detection
    class E,F,G,H recovery
    class I,J,K,L reporting
```

## API Design Architecture

```mermaid
graph LR
    subgraph "REST API Design"
        A[RESTful Endpoints<br/>Standard HTTP Methods]
        B[Resource-based URLs<br/>Logical Hierarchy]
        C[JSON Request/Response<br/>Standard Format]
        D[HTTP Status Codes<br/>Proper Usage]
    end
    
    subgraph "Advanced Features"
        E[Streaming Responses<br/>Server-Sent Events]
        F[File Upload<br/>Multipart Form Data]
        G[Query Parameters<br/>Filtering/Pagination]
        H[Request Validation<br/>Pydantic Models]
    end
    
    subgraph "Documentation"
        I[OpenAPI Schema<br/>Auto-generated]
        J[Interactive Docs<br/>Swagger UI]
        K[API Examples<br/>Code Samples]
        L[Error Documentation<br/>Response Codes]
    end
    
    A --> E
    B --> F
    C --> G
    D --> H
    
    E --> I
    F --> J
    G --> K
    H --> L
    
    classDef rest fill:#e1f5fe
    classDef advanced fill:#f3e5f5
    classDef docs fill:#e8f5e8
    
    class A,B,C,D rest
    class E,F,G,H advanced
    class I,J,K,L docs
```

## Key Architectural Principles

### 1. **Modular Design**
- Service-oriented architecture with clear separation of concerns
- Pluggable components with well-defined interfaces
- Factory pattern for service management and dependency injection

### 2. **Scalability & Performance**
- Async/await throughout the application for non-blocking operations
- Connection pooling and caching for improved performance
- Streaming responses for real-time user experience
- Resource monitoring and automatic cleanup

### 3. **Reliability & Resilience**
- Comprehensive health monitoring and error recovery
- Graceful degradation when services are unavailable
- Automatic service restart and circuit breaker patterns
- Structured logging and error tracking

### 4. **Security & Privacy**
- Local deployment with no external data sharing
- Input validation and file security checks
- CORS configuration and optional API key authentication
- Content filtering and safety validation

### 5. **Developer Experience**
- Auto-generated API documentation with interactive testing
- Type safety with Pydantic models throughout
- Hot reload in development with production optimization
- Comprehensive configuration management

### 6. **Zero-Cost Architecture**
- Entirely built with free and open-source components
- Local AI models with no API costs
- Self-hosted infrastructure with minimal resource requirements
- Optional cloud deployment with cost-effective services