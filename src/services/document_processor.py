"""
ZeroRAG Document Processor

This module provides document processing functionality for multiple file formats
with intelligent chunking, text normalization, and metadata extraction.
"""

import logging
import hashlib
import time
from typing import Dict, Any, List, Optional, Union, Tuple
from pathlib import Path
import re
from dataclasses import dataclass
from datetime import datetime
import csv
import io

logger = logging.getLogger(__name__)


@dataclass
class DocumentChunk:
    """Document chunk container."""
    text: str
    chunk_id: str
    source_file: str
    chunk_index: int
    start_char: int
    end_char: int
    metadata: Dict[str, Any]


@dataclass
class DocumentMetadata:
    """Document metadata container."""
    file_path: str
    file_name: str
    file_size: int
    file_type: str
    encoding: str
    word_count: int
    char_count: int
    chunk_count: int
    processing_time: float
    created_at: datetime
    last_modified: datetime
    content_hash: str


class DocumentProcessor:
    """
    Document processor for multiple file formats with intelligent chunking.
    
    Features:
    - Multi-format support (TXT, CSV, MD)
    - Intelligent text chunking with overlap
    - Text cleaning and normalization
    - Metadata extraction and tracking
    - Encoding detection and handling
    - Comprehensive error handling
    """
    
    def __init__(self, config=None):
        """Initialize the document processor."""
        from config import get_config
        self.config = config or get_config()
        
        # Processing settings
        self.max_chunk_size = self.config.document.chunk_size
        self.chunk_overlap = self.config.document.chunk_overlap
        self.min_chunk_size = self.config.document.chunk_size // 4  # 25% of max chunk size
        
        # Supported file types
        self.supported_extensions = {
            '.txt': self._process_text_file,
            '.csv': self._process_csv_file,
            '.md': self._process_markdown_file,
        }
        
        # Performance tracking
        self._processing_metrics = {
            'total_documents': 0,
            'total_chunks': 0,
            'total_processing_time': 0.0,
            'errors': []
        }
    
    def process_document(self, file_path: Union[str, Path]) -> Tuple[List[DocumentChunk], DocumentMetadata]:
        """
        Process a document and return chunks with metadata.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            Tuple[List[DocumentChunk], DocumentMetadata]: Processed chunks and metadata
            
        Raises:
            ValueError: If file doesn't exist or is unsupported
            RuntimeError: If processing fails
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise ValueError(f"File does not exist: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        # Check file extension
        file_extension = file_path.suffix.lower()
        if file_extension not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {file_extension}")
        
        start_time = time.time()
        
        try:
            logger.info(f"Processing document: {file_path}")
            
            # Get file metadata
            metadata = self._extract_file_metadata(file_path)
            
            # Process file based on type
            processor_func = self.supported_extensions[file_extension]
            raw_text = processor_func(file_path)
            
            # Clean and normalize text
            cleaned_text = self._clean_and_normalize_text(raw_text)
            
            # Generate chunks
            chunks = self._generate_chunks(cleaned_text, file_path.name)
            
            # Update metadata
            metadata.word_count = len(cleaned_text.split())
            metadata.char_count = len(cleaned_text)
            metadata.chunk_count = len(chunks)
            metadata.processing_time = time.time() - start_time
            
            # Update performance metrics
            self._update_metrics(len(chunks), metadata.processing_time)
            
            logger.info(f"Successfully processed {file_path.name}: {len(chunks)} chunks in {metadata.processing_time:.2f}s")
            
            return chunks, metadata
            
        except Exception as e:
            error_msg = f"Failed to process document {file_path}: {e}"
            logger.error(error_msg)
            self._processing_metrics['errors'].append(error_msg)
            raise RuntimeError(error_msg)
    
    def _extract_file_metadata(self, file_path: Path) -> DocumentMetadata:
        """Extract file metadata."""
        stat = file_path.stat()
        
        # Calculate content hash
        content_hash = self._calculate_file_hash(file_path)
        
        return DocumentMetadata(
            file_path=str(file_path),
            file_name=file_path.name,
            file_size=stat.st_size,
            file_type=file_path.suffix.lower(),
            encoding='utf-8',  # Default, will be detected during processing
            word_count=0,  # Will be updated after processing
            char_count=0,  # Will be updated after processing
            chunk_count=0,  # Will be updated after processing
            processing_time=0.0,  # Will be updated after processing
            created_at=datetime.fromtimestamp(stat.st_ctime),
            last_modified=datetime.fromtimestamp(stat.st_mtime),
            content_hash=content_hash
        )
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file content."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _process_text_file(self, file_path: Path) -> str:
        """Process a text file."""
        try:
            # Try UTF-8 first
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        except UnicodeDecodeError:
            # Fallback to other encodings
            encodings = ['latin-1', 'cp1252', 'iso-8859-1']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        content = f.read()
                    logger.info(f"Successfully read {file_path} with {encoding} encoding")
                    return content
                except UnicodeDecodeError:
                    continue
            
            raise RuntimeError(f"Could not decode {file_path} with any supported encoding")
    
    def _process_csv_file(self, file_path: Path) -> str:
        """Process a CSV file and convert to text."""
        try:
            with open(file_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.reader(f)
                
                # Read header
                header = next(reader, [])
                if not header:
                    return ""
                
                # Convert to text format
                lines = []
                lines.append("CSV Document")
                lines.append("=" * 50)
                lines.append(f"Columns: {', '.join(header)}")
                lines.append("")
                
                for i, row in enumerate(reader, 1):
                    if not row:  # Skip empty rows
                        continue
                    
                    # Create a formatted row
                    row_text = f"Row {i}: {', '.join(str(cell) for cell in row)}"
                    lines.append(row_text)
                
                return "\n".join(lines)
                
        except Exception as e:
            logger.error(f"Failed to process CSV file {file_path}: {e}")
            raise RuntimeError(f"CSV processing failed: {e}")
    
    def _process_markdown_file(self, file_path: Path) -> str:
        """Process a markdown file and convert to plain text."""
        try:
            content = self._process_text_file(file_path)
            
            # Basic markdown to text conversion
            # Remove code blocks
            content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)
            
            # Remove inline code
            content = re.sub(r'`([^`]+)`', r'\1', content)
            
            # Remove headers (keep text)
            content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)
            
            # Remove bold/italic markers
            content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
            content = re.sub(r'\*([^*]+)\*', r'\1', content)
            
            # Remove links (keep text)
            content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
            
            # Remove images
            content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', '', content)
            
            # Clean up extra whitespace
            content = re.sub(r'\n\s*\n', '\n\n', content)
            content = content.strip()
            
            return content
            
        except Exception as e:
            logger.error(f"Failed to process markdown file {file_path}: {e}")
            raise RuntimeError(f"Markdown processing failed: {e}")
    
    def _clean_and_normalize_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove control characters except newlines and tabs
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Normalize line endings
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        
        # Remove excessive newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _generate_chunks(self, text: str, source_file: str) -> List[DocumentChunk]:
        """Generate intelligent text chunks."""
        if not text:
            return []
        
        chunks = []
        sentences = self._split_into_sentences(text)
        
        current_chunk = []
        current_length = 0
        chunk_index = 0
        start_char = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # Check if adding this sentence would exceed max chunk size
            if current_length + sentence_length > self.max_chunk_size and current_chunk:
                # Create chunk from current sentences
                chunk_text = ' '.join(current_chunk)
                chunk = self._create_chunk(
                    chunk_text, source_file, chunk_index, start_char, 
                    start_char + len(chunk_text)
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_sentences = self._get_overlap_sentences(current_chunk)
                current_chunk = overlap_sentences + [sentence]
                current_length = sum(len(s) for s in current_chunk)
                start_char = start_char + len(' '.join(overlap_sentences))
                chunk_index += 1
            else:
                current_chunk.append(sentence)
                current_length += sentence_length
        
        # Add final chunk if it meets minimum size
        if current_chunk and current_length >= self.min_chunk_size:
            chunk_text = ' '.join(current_chunk)
            chunk = self._create_chunk(
                chunk_text, source_file, chunk_index, start_char,
                start_char + len(chunk_text)
            )
            chunks.append(chunk)
        
        return chunks
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences using intelligent boundary detection."""
        # Basic sentence splitting with common patterns
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])'
        sentences = re.split(sentence_pattern, text)
        
        # Clean up sentences
        cleaned_sentences = []
        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and len(sentence) > 10:  # Minimum sentence length
                cleaned_sentences.append(sentence)
        
        return cleaned_sentences
    
    def _get_overlap_sentences(self, sentences: List[str]) -> List[str]:
        """Get sentences for overlap based on chunk overlap setting."""
        if not sentences or self.chunk_overlap <= 0:
            return []
        
        # Calculate how many sentences to include for overlap
        overlap_chars = self.chunk_overlap
        overlap_sentences = []
        
        for sentence in reversed(sentences):
            if len(' '.join(overlap_sentences + [sentence])) <= overlap_chars:
                overlap_sentences.insert(0, sentence)
            else:
                break
        
        return overlap_sentences
    
    def _create_chunk(self, text: str, source_file: str, chunk_index: int, 
                     start_char: int, end_char: int) -> DocumentChunk:
        """Create a document chunk with metadata."""
        chunk_id = f"{source_file}_{chunk_index}_{hashlib.md5(text.encode()).hexdigest()[:8]}"
        
        metadata = {
            'source_file': source_file,
            'chunk_index': chunk_index,
            'word_count': len(text.split()),
            'char_count': len(text),
            'created_at': datetime.now().isoformat()
        }
        
        return DocumentChunk(
            text=text,
            chunk_id=chunk_id,
            source_file=source_file,
            chunk_index=chunk_index,
            start_char=start_char,
            end_char=end_char,
            metadata=metadata
        )
    
    def _update_metrics(self, chunk_count: int, processing_time: float):
        """Update processing metrics."""
        self._processing_metrics['total_documents'] += 1
        self._processing_metrics['total_chunks'] += chunk_count
        self._processing_metrics['total_processing_time'] += processing_time
    
    def get_processing_metrics(self) -> Dict[str, Any]:
        """Get processing performance metrics."""
        total_docs = self._processing_metrics['total_documents']
        total_time = self._processing_metrics['total_processing_time']
        
        return {
            'total_documents': total_docs,
            'total_chunks': self._processing_metrics['total_chunks'],
            'total_processing_time': total_time,
            'average_time_per_document': total_time / total_docs if total_docs > 0 else 0,
            'average_chunks_per_document': self._processing_metrics['total_chunks'] / total_docs if total_docs > 0 else 0,
            'error_count': len(self._processing_metrics['errors']),
            'errors': self._processing_metrics['errors'][-10:]  # Last 10 errors
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on document processor."""
        return {
            'status': 'healthy',
            'supported_formats': list(self.supported_extensions.keys()),
            'processing_metrics': self.get_processing_metrics(),
            'configuration': {
                'max_chunk_size': self.max_chunk_size,
                'chunk_overlap': self.chunk_overlap,
                'min_chunk_size': self.min_chunk_size
            }
        }


# Global instance
_document_processor = None


def get_document_processor(config=None) -> DocumentProcessor:
    """Get or create document processor instance."""
    global _document_processor
    if _document_processor is None:
        _document_processor = DocumentProcessor(config)
    return _document_processor


def reset_document_processor():
    """Reset document processor instance."""
    global _document_processor
    _document_processor = None
