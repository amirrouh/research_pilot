"""
OCR Tool - Extract text from documents using Docling (IBM Research)

Advanced document parsing that preserves structure, tables, and layout.
Converts PDFs, images, DOCX, HTML to clean Markdown.

Usage:
    from trion.tools.document.ocr import read

    # Extract text from PDF (maintains structure)
    text = read("document.pdf")

    # Extract from image
    text = read("image.jpg")

    # Specific page from PDF
    text = read("document.pdf", page=1)

Returns:
    str: Extracted text in Markdown format with preserved structure
"""

from typing import Optional, Union
from pathlib import Path
from trion.tools._dependencies import require_package

# Check docling is installed
require_package("docling", "document")

from docling.document_converter import DocumentConverter


def read(
    file_path: Union[str, Path],
    page: Optional[int] = None
) -> str:
    """
    Extract text from documents using Docling OCR.

    Preserves document structure including:
    - Headings and hierarchy
    - Tables (with proper formatting)
    - Lists and paragraphs
    - Code blocks
    - Mathematical formulas
    - Reading order

    Args:
        file_path: Path to the file (pdf, docx, jpg, png, html, etc.)
        page: For PDFs, specific page number to extract (1-indexed). None = all pages

    Returns:
        Markdown-formatted text with preserved document structure

    Examples:
        read("paper.pdf")  # Full document
        read("paper.pdf", page=1)  # Single page
        read("image.jpg")  # Image OCR
        read("document.docx")  # Word doc
    """
    # Convert path to string
    file_path = str(file_path)

    # Create converter
    converter = DocumentConverter()

    # Convert document
    result = converter.convert(file_path)

    # Get markdown output
    markdown = result.document.export_to_markdown()

    # Handle page selection for PDFs
    if page is not None and file_path.lower().endswith('.pdf'):
        # Split by page markers
        pages = markdown.split('\n\n---\n\n')  # Docling uses --- for page breaks

        if page < 1 or page > len(pages):
            raise ValueError(f"Page {page} out of range (1-{len(pages)})")

        return pages[page - 1]

    return markdown


# LangChain Tool Wrapper
try:
    from langchain_core.tools import tool

    @tool
    def ocr_read(file_path: str, page: int = None) -> str:
        """
        Extract text from documents with structure preservation using advanced OCR.

        Use this tool when you need to:
        - Extract text from PDFs, images, or Office documents
        - Preserve document structure (headings, tables, lists)
        - Get clean Markdown output
        - Process scanned documents or images with text
        - Extract data from forms, receipts, invoices

        Supports: PDF, DOCX, PPTX, XLSX, HTML, images (jpg, png), EPUB

        Args:
            file_path: Path to the document file
            page: For PDFs, specific page number (1-indexed). None = all pages

        Returns:
            Clean Markdown text with preserved document structure
        """
        result = read(file_path, page=page)
        return result

except ImportError:
    # LangChain not installed - skip tool creation
    pass


# Test
if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python ocr.py <file_path> [page_number]")
        print("\nExample:")
        print("  python ocr.py document.pdf")
        print("  python ocr.py document.pdf 1")
        print("  python ocr.py image.jpg")
        sys.exit(1)

    file_path = sys.argv[1]
    page_num = int(sys.argv[2]) if len(sys.argv) > 2 else None

    print(f"\n{'='*80}")
    print(f"Processing: {file_path}")
    if page_num:
        print(f"Page: {page_num}")
    print(f"{'='*80}\n")

    result = read(file_path, page=page_num)
    print(result)

    print(f"\n{'='*80}")
    print("✅ OCR completed!")
    print(f"{'='*80}\n")
