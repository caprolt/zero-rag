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
    """Document metadata container with enhanced information."""
    # File information
    file_path: str
    file_name: str
    file_size: int
    file_type: str
    encoding: str
    
    # Content statistics
    word_count: int
    char_count: int
    chunk_count: int
    sentence_count: int
    paragraph_count: int
    line_count: int
    
    # Processing information
    processing_time: float
    processing_status: str  # 'pending', 'processing', 'completed', 'failed'
    
    # Timestamps
    created_at: datetime
    last_modified: datetime
    content_hash: str
    
    # Content analysis
    content_type: str  # 'text', 'structured', 'mixed'
    
    # Validation results
    is_valid: bool = True
    
    # Optional fields with defaults
    error_message: Optional[str] = None
    processed_at: Optional[datetime] = None
    language_detected: Optional[str] = None
    has_tables: bool = False
    has_images: bool = False
    has_links: bool = False
    validation_errors: List[str] = None
    
    def __post_init__(self):
        if self.validation_errors is None:
            self.validation_errors = []


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
        try:
            from ..config import get_config
        except ImportError:
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
    
    def process_text_content(self, text_content: str, source_file: str) -> List[DocumentChunk]:
        """
        Process text content directly and return chunks.
        
        Args:
            text_content: Text content to process
            source_file: Source file name for metadata
            
        Returns:
            List of DocumentChunk objects
        """
        if not text_content or not text_content.strip():
            return []
        
        # Clean and normalize text
        cleaned_text = self._clean_and_normalize_text(text_content)
        
        # Generate chunks
        chunks = self._generate_chunks(cleaned_text, source_file)
        
        return chunks
    
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
            
            # Validate document
            if not self._validate_document(file_path, metadata):
                error_msg = f"Document validation failed: {', '.join(metadata.validation_errors)}"
                logger.error(error_msg)
                metadata.processing_status = 'failed'
                metadata.error_message = error_msg
                metadata.processing_time = time.time() - start_time
                raise ValueError(error_msg)
            
            # Update processing status
            metadata.processing_status = 'processing'
            
            # Process file based on type
            processor_func = self.supported_extensions[file_extension]
            raw_text = processor_func(file_path)
            
            # Clean and normalize text
            cleaned_text = self._clean_and_normalize_text(raw_text)
            
            # Analyze content for enhanced metadata
            content_analysis = self._analyze_content(cleaned_text, metadata.file_type)
            
            # Generate chunks
            chunks = self._generate_chunks(cleaned_text, file_path.name)
            
            # Update metadata with comprehensive information
            metadata.word_count = len(cleaned_text.split())
            metadata.char_count = len(cleaned_text)
            metadata.chunk_count = len(chunks)
            metadata.sentence_count = content_analysis['sentence_count']
            metadata.paragraph_count = content_analysis['paragraph_count']
            metadata.line_count = content_analysis['line_count']
            metadata.content_type = content_analysis['content_type']
            metadata.has_tables = content_analysis['has_tables']
            metadata.has_images = content_analysis['has_images']
            metadata.has_links = content_analysis['has_links']
            metadata.language_detected = content_analysis['language_detected']
            metadata.processing_time = time.time() - start_time
            metadata.processing_status = 'completed'
            metadata.processed_at = datetime.now()
            
            # Update performance metrics
            self._update_metrics(len(chunks), metadata.processing_time)
            
            logger.info(f"Successfully processed {file_path.name}: {len(chunks)} chunks in {metadata.processing_time:.2f}s")
            
            return chunks, metadata
            
        except Exception as e:
            error_msg = f"Failed to process document {file_path}: {e}"
            logger.error(error_msg)
            self._processing_metrics['errors'].append(error_msg)
            
            # Update metadata with error information
            if 'metadata' in locals():
                metadata.processing_status = 'failed'
                metadata.error_message = error_msg
                metadata.processing_time = time.time() - start_time
                metadata.processed_at = datetime.now()
            
            raise RuntimeError(error_msg)
    
    def process_file(self, file_path: Union[str, Path], document_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a file and return a result object compatible with the API.
        
        Args:
            file_path: Path to the document file
            document_id: Optional document ID to include in chunk metadata
            
        Returns:
            Dict containing 'chunks' and 'metadata' keys
            
        Raises:
            ValueError: If file doesn't exist or is unsupported
            RuntimeError: If processing fails
        """
        try:
            chunks, metadata = self.process_document(file_path)
            
            # Convert chunks to the format expected by the vector store
            try:
                from .vector_store import VectorDocument
            except ImportError:
                from vector_store import VectorDocument
            vector_documents = []
            
            for chunk in chunks:
                # Add document_id to chunk metadata if provided
                if document_id:
                    chunk.metadata['document_id'] = document_id
                
                # Generate a proper UUID for Qdrant
                import uuid
                vector_doc = VectorDocument(
                    id=str(uuid.uuid4()),
                    text=chunk.text,
                    vector=[],  # Will be populated by embedding service
                    metadata=chunk.metadata,
                    source_file=chunk.source_file,
                    chunk_index=chunk.chunk_index,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                vector_documents.append(vector_doc)
            
            return {
                'chunks': vector_documents,
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"process_file failed for {file_path}: {e}")
            raise
    
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
            sentence_count=0, # Will be updated after processing
            paragraph_count=0, # Will be updated after processing
            line_count=0, # Will be updated after processing
            processing_time=0.0,  # Will be updated after processing
            processing_status='pending', # Will be updated after processing
            created_at=datetime.fromtimestamp(stat.st_ctime),
            last_modified=datetime.fromtimestamp(stat.st_mtime),
            content_hash=content_hash,
            content_type='text', # Will be updated after processing
            is_valid=True, # Will be updated after processing
            error_message=None, # Will be updated after processing
            processed_at=None, # Will be updated after processing
            language_detected=None, # Will be updated after processing
            has_tables=False, # Will be updated after processing
            has_images=False, # Will be updated after processing
            has_links=False, # Will be updated after processing
            validation_errors=[] # Will be updated after processing
        )
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file content."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def _validate_document(self, file_path: Path, metadata: DocumentMetadata) -> bool:
        """Validate document before processing."""
        validation_errors = []
        
        # Check file size
        max_size_bytes = self._parse_file_size(self.config.document.max_file_size)
        if metadata.file_size > max_size_bytes:
            validation_errors.append(f"File size {metadata.file_size} bytes exceeds limit of {max_size_bytes} bytes")
        
        # Check file type
        if metadata.file_type not in [ext for ext in self.supported_extensions.keys()]:
            validation_errors.append(f"Unsupported file type: {metadata.file_type}")
        
        # Check if file is empty
        if metadata.file_size == 0:
            validation_errors.append("File is empty")
        
        # Check if file is readable
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1)  # Try to read first character
        except Exception as e:
            validation_errors.append(f"File is not readable: {e}")
        
        # Update metadata with validation results
        metadata.is_valid = len(validation_errors) == 0
        metadata.validation_errors = validation_errors
        
        return metadata.is_valid
    
    def _parse_file_size(self, size_str: str) -> int:
        """Parse file size string to bytes."""
        size_str = size_str.upper().strip()
        if size_str.endswith('MB'):
            return int(float(size_str[:-2]) * 1024 * 1024)
        elif size_str.endswith('KB'):
            return int(float(size_str[:-2]) * 1024)
        elif size_str.endswith('GB'):
            return int(float(size_str[:-2]) * 1024 * 1024 * 1024)
        else:
            return int(size_str)
    
    def _analyze_content(self, text: str, file_type: str) -> Dict[str, Any]:
        """Analyze content for enhanced metadata."""
        analysis = {
            'sentence_count': 0,
            'paragraph_count': 0,
            'line_count': 0,
            'content_type': 'text',
            'has_tables': False,
            'has_images': False,
            'has_links': False,
            'language_detected': None
        }
        
        if not text:
            return analysis
        
        # Count lines
        analysis['line_count'] = len(text.split('\n'))
        
        # Count paragraphs (non-empty lines separated by empty lines)
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        analysis['paragraph_count'] = len(paragraphs)
        
        # Count sentences
        sentences = self._split_into_sentences(text)
        analysis['sentence_count'] = len(sentences)
        
        # Detect content features
        analysis['has_tables'] = '|' in text and '\n' in text
        analysis['has_images'] = '![' in text or 'image:' in text.lower()
        analysis['has_links'] = 'http' in text or 'www.' in text
        
        # Determine content type
        if file_type == 'csv':
            analysis['content_type'] = 'structured'
        elif analysis['has_tables'] and analysis['has_links']:
            analysis['content_type'] = 'mixed'
        elif analysis['has_tables']:
            analysis['content_type'] = 'structured'
        else:
            analysis['content_type'] = 'text'
        
        # Basic language detection (English vs non-English)
        # This is a simple heuristic - in production, use a proper language detection library
        english_chars = sum(1 for c in text if c.isalpha() and ord(c) < 128)
        total_chars = sum(1 for c in text if c.isalpha())
        if total_chars > 0 and english_chars / total_chars > 0.9:
            analysis['language_detected'] = 'en'
        else:
            analysis['language_detected'] = 'unknown'
        
        return analysis
    
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
        """Process a CSV file and convert to text with enhanced features."""
        try:
            with open(file_path, 'r', encoding='utf-8', newline='') as f:
                reader = csv.reader(f)
                
                # Read header
                header = next(reader, [])
                if not header:
                    return "Empty CSV file"
                
                # Analyze data types and structure
                data_types = self._analyze_csv_data_types(header, reader)
                
                # Reset file pointer for full processing
                f.seek(0)
                reader = csv.reader(f)
                next(reader)  # Skip header again
                
                # Convert to text format with enhanced structure
                lines = []
                lines.append("CSV Document Analysis")
                lines.append("=" * 60)
                lines.append(f"File: {file_path.name}")
                lines.append(f"Columns: {len(header)}")
                lines.append(f"Column Headers: {', '.join(header)}")
                lines.append("")
                
                # Add data type information
                lines.append("Data Types:")
                for col_name, data_type in data_types.items():
                    lines.append(f"  - {col_name}: {data_type}")
                lines.append("")
                
                # Process rows with better formatting
                row_count = 0
                for i, row in enumerate(reader, 1):
                    if not row:  # Skip empty rows
                        continue
                    
                    row_count += 1
                    
                    # Create a structured row representation
                    row_data = []
                    for j, (col_name, value) in enumerate(zip(header, row)):
                        # Format based on data type
                        formatted_value = self._format_csv_value(value, data_types.get(col_name, 'string'))
                        row_data.append(f"{col_name}: {formatted_value}")
                    
                    row_text = f"Row {i}: {' | '.join(row_data)}"
                    lines.append(row_text)
                
                # Add summary
                lines.append("")
                lines.append(f"Total Rows: {row_count}")
                lines.append(f"Total Columns: {len(header)}")
                
                return "\n".join(lines)
                
        except UnicodeDecodeError:
            # Try alternative encodings
            encodings = ['latin-1', 'cp1252', 'iso-8859-1']
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding, newline='') as f:
                        reader = csv.reader(f)
                        header = next(reader, [])
                        if header:
                            logger.info(f"Successfully read CSV {file_path} with {encoding} encoding")
                            # Process with the working encoding
                            return self._process_csv_with_encoding(file_path, encoding)
                except UnicodeDecodeError:
                    continue
            
            raise RuntimeError(f"Could not decode CSV file {file_path} with any supported encoding")
        except Exception as e:
            logger.error(f"Failed to process CSV file {file_path}: {e}")
            raise RuntimeError(f"CSV processing failed: {e}")
    
    def _process_csv_with_encoding(self, file_path: Path, encoding: str) -> str:
        """Process CSV file with specific encoding."""
        with open(file_path, 'r', encoding=encoding, newline='') as f:
            reader = csv.reader(f)
            header = next(reader, [])
            
            lines = []
            lines.append(f"CSV Document (Encoding: {encoding})")
            lines.append("=" * 50)
            lines.append(f"Columns: {', '.join(header)}")
            lines.append("")
            
            for i, row in enumerate(reader, 1):
                if not row:
                    continue
                row_text = f"Row {i}: {', '.join(str(cell) for cell in row)}"
                lines.append(row_text)
            
            return "\n".join(lines)
    
    def _analyze_csv_data_types(self, header: List[str], reader) -> Dict[str, str]:
        """Analyze CSV data types by examining sample rows."""
        data_types = {}
        sample_rows = []
        
        # Collect sample rows for analysis
        for i, row in enumerate(reader):
            if i >= 10:  # Analyze first 10 rows
                break
            if row and len(row) == len(header):
                sample_rows.append(row)
        
        # Analyze each column
        for col_idx, col_name in enumerate(header):
            values = [row[col_idx] for row in sample_rows if len(row) > col_idx]
            data_types[col_name] = self._detect_data_type(values)
        
        return data_types
    
    def _detect_data_type(self, values: List[str]) -> str:
        """Detect data type from a list of values."""
        if not values:
            return 'string'
        
        # Check for numeric types
        numeric_count = 0
        float_count = 0
        date_count = 0
        
        for value in values:
            value = value.strip()
            if not value:
                continue
            
            # Check for integers
            try:
                int(value)
                numeric_count += 1
                continue
            except ValueError:
                pass
            
            # Check for floats
            try:
                float(value)
                float_count += 1
                continue
            except ValueError:
                pass
            
            # Check for dates (basic patterns)
            date_patterns = [
                r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
                r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
                r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
            ]
            for pattern in date_patterns:
                if re.match(pattern, value):
                    date_count += 1
                    break
        
        total_valid = len([v for v in values if v.strip()])
        if total_valid == 0:
            return 'string'
        
        # Determine dominant type
        if date_count / total_valid > 0.5:
            return 'date'
        elif float_count / total_valid > 0.5:
            return 'float'
        elif numeric_count / total_valid > 0.5:
            return 'integer'
        else:
            return 'string'
    
    def _format_csv_value(self, value: str, data_type: str) -> str:
        """Format CSV value based on detected data type."""
        if not value.strip():
            return "(empty)"
        
        if data_type == 'integer':
            try:
                return str(int(value))
            except ValueError:
                return value
        elif data_type == 'float':
            try:
                return f"{float(value):.2f}"
            except ValueError:
                return value
        elif data_type == 'date':
            return value  # Keep date as is
        else:
            return value
    
    def _process_markdown_file(self, file_path: Path) -> str:
        """Process a markdown file and convert to plain text with enhanced features."""
        try:
            content = self._process_text_file(file_path)
            
            # Enhanced markdown to text conversion
            processed_content = self._convert_markdown_to_text(content)
            
            return processed_content
            
        except Exception as e:
            logger.error(f"Failed to process markdown file {file_path}: {e}")
            raise RuntimeError(f"Markdown processing failed: {e}")
    
    def _convert_markdown_to_text(self, content: str) -> str:
        """Convert markdown content to plain text with enhanced processing."""
        if not content:
            return ""
        
        # Remove code blocks (keep content for context)
        content = re.sub(r'```[\w]*\n(.*?)\n```', r'[Code Block: \1]', content, flags=re.DOTALL)
        
        # Remove inline code markers but keep content
        content = re.sub(r'`([^`]+)`', r'\1', content)
        
        # Process headers (convert to plain text with hierarchy indication)
        content = re.sub(r'^(#{1,6})\s+(.+)$', self._convert_header, content, flags=re.MULTILINE)
        
        # Process bold text (keep content)
        content = re.sub(r'\*\*([^*]+)\*\*', r'\1', content)
        content = re.sub(r'__([^_]+)__', r'\1', content)
        
        # Process italic text (keep content)
        content = re.sub(r'\*([^*]+)\*', r'\1', content)
        content = re.sub(r'_([^_]+)_', r'\1', content)
        
        # Process links (extract text and URL)
        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1 (URL: \2)', content)
        
        # Process images (extract alt text)
        content = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'[Image: \1]', content)
        
        # Process tables
        content = self._convert_markdown_tables(content)
        
        # Process lists
        content = self._convert_markdown_lists(content)
        
        # Process blockquotes
        content = re.sub(r'^>\s+(.+)$', r'Quote: \1', content, flags=re.MULTILINE)
        
        # Process horizontal rules
        content = re.sub(r'^[-*_]{3,}$', r'---', content, flags=re.MULTILINE)
        
        # Clean up extra whitespace and normalize
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        content = content.strip()
        
        return content
    
    def _convert_header(self, match) -> str:
        """Convert markdown header to plain text with hierarchy indication."""
        level = len(match.group(1))
        text = match.group(2)
        
        # Create hierarchy indicator
        if level == 1:
            return f"\n{text}\n{'=' * len(text)}\n"
        elif level == 2:
            return f"\n{text}\n{'-' * len(text)}\n"
        else:
            prefix = '  ' * (level - 1)
            return f"\n{prefix}{text}\n"
    
    def _convert_markdown_tables(self, content: str) -> str:
        """Convert markdown tables to plain text format."""
        # Find table blocks
        table_pattern = r'(\|[^\n]*\|[^\n]*\n\|[^\n]*\|[^\n]*\n(\|[^\n]*\|[^\n]*\n)*)'
        
        def convert_table(match):
            table_text = match.group(1)
            lines = table_text.strip().split('\n')
            
            if len(lines) < 2:
                return table_text
            
            # Parse table structure
            table_data = []
            for line in lines:
                if line.strip() and '|' in line:
                    # Remove leading/trailing pipes and split
                    cells = [cell.strip() for cell in line.strip('|').split('|')]
                    table_data.append(cells)
            
            if len(table_data) < 2:
                return table_text
            
            # Convert to text format
            result = ["\nTable:"]
            
            # Add header
            if table_data:
                header = table_data[0]
                result.append("  " + " | ".join(header))
                result.append("  " + "-" * (len(" | ".join(header))))
                
                # Add data rows (skip separator row)
                for row in table_data[2:]:
                    if row and any(cell.strip() for cell in row):
                        result.append("  " + " | ".join(row))
            
            result.append("")  # Add spacing
            return "\n".join(result)
        
        return re.sub(table_pattern, convert_table, content, flags=re.MULTILINE)
    
    def _convert_markdown_lists(self, content: str) -> str:
        """Convert markdown lists to plain text format."""
        lines = content.split('\n')
        result_lines = []
        in_list = False
        list_indent = 0
        
        for line in lines:
            # Check for list items
            list_match = re.match(r'^(\s*)([-*+]|\d+\.)\s+(.+)$', line)
            
            if list_match:
                indent = len(list_match.group(1))
                marker = list_match.group(2)
                text = list_match.group(3)
                
                if not in_list:
                    in_list = True
                    list_indent = indent
                    result_lines.append("")  # Add spacing before list
                
                # Create list item
                if marker in ['-', '*', '+']:
                    result_lines.append("  " * (indent - list_indent) + f"• {text}")
                else:
                    result_lines.append("  " * (indent - list_indent) + f"{marker} {text}")
            else:
                if in_list and line.strip() == '':
                    # End of list
                    in_list = False
                    result_lines.append("")  # Add spacing after list
                result_lines.append(line)
        
        return '\n'.join(result_lines)
    
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
        """Create a document chunk with enhanced metadata."""
        # Create a more robust chunk ID
        chunk_hash = hashlib.md5(text.encode()).hexdigest()[:12]
        chunk_id = f"{source_file.replace('.', '_')}_{chunk_index:04d}_{chunk_hash}"
        
        # Enhanced chunk metadata
        metadata = {
            'source_file': source_file,
            'chunk_index': chunk_index,
            'chunk_id': chunk_id,
            'word_count': len(text.split()),
            'char_count': len(text),
            'sentence_count': len(self._split_into_sentences(text)),
            'start_char': start_char,
            'end_char': end_char,
            'chunk_size': len(text),
            'created_at': datetime.now().isoformat(),
            'chunk_type': 'text',
            'has_content': bool(text.strip()),
            'content_preview': text[:100] + '...' if len(text) > 100 else text
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
                'min_chunk_size': self.min_chunk_size,
                'max_file_size': self.config.document.max_file_size,
                'max_chunks_per_document': self.config.document.max_chunks_per_document
            }
        }
    
    def get_processing_status(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Get processing status for a specific document."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                'status': 'not_found',
                'file_path': str(file_path),
                'error': 'File does not exist'
            }
        
        try:
            # Extract basic metadata to check status
            metadata = self._extract_file_metadata(file_path)
            
            return {
                'status': 'available',
                'file_path': str(file_path),
                'file_name': metadata.file_name,
                'file_size': metadata.file_size,
                'file_type': metadata.file_type,
                'last_modified': metadata.last_modified.isoformat(),
                'is_valid': metadata.is_valid,
                'validation_errors': metadata.validation_errors
            }
        except Exception as e:
            return {
                'status': 'error',
                'file_path': str(file_path),
                'error': str(e)
            }
    
    def validate_document_file(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Validate a document file without processing it."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            return {
                'valid': False,
                'errors': ['File does not exist'],
                'file_path': str(file_path)
            }
        
        try:
            metadata = self._extract_file_metadata(file_path)
            is_valid = self._validate_document(file_path, metadata)
            
            return {
                'valid': is_valid,
                'errors': metadata.validation_errors,
                'file_path': str(file_path),
                'file_name': metadata.file_name,
                'file_size': metadata.file_size,
                'file_type': metadata.file_type,
                'content_hash': metadata.content_hash
            }
        except Exception as e:
            return {
                'valid': False,
                'errors': [f'Validation failed: {e}'],
                'file_path': str(file_path)
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
