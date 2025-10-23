# Contributing to ZeroRAG

Thank you for your interest in contributing to ZeroRAG! This document provides guidelines and instructions for contributing to the project.

## 🌟 How Can I Contribute?

### Reporting Bugs

Before creating a bug report, please check the [existing issues](https://github.com/caprolt/zero-rag/issues) to avoid duplicates.

When reporting a bug, please include:
- **Clear description** of the issue
- **Steps to reproduce** the behavior
- **Expected behavior** vs. actual behavior
- **Environment details** (OS, Python version, etc.)
- **Logs or error messages** if applicable
- **Screenshots** if relevant

### Suggesting Enhancements

Enhancement suggestions are welcome! Please:
- Use a clear and descriptive title
- Provide a detailed description of the proposed feature
- Explain why this enhancement would be useful
- Include examples or mockups if applicable

### Pull Requests

1. **Fork the repository** and create your branch from `main`
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make your changes** following the coding standards below

3. **Test your changes** thoroughly
   ```bash
   pytest tests/
   ```

4. **Update documentation** if needed (README, docs/, etc.)

5. **Commit your changes** with clear, descriptive messages
   ```bash
   git commit -m "Add amazing feature: detailed description"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request** with a clear title and description

## 💻 Development Setup

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Git

### Setup Steps

1. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/zero-rag.git
   cd zero-rag
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

4. **Set up environment**
   ```bash
   cp env.example .env
   ```

5. **Start infrastructure services**
   ```bash
   docker-compose up -d
   ```

6. **Run tests**
   ```bash
   pytest
   ```

## 📝 Coding Standards

### Python Style Guide

- Follow [PEP 8](https://pep8.org/) style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and single-purpose
- Maximum line length: 100 characters

### Code Formatting

We recommend using `black` for code formatting:
```bash
black src/ tests/
```

### Type Hints

Use type hints for function parameters and return values:
```python
def process_document(file_path: str, chunk_size: int = 1000) -> List[str]:
    """Process a document and return chunks."""
    pass
```

### Documentation

- Add docstrings to all public functions and classes
- Update README.md for user-facing changes
- Update docs/ for technical documentation
- Include inline comments for complex logic

### Testing

- Write unit tests for new features
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage
- Use descriptive test names

Example:
```python
def test_document_processor_handles_empty_file():
    """Test that document processor gracefully handles empty files."""
    pass
```

## 🔍 Code Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, your PR will be merged
4. Your contribution will be acknowledged in release notes

## 📋 Commit Message Guidelines

Use clear, descriptive commit messages:

```
Add feature: Brief description of the feature

More detailed explanation of what was changed and why.
Include any breaking changes or important notes.
```

### Commit Types

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting, etc.)
- `refactor:` Code refactoring
- `test:` Adding or updating tests
- `chore:` Maintenance tasks

## 🎯 Areas Needing Contributions

We especially welcome contributions in these areas:

1. **PDF/DOCX Support** - Adding support for more document formats
2. **Performance Optimization** - Improving query speed and memory usage
3. **UI Enhancements** - Improving the Streamlit interface
4. **Documentation** - Expanding guides and tutorials
5. **Testing** - Increasing test coverage
6. **Cloud Deployment** - Deployment guides for various platforms

## 🤔 Questions?

If you have questions about contributing:
- Open a [GitHub Discussion](https://github.com/caprolt/zero-rag/discussions)
- Check existing [Issues](https://github.com/caprolt/zero-rag/issues)
- Review the [Documentation](docs/)

## 📜 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive experience for everyone.

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment, discrimination, or trolling
- Personal attacks or insults
- Publishing others' private information
- Other conduct that could be considered inappropriate

## 🙏 Recognition

All contributors will be:
- Listed in the project's contributors page
- Mentioned in release notes for their contributions
- Acknowledged in the README (for significant contributions)

Thank you for contributing to ZeroRAG! 🚀
