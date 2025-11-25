# -----------------------------------------------------------------------------
# File: test_document_parser.py
# Description: Test suite for document_parser.py - tests document parsing
#              functionality for PDF, DOCX, and text file formats.
# Author: Pradyumna Chacham
# Date: November 2025
# Copyright (c) 2025 Pradyumna Chacham. All rights reserved.
# License: MIT License - see LICENSE file in the root directory.
# -----------------------------------------------------------------------------

import os
from io import BytesIO

import pytest
import PyPDF2
from fastapi import HTTPException
from reportlab.pdfgen import canvas

from utilities.document_parser import extract_from_pdf, extract_from_docx
from docx import Document

from utilities.document_parser import (categorize_text_size, extract_from_text,
                             extract_text_from_file, get_text_stats,
                             parse_document, validate_file_size)


class MockFile:
    def __init__(self, filename: str, content: bytes):
        self.filename = filename
        self.file = BytesIO(content)

    def __call__(self):
        return self


def test_parse_document():
    # Test with simple text
    text = "Sample document text"
    result = parse_document(text)

    assert isinstance(result, dict)
    assert "text" in result
    assert "metadata" in result
    assert result["text"] == text
    assert result["metadata"]["format"] == "text"
    assert result["metadata"]["version"] == "1.0"
    assert result["metadata"]["encoding"] == "utf-8"
    assert "stats" in result["metadata"]


def test_extract_from_text():
    # Test UTF-8 text
    content = "Hello, world!".encode("utf-8")
    result = extract_from_text(content)
    assert result == "Hello, world!"

    # Test latin-1 text
    content = "Hello, world!".encode("latin-1")
    result = extract_from_text(content)
    assert result == "Hello, world!"

    # Test invalid encoding - use bytes that will fail latin-1 too
    # Actually, latin-1 can decode almost any byte sequence, so let's test a different edge case
    # Just verify the function works with valid inputs
    content = "Test content with special chars: áéíóú".encode("utf-8")
    result = extract_from_text(content)
    assert "áéíóú" in result


def test_validate_file_size():
    # Test file within size limit
    content = b"Small file content"
    file = MockFile("test.txt", content)
    validate_file_size(file(), max_size_mb=1)  # Should not raise exception

    # Test file exceeding size limit
    large_content = b"x" * (11 * 1024 * 1024)  # 11MB
    file = MockFile("large.txt", large_content)
    with pytest.raises(HTTPException) as exc:
        validate_file_size(file(), max_size_mb=10)
    assert "File too large" in str(exc.value.detail)


def test_get_text_stats():
    text = "Line 1\nLine 2\nLine 3"
    stats = get_text_stats(text)

    assert isinstance(stats, dict)
    assert "characters" in stats
    assert "words" in stats
    assert "lines" in stats
    assert "estimated_tokens" in stats
    assert "size_category" in stats

    assert stats["characters"] == len(text)
    assert stats["words"] == 6  # "Line", "1", "Line", "2", "Line", "3"
    assert stats["lines"] == 3
    assert stats["estimated_tokens"] == 6 * 1.3  # words * 1.3


def test_categorize_text_size():
    assert categorize_text_size(100) == "tiny"
    assert categorize_text_size(1000) == "small"
    assert categorize_text_size(5000) == "medium"
    assert categorize_text_size(10000) == "large"
    assert categorize_text_size(25000) == "very_large"


def test_extract_text_from_file():
    # Test txt file
    txt_content = "Hello, world!".encode("utf-8")
    txt_file = MockFile("test.txt", txt_content)
    txt_text, txt_ext = extract_text_from_file(txt_file())
    assert txt_text == "Hello, world!"
    assert txt_ext == ".txt"

    # Test markdown file
    md_content = "# Title\nContent".encode("utf-8")
    md_file = MockFile("test.md", md_content)
    md_text, md_ext = extract_text_from_file(md_file())
    assert md_text == "# Title\nContent"
    assert md_ext == ".md"

    # Test unsupported file type
    invalid_file = MockFile("test.xyz", b"content")
    with pytest.raises(HTTPException) as exc:
        extract_text_from_file(invalid_file())
    assert "Unsupported file type" in str(exc.value.detail)

    # Test file read error
    broken_file = MockFile("test.txt", None)
    broken_file.file = None  # Simulate broken file
    with pytest.raises(HTTPException) as exc:
        extract_text_from_file(broken_file())
    assert "Error reading file" in str(exc.value.detail)


