"""
Lightweight PDF parser for SuperScan sparse text extraction.

Uses PyPDF2 for simple text extraction (no deep chunking or layout analysis).
"""

from typing import Dict, List, Optional
import io

def extract_text_from_pdf(pdf_bytes: bytes, max_pages: int = 10) -> Dict[str, any]:
    """
    Extract sparse text from PDF for ontology proposal hints.
    
    Args:
        pdf_bytes: PDF file content as bytes
        max_pages: Maximum number of pages to extract (for speed)
    
    Returns:
        Dict with 'pages', 'total_pages', and 'text_snippets'
    """
    try:
        import PyPDF2
    except ImportError:
        # Fallback if PyPDF2 not installed
        return {
            "pages": 0,
            "total_pages": 0,
            "text_snippets": ["PDF parsing library not available. Install PyPDF2."],
        }
    
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
        total_pages = len(reader.pages)
        pages_to_scan = min(max_pages, total_pages)
        
        snippets = []
        for i in range(pages_to_scan):
            page = reader.pages[i]
            text = page.extract_text()
            if text and text.strip():
                # Keep first 500 chars per page for sparse scan
                snippets.append(text.strip()[:500])
        
        return {
            "pages": pages_to_scan,
            "total_pages": total_pages,
            "text_snippets": snippets,
        }
    except Exception as e:
        return {
            "pages": 0,
            "total_pages": 0,
            "text_snippets": [f"PDF parsing error: {str(e)}"],
        }


def extract_text_from_file_path(file_path: str, max_pages: int = 10) -> Dict[str, any]:
    """Extract text from PDF file path."""
    with open(file_path, 'rb') as f:
        return extract_text_from_pdf(f.read(), max_pages=max_pages)
