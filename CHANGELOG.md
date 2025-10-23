# Changelog

All notable changes to the ZeroRAG project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Portfolio-Ready Cleanup (October 2025)

#### Added
- **LICENSE** - MIT License file
- **CONTRIBUTING.md** - Comprehensive contribution guidelines
- **PROJECT_SUMMARY.md** - Detailed project overview for portfolio/resume
- **PROJECT_STRUCTURE.md** - Visual project structure documentation
- **.gitattributes** - Git line ending configuration
- **.github/** directory with templates:
  - Issue templates (bug report, feature request)
  - Pull request template
- **screenshots/** directory with README for visual documentation
- **scripts/README.md** - Comprehensive scripts documentation
- **scripts/debug/** directory for development/debug scripts
- Project highlights section to README
- Data directory .gitkeep files to preserve structure
- Portfolio-focused badges and statistics

#### Changed
- **README.md** - Updated with correct GitHub URLs (caprolt/zero-rag)
- **README.md** - Enhanced with project highlights and portfolio information
- **CONTRIBUTING.md** reference instead of inline steps
- **.gitignore** - Added .env, development artifacts, and test files
- **env.example** - Updated OLLAMA_MODEL from gpt-oss:20b to llama3.2:1b
- **.env** - Updated OLLAMA_MODEL to match documentation
- **.env.example** - Fixed incomplete file with full configuration template

#### Removed
- Moved planning documents from root to `planning/` directory:
  - ARCHITECTURE_DIAGRAM.md
  - DESIGN_DECISIONS.md
  - OLLAMA_RESTART_INTEGRATION.md
  - budget_rag_implementation.md
  - budget_rag_implementation_plan.md
- Moved development/test scripts from root to `scripts/debug/`:
  - debug_rag.py
  - inspect_documents.py
  - load_documents.py
  - test_llm_health.py
  - test_query.py
  - test_start_app.py
- Cleared test files from `data/uploads/` directory

#### Project Structure Improvements
- Better organization with clear separation of concerns
- Professional documentation structure
- Ready for GitHub showcasing and job applications
- Comprehensive contribution workflow
- Proper git configuration for collaboration

---

## Version History

### [1.0.0] - 2025-09-21

#### Initial Release
- Full-stack RAG system implementation
- FastAPI backend with RESTful API
- Streamlit web interface
- Qdrant vector database integration
- Redis caching layer
- Ollama/HuggingFace LLM support
- Document processing pipeline
- Semantic search capabilities
- Health monitoring system
- Docker containerization
- Cloud deployment support (Railway, etc.)

#### Features
- Document upload (TXT, CSV, MD)
- Intelligent Q&A with context
- Real-time streaming responses
- Multi-provider LLM support
- Comprehensive error handling
- Logging and monitoring
- Configuration management
- Development and production modes

#### Documentation
- Quick start guide
- API documentation
- Configuration guide
- Deployment guides
- Troubleshooting guide
- Development workflow documentation

---

## Future Roadmap

### Planned Features
- [ ] PDF and DOCX document support
- [ ] Multi-user authentication
- [ ] Advanced analytics dashboard
- [ ] Fine-tuning capabilities
- [ ] Mobile application
- [ ] Cloud storage integrations (Dropbox, Google Drive)
- [ ] Collaborative document annotations
- [ ] REST API authentication with API keys
- [ ] Webhook support for document updates
- [ ] Batch document processing
- [ ] Export functionality (chat history, search results)

### Improvements
- [ ] Enhanced UI/UX design
- [ ] Performance optimization for large document sets
- [ ] Better caching strategies
- [ ] Expanded test coverage
- [ ] CI/CD pipeline setup
- [ ] Automated dependency updates
- [ ] Security audit and hardening
- [ ] Load testing and benchmarks
- [ ] Internationalization (i18n)

---

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to contribute to this project.

## Links

- **Repository**: https://github.com/caprolt/zero-rag
- **Issues**: https://github.com/caprolt/zero-rag/issues
- **Discussions**: https://github.com/caprolt/zero-rag/discussions

---

[Unreleased]: https://github.com/caprolt/zero-rag/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/caprolt/zero-rag/releases/tag/v1.0.0