# Test PDF extraction
def test_extract_from_pdf():
    # Create a simple PDF in memory for testing
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer)
    c.drawString(100, 750, "Test PDF content")
    c.save()

    # Test PDF extraction
    pdf_content = pdf_buffer.getvalue()
    result = extract_from_pdf(pdf_content)
    assert "Test PDF content" in result

    # Test invalid PDF
    with pytest.raises(HTTPException) as exc:
        extract_from_pdf(b"invalid pdf content")
    assert "Error parsing PDF" in str(exc.value.detail)


# Test DOCX extraction
def test_extract_from_docx():
    # Create a simple DOCX in memory
    doc = Document()
    doc.add_paragraph("Test DOCX content")
    docx_buffer = BytesIO()
    doc.save(docx_buffer)

    # Test DOCX extraction
    docx_content = docx_buffer.getvalue()
    result = extract_from_docx(docx_content)
    assert "Test DOCX content" in result

    # Test invalid DOCX
    with pytest.raises(HTTPException) as exc:
        extract_from_docx(b"invalid docx content")
    assert "Error parsing DOCX" in str(exc.value.detail)


def test_parse_document_with_metadata():
    """Test parse_document includes proper metadata"""
    text = "Test document" * 100  # Make it a bit larger
    result = parse_document(text)
    
    assert result["metadata"]["format"] == "text"
    assert result["metadata"]["version"] == "1.0"
    assert "stats" in result["metadata"]
    assert result["metadata"]["stats"]["characters"] > 0
    assert result["metadata"]["stats"]["words"] > 0


def test_get_text_stats_edge_cases():
    """Test text stats with edge cases"""
    # Empty text
    empty_stats = get_text_stats("")
    assert empty_stats["characters"] == 0
    assert empty_stats["words"] == 0
    assert empty_stats["lines"] == 1  # Empty string has 1 line
    
    # Single word
    single_stats = get_text_stats("word")
    assert single_stats["words"] == 1
    
    # Multiple spaces and newlines
    complex_text = "word1   word2\n\n\nword3"
    complex_stats = get_text_stats(complex_text)
    assert complex_stats["words"] == 3
    assert complex_stats["lines"] == 4


def test_categorize_text_size_boundaries():
    """Test size categorization boundary conditions"""
    assert categorize_text_size(0) == "tiny"
    assert categorize_text_size(499) == "tiny"
    assert categorize_text_size(500) == "small"  # At 500 chars = small
    assert categorize_text_size(1999) == "small"
    assert categorize_text_size(2000) == "medium"  # At 2000 = medium
    assert categorize_text_size(7999) == "medium"
    assert categorize_text_size(8000) == "large"  # At 8000 = large
    assert categorize_text_size(19999) == "large"
    assert categorize_text_size(20000) == "very_large"


def test_extract_from_text_encoding():
    """Test text extraction with various encodings"""
    # UTF-8 with special characters
    utf8_text = "Café résumé naïve".encode("utf-8")
    result = extract_from_text(utf8_text)
    assert "Café" in result
    assert "résumé" in result
    
    # ASCII text
    ascii_text = b"Simple ASCII text"
    result = extract_from_text(ascii_text)
    assert result == "Simple ASCII text"


def test_validate_file_size_boundary():
    """Test file size validation at exact boundary"""
    # Exactly 1MB (within limit)
    content_1mb = b"x" * (1 * 1024 * 1024)
    file_1mb = MockFile("1mb.txt", content_1mb)
    validate_file_size(file_1mb(), max_size_mb=1)  # Should not raise
    
    # Just over 1MB
    content_over = b"x" * (1 * 1024 * 1024 + 1)
    file_over = MockFile("over.txt", content_over)
    with pytest.raises(HTTPException):
        validate_file_size(file_over(), max_size_mb=1)


def test_parse_document_large_text():
    """Test parsing very large documents"""
    large_text = "This is a sentence. " * 10000  # ~200KB
    result = parse_document(large_text)
    
    assert result["text"] == large_text
    assert result["metadata"]["stats"]["size_category"] == "very_large"
    assert result["metadata"]["stats"]["words"] == 40000


def test_extract_from_docx_error_handling():
    """Test DOCX extraction error handling"""
    # Invalid DOCX content
    invalid_content = b"Not a DOCX file"
    with pytest.raises(Exception):
        extract_from_docx(invalid_content)


def test_extract_from_pdf_empty():
    """Test PDF extraction with empty/invalid content"""
    from fastapi import HTTPException
    invalid_content = b"Not a PDF"
    with pytest.raises(HTTPException):
        extract_from_pdf(invalid_content)


def test_parse_document_with_metadata():
    """Test document parsing returns proper metadata"""
    text = "This is a test document with some content."
    result = parse_document(text)
    assert "metadata" in result
    assert "stats" in result["metadata"]
    assert "words" in result["metadata"]["stats"]
    assert "characters" in result["metadata"]["stats"]
