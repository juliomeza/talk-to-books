import os
import logging
from typing import List, Dict, Any, Optional
import PyPDF2
import docx
import re
import chardet
from langchain.text_splitter import RecursiveCharacterTextSplitter

logger = logging.getLogger(__name__)

class BookParser:
    """
    Service for parsing book files (PDF, DOCX, TXT) and extracting text content.
    Also responsible for chunking the text for embedding generation.
    """
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """
        Initialize book parser.
        
        Args:
            chunk_size: Size of text chunks in characters
            chunk_overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    def parse_file(self, file_path: str) -> Optional[str]:
        """
        Parse a book file and extract text content.
        
        Args:
            file_path: Path to the book file
            
        Returns:
            Extracted text content or None if failed
        """
        try:
            file_extension = os.path.splitext(file_path)[1].lower()
            
            if file_extension == '.pdf':
                return self._parse_pdf(file_path)
            elif file_extension == '.docx':
                return self._parse_docx(file_path)
            elif file_extension == '.txt':
                return self._parse_txt(file_path)
            else:
                logger.error(f"Unsupported file format: {file_extension}")
                return None
        
        except Exception as e:
            logger.error(f"Error parsing file {file_path}: {e}")
            return None
    
    def _parse_pdf(self, file_path: str) -> str:
        """Parse PDF file and extract text."""
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"
        return text
    
    def _parse_docx(self, file_path: str) -> str:
        """Parse DOCX file and extract text."""
        doc = docx.Document(file_path)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    
    def _parse_txt(self, file_path: str) -> str:
        """Parse TXT file and extract text."""
        # Detect encoding
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']
        
        # Read with detected encoding
        with open(file_path, 'r', encoding=encoding) as f:
            text = f.read()
        return text
    
    def chunk_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Split text into chunks for embedding.
        
        Args:
            text: Full text content
            
        Returns:
            List of chunk objects with text and metadata
        """
        # Clean text
        text = self._clean_text(text)
        
        # Split into chunks
        raw_chunks = self.text_splitter.split_text(text)
        
        # Format chunks with metadata
        chunks = []
        for i, chunk_text in enumerate(raw_chunks):
            chunks.append({
                "text": chunk_text,
                "chunk_id": f"chunk_{i}",
                # Estimate page number based on chunk position
                "page": i // 3 + 1  # Rough estimate: 3 chunks per page
            })
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean text by removing extra whitespace, etc."""
        # Replace multiple newlines with single newline
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # Replace multiple spaces with single space
        text = re.sub(r' +', ' ', text)
        
        # Strip leading/trailing whitespace
        text = text.strip()
        
        return text
