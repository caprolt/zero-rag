# ZeroRAG Project Structure

```
zero-rag/
├── 📄 README.md                    # Main project documentation
├── 📄 LICENSE                      # MIT License
├── 📄 CONTRIBUTING.md              # Contribution guidelines
├── 📄 PROJECT_SUMMARY.md           # Detailed project overview
│
├── 🔧 Configuration
│   ├── .env.example                # Environment configuration template
│   ├── .gitignore                  # Git ignore rules
│   ├── .gitattributes              # Git file attributes
│   ├── docker-compose.yml          # Development infrastructure
│   ├── docker-compose.prod.yml     # Production infrastructure
│   ├── Dockerfile.prod             # Production Docker image
│   ├── requirements.txt            # Python dependencies
│   ├── requirements-windows.txt    # Windows-specific dependencies
│   ├── requirements-railway.txt    # Railway deployment dependencies
│   ├── Procfile                    # Process file for cloud deployment
│   ├── railway.json                # Railway.app configuration
│   └── nixpacks.toml              # Nixpacks build configuration
│
├── 🚀 Entry Points
│   ├── start_app.py               # Main application launcher
│   ├── start_app.bat              # Windows batch launcher
│   ├── run_streamlit.py           # Standalone UI launcher
│   ├── start_railway.py           # Railway deployment launcher
│   └── restart_llm_service.py     # LLM service restart utility
│
├── 📁 src/                        # Source code
│   ├── __init__.py
│   ├── config.py                  # Configuration management
│   ├── test_services.py           # Service integration tests
│   │
│   ├── api/                       # FastAPI backend
│   │   ├── __init__.py
│   │   ├── main.py               # API application entry point
│   │   ├── routes.py             # API route definitions
│   │   ├── models.py             # Pydantic request/response models
│   │   └── advanced_features.py  # Advanced API features
│   │
│   ├── models/                    # AI/ML models
│   │   ├── __init__.py
│   │   ├── embeddings.py         # Sentence transformer embeddings
│   │   └── llm.py                # LLM service (Ollama/HuggingFace)
│   │
│   ├── services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── document_processor.py # Document processing pipeline
│   │   ├── vector_store.py       # Qdrant vector database interface
│   │   ├── rag_pipeline.py       # RAG implementation
│   │   ├── health_monitor.py     # System health monitoring
│   │   └── service_factory.py    # Dependency injection
│   │
│   └── ui/                        # Streamlit frontend
│       ├── __init__.py
│       ├── streamlit_app.py      # Main UI application
│       └── pages/
│           └── health_page.py    # Health monitoring dashboard
│
├── 📁 tests/                      # Test suite
│   ├── test_config.py            # Configuration tests
│   ├── test_embeddings.py        # Embedding model tests
│   ├── test_llm.py               # LLM service tests
│   └── test_llm_old.py           # Legacy LLM tests
│
├── 📁 scripts/                    # Utility scripts
│   ├── README.md                 # Scripts documentation
│   ├── check_vector_store.py     # Vector database inspection
│   ├── demo_streamlit_ui.py      # Demo UI
│   ├── load_existing_documents.py # Bulk document loader
│   ├── monitor_memory.py         # Memory monitoring
│   ├── optimize_memory.py        # Memory optimization
│   ├── show_all_chunks.py        # Chunk visualization
│   ├── validate_config.py        # Configuration validator
│   ├── deploy_cloud.sh           # Cloud deployment script
│   ├── setup_dev.sh              # Linux/macOS setup
│   ├── setup_dev.ps1             # Windows setup
│   │
│   └── debug/                    # Debug utilities
│       ├── debug_rag.py          # RAG pipeline debugging
│       ├── inspect_documents.py  # Document inspection
│       ├── load_documents.py     # Test document loader
│       ├── test_llm_health.py    # LLM health tests
│       ├── test_query.py         # Query testing
│       └── test_start_app.py     # Startup tests
│
├── 📁 docs/                       # Documentation
│   ├── api_documentation.md      # API reference
│   ├── cloud_deployment_guide.md # Cloud deployment guide
│   ├── configuration.md          # Configuration guide
│   ├── error_codes.md            # Error code reference
│   ├── health_page_guide.md      # Health monitoring guide
│   ├── infrastructure_setup.md   # Infrastructure setup
│   ├── memory_optimization_guide.md # Memory optimization
│   ├── quick_start.md            # Quick start guide
│   ├── quick_deployment.md       # Quick deployment guide
│   ├── railway_deployment.md     # Railway.app deployment
│   └── plan.md                   # Development plan
│
├── 📁 planning/                   # Project planning docs
│   ├── README.md
│   ├── 00_project_overview.md
│   ├── 01_phase_1_foundation.md
│   ├── 02_phase_2_core_ai_models.md
│   ├── 03_phase_3_document_processing.md
│   ├── 04_phase_4_vector_database.md
│   ├── 05_phase_5_rag_pipeline.md
│   ├── 06_phase_6_api_development.md
│   ├── 07_phase_7_user_interface.md
│   ├── 08_phase_8_testing_qa.md
│   ├── 09_phase_9_deployment.md
│   ├── ARCHITECTURE_DIAGRAM.md
│   ├── DESIGN_DECISIONS.md
│   ├── OLLAMA_RESTART_INTEGRATION.md
│   ├── budget_rag_implementation.md
│   └── budget_rag_implementation_plan.md
│
├── 📁 data/                       # Data directory
│   ├── documents/                # Document storage
│   │   └── .gitkeep
│   ├── uploads/                  # Uploaded documents
│   │   └── .gitkeep
│   ├── processed/                # Processed documents
│   │   └── .gitkeep
│   └── cache/                    # Cache directory
│       └── .gitkeep
│
├── 📁 screenshots/                # Project screenshots
│   └── README.md                 # Screenshot guidelines
│
├── 📁 logs/                       # Application logs
│
└── 📁 .github/                    # GitHub configuration
    ├── PULL_REQUEST_TEMPLATE.md  # PR template
    └── ISSUE_TEMPLATE/
        ├── bug_report.md         # Bug report template
        └── feature_request.md    # Feature request template
```

