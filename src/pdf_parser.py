"""
PDF Parser Module

Handles PDF file parsing and element extraction.
"""

import io
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from loguru import logger

try:
    import fitz  # PyMuPDF
except ImportError:
    logger.error("PyMuPDF not installed. Install with: pip install PyMuPDF")
    raise


@dataclass
class PDFElement:
    """Represents an extracted PDF element (text, image, table)."""
    element_type: str  # 'text', 'image', 'table'
    content: str
    page_num: int
    bbox: tuple  # (x0, y0, x1, y1)
    font_name: Optional[str] = None
    font_size: Optional[float] = None
    confidence: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert element to dictionary."""
        return {
            'type': self.element_type,
            'content': self.content,
            'page': self.page_num,
            'bbox': self.bbox,
            'font': self.font_name,
            'size': self.font_size,
            'confidence': self.confidence
        }


class PDFParser:
    """PDF parsing and element extraction."""
    
    def __init__(self, pdf_path: str):
        """Initialize PDF parser."""
        self.pdf_path = Path(pdf_path)
        self.document = None
        self.elements: List[PDFElement] = []
        self.metadata = {}
        
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        logger.info(f"Initializing PDF parser for: {self.pdf_path}")
    
    def open(self) -> None:
        """Open PDF document."""
        try:
            self.document = fitz.open(str(self.pdf_path))
            self._extract_metadata()
            logger.info(f"PDF opened successfully. Pages: {self.document.page_count}")
        except Exception as e:
            logger.error(f"Failed to open PDF: {str(e)}")
            raise
    
    def _extract_metadata(self) -> None:
        """Extract PDF metadata."""
        if not self.document:
            return
        
        self.metadata = {
            'pages': self.document.page_count,
            'title': self.document.metadata.get('title', ''),
            'author': self.document.metadata.get('author', ''),
            'subject': self.document.metadata.get('subject', ''),
            'creator': self.document.metadata.get('creator', ''),
        }
    
    def parse_all_pages(self) -> List[PDFElement]:
        """Parse all pages in PDF."""
        if not self.document:
            self.open()
        
        self.elements = []
        for page_num in range(self.document.page_count):
            self._parse_page(page_num)
        
        logger.info(f"Extracted {len(self.elements)} elements from PDF")
        return self.elements
    
    def _parse_page(self, page_num: int) -> None:
        """Parse a single page."""
        page = self.document[page_num]
        
        # Extract text blocks
        text_dict = page.get_text("dict")
        for block in text_dict.get("blocks", []):
            if block["type"] == 0:  # Text block
                self._extract_text_block(block, page_num)
            elif block["type"] == 1:  # Image block
                self._extract_image_block(block, page_num)
    
    def _extract_text_block(self, block: Dict, page_num: int) -> None:
        """Extract text from a text block."""
        bbox = block["bbox"]
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                text = span["text"]
                font_name = span.get("font", "Unknown")
                font_size = span.get("size", 0)
                
                element = PDFElement(
                    element_type="text",
                    content=text,
                    page_num=page_num,
                    bbox=tuple(bbox),
                    font_name=font_name,
                    font_size=font_size
                )
                self.elements.append(element)
    
    def _extract_image_block(self, block: Dict, page_num: int) -> None:
        """Extract image information from an image block."""
        bbox = block["bbox"]
        element = PDFElement(
            element_type="image",
            content="[Image]",
            page_num=page_num,
            bbox=tuple(bbox)
        )
        self.elements.append(element)
    
    def get_elements_by_type(self, element_type: str) -> List[PDFElement]:
        """Get elements filtered by type."""
        return [e for e in self.elements if e.element_type == element_type]
    
    def get_elements_by_page(self, page_num: int) -> List[PDFElement]:
        """Get elements from a specific page."""
        return [e for e in self.elements if e.page_num == page_num]
    
    def export_elements(self) -> List[Dict[str, Any]]:
        """Export elements as list of dictionaries."""
        return [e.to_dict() for e in self.elements]
    
    def close(self) -> None:
        """Close PDF document."""
        if self.document:
            self.document.close()
            logger.info("PDF document closed")
    
    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
