# ZeroRAG Scripts

This directory contains utility scripts for development, debugging, and maintenance of the ZeroRAG system.

## 📂 Directory Structure

### Production Scripts (Root Directory)
Located in the project root for easy access:
- **`start_app.py`** - Main application launcher (starts API + UI)
- **`run_streamlit.py`** - Standalone Streamlit UI launcher
- **`restart_llm_service.py`** - LLM service restart utility

### Utility Scripts (scripts/)
- **`check_vector_store.py`** - Inspect Qdrant vector store contents
- **`demo_streamlit_ui.py`** - Demo UI for testing
- **`load_existing_documents.py`** - Bulk document loader
- **`monitor_memory.py`** - Memory usage monitoring
- **`optimize_memory.py`** - Memory optimization utilities
- **`show_all_chunks.py`** - Display document chunks
- **`validate_config.py`** - Configuration validation

### Development Scripts (scripts/setup)
- **`setup_dev.sh`** - Linux/macOS development setup
- **`setup_dev.ps1`** - Windows PowerShell development setup

### Debug Scripts (scripts/debug/)
Development and testing scripts:
- **`debug_rag.py`** - RAG pipeline debugging
- **`inspect_documents.py`** - Document inspection tool
- **`load_documents.py`** - Test document loader
- **`test_llm_health.py`** - LLM service health tests
- **`test_query.py`** - Query testing utility
- **`test_start_app.py`** - Application startup tests

## 🚀 Usage

### Quick Start
```bash
# Start the full application
python start_app.py

# Or start components separately
python run_streamlit.py  # UI only
```

### Configuration Validation
```bash
# Validate your .env configuration
python scripts/validate_config.py
```

### Vector Store Inspection
```bash
# Check what's in your vector database
python scripts/check_vector_store.py
```

### Memory Monitoring
```bash
# Monitor system memory usage
python scripts/monitor_memory.py

# Run memory optimization
python scripts/optimize_memory.py
```

### Development Setup
```bash
# Linux/macOS
bash scripts/setup_dev.sh

# Windows PowerShell
.\scripts\setup_dev.ps1
```

### Debug Tools
```bash
# Debug RAG pipeline
python scripts/debug/debug_rag.py

# Test LLM health
python scripts/debug/test_llm_health.py

# Test queries
python scripts/debug/test_query.py
```

## 📝 Script Descriptions

### Production Scripts

#### start_app.py
The main entry point for running ZeroRAG. Starts both the FastAPI backend and Streamlit frontend.

**Features:**
- Health checks for all services
- Automatic dependency validation
- Process management
- Graceful shutdown handling

**Usage:**
```bash
python start_app.py
```

#### run_streamlit.py
Runs only the Streamlit UI. Useful when you want to run the API separately or in development.

**Usage:**
```bash
python run_streamlit.py
```

#### restart_llm_service.py
Forces a restart of the LLM service and re-detection of available providers.

**Usage:**
```bash
python restart_llm_service.py
```

### Utility Scripts

#### validate_config.py
Validates your `.env` configuration file and checks for common issues.

**Checks:**
- Required environment variables
- Service connectivity (Qdrant, Redis, Ollama)
- Model availability
- Directory permissions

#### check_vector_store.py
Inspects the Qdrant vector database to see what documents are indexed.

**Shows:**
- Number of documents
- Collection details
- Sample vectors
- Metadata

#### monitor_memory.py
Monitors system and process memory usage in real-time.

**Features:**
- Real-time memory graphs
- Process-level tracking
- Alert thresholds
- Export capabilities

## 🔧 Development

### Adding New Scripts

When adding a new script:

1. Choose the appropriate directory:
   - Root: User-facing production scripts
   - `scripts/`: Utility and maintenance scripts
   - `scripts/debug/`: Development/debug scripts

2. Follow the template:
```python
#!/usr/bin/env python3
"""
Script description

Usage:
    python script_name.py [options]
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    """Main script logic."""
    pass

if __name__ == "__main__":
    main()
```

3. Add documentation to this README
4. Make the script executable (Linux/macOS):
```bash
chmod +x scripts/your_script.py
```

## 📖 Related Documentation

- [Quick Start Guide](../docs/quick_start.md)
- [Configuration Guide](../docs/configuration.md)
- [API Documentation](../docs/api_documentation.md)
- [Deployment Guide](../docs/quick_deployment.md)

## 🐛 Troubleshooting

### Script Won't Run
```bash
# Make sure you're in the project root
cd /path/to/zero-rag

# Make sure your virtual environment is activated
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt
```

### Import Errors
Most scripts add the project root to the Python path automatically. If you still get import errors, make sure you're running the script from the correct directory.

### Permission Errors (Linux/macOS)
```bash
# Make scripts executable
chmod +x scripts/*.py
chmod +x scripts/setup/*.sh
```

## 💡 Tips

- Always run scripts from the project root directory
- Activate your virtual environment before running scripts
- Check script documentation with `python script.py --help` (if implemented)
- Use `validate_config.py` before running the main application

---

For questions or issues, see [CONTRIBUTING.md](../CONTRIBUTING.md) or open an issue.