## 📊 Quick Stats

- **Source Files**: 20+ Python modules
- **Lines of Code**: ~11,000 (in src/)
- **Documentation**: 20+ markdown files
- **Test Coverage**: Unit tests for core components
- **Configuration**: Environment-based with validation

## 🎯 Key Directories

### `/src` - Core Application
The heart of ZeroRAG, containing all production code:
- **API Layer**: FastAPI endpoints and routing
- **Model Layer**: AI/ML model interfaces
- **Service Layer**: Business logic and orchestration
- **UI Layer**: Streamlit web interface

### `/tests` - Test Suite
Comprehensive testing infrastructure:
- Unit tests for core components
- Integration tests for services
- Configuration validation tests

### `/scripts` - Utilities
Development and maintenance tools:
- Configuration validation
- Vector store inspection
- Memory monitoring
- Debug utilities

### `/docs` - Documentation
Complete project documentation:
- Setup and deployment guides
- API documentation
- Configuration reference
- Troubleshooting guides

### `/planning` - Project Planning
Development planning and architecture:
- Phase-by-phase development plan
- Architecture diagrams
- Design decisions
- Implementation plans

## 🔄 Data Flow

```
User Upload → Document Processor → Vector Embeddings → Qdrant
                                                           ↓
User Query → Embedding → Similarity Search → Context Retrieval → LLM → Response
```

## 🚀 Getting Started

See [README.md](README.md) for installation and usage instructions.

## 📝 Development Workflow

1. **Configuration**: Copy `.env.example` to `.env`
2. **Infrastructure**: `docker-compose up -d`
3. **Validation**: `python scripts/validate_config.py`
4. **Start App**: `python start_app.py`
5. **Test**: `pytest tests/`

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

---

Last updated: October 2025
