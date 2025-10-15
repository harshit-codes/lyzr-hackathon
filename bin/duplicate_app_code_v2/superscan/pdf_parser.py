"""
This module provides a lightweight PDF parser for the SuperScan component.

The `PDFParser` class uses the `PyPDF2` library to extract text from PDF
documents. It is designed for a "sparse" scan, meaning it only extracts text
from the first few pages of the document. This is used to generate a schema
proposal without having to process the entire document.
"""

from typing import Dict, List, Optional
import io

class PDFParser:
    """
    A lightweight PDF parser for SuperScan.

    This class uses the `PyPDF2` library to extract text from the first few
    pages of a PDF document.
    """

    def __init__(self):
        """
        Initializes the `PDFParser`.
        """
        self.max_pages = 10

    def extract_text(self, file_path: str) -> str:
        """
        Extracts text from a PDF file.

        Args:
            file_path: The path to the PDF file.

        Returns:
            A string containing the extracted text.
        """
        result = extract_text_from_file_path(file_path, max_pages=self.max_pages)
        # Join snippets into single text
        return '\n\n'.join(result.get('text_snippets', []))

def extract_text_from_pdf(pdf_bytes: bytes, max_pages: int = 10) -> Dict[str, any]:
    """
    Extracts sparse text from a PDF for ontology proposal hints.

    This function extracts text from the first few pages of a PDF document
    and returns it as a list of snippets.

    Args:
        pdf_bytes: The PDF file content as bytes.
        max_pages: The maximum number of pages to extract text from.

    Returns:
        A dictionary containing the number of pages scanned, the total
        number of pages, and a list of text snippets.
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
    """
    Extracts text from a PDF file path.

    Args:
        file_path: The path to the PDF file.
        max_pages: The maximum number of pages to extract text from.

    Returns:
        A dictionary containing the number of pages scanned, the total
        number of pages, and a list of text snippets.
    """
    with open(file_path, 'rb') as f:
        return extract_text_from_pdf(f.read(), max_pages=max_pages)