#!/usr/bin/env python3
"""
Quick Document Loader

This script quickly loads existing documents from the data directories into ZeroRAG.

Usage:
    python load_documents.py
"""

import sys
from pathlib import Path

# Add the scripts directory to the path
sys.path.insert(0, str(Path(__file__).parent / "scripts"))

# Import and run the document loader
from load_existing_documents import main

if __name__ == "__main__":
    main()
