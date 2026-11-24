"""Tests for PDF text extraction and error recovery.
"""
import pytest
from pathlib import Path
from src.document_processing.pdf_extractor import PDFExtractor

def test_extract_valid_pdf(sample_pdf_path):
    extractor = PDFExtractor()
    doc = extractor.extract_from_path(sample_pdf_path)
    assert doc.doc_name == "cloud_computing_sample.pdf"
    assert doc.total_pages == 3
    assert len(doc.pages) == 3
    assert doc.total_characters > 1000
    assert "Cloud Computing" in doc.full_text

def test_extract_empty_bytes():
    extractor = PDFExtractor()
    with pytest.raises(ValueError, match="empty"):
        extractor.extract_from_bytes(b"", "empty.pdf")

def test_extract_corrupted_pdf_bytes():
    extractor = PDFExtractor()
    with pytest.raises(ValueError, match="Invalid or corrupted"):
        extractor.extract_from_bytes(b"NOT_A_VALID_PDF_STREAM_HEADER", "corrupt.pdf")

def test_unsupported_file_extension(tmp_path):
    fake_txt = tmp_path / "notes.txt"
    fake_txt.write_text("hello world")
    extractor = PDFExtractor()
    with pytest.raises(ValueError, match="Unsupported file type"):
        extractor.extract_from_path(fake_txt)

def test_clean_text_whitespace():
    raw = "Cloud   Computing \r\n\r\n is  awesome! \n\n\n\n Highly   scalable. "
    cleaned = PDFExtractor.clean_text(raw)
    assert "   " not in cleaned
    assert "\r" not in cleaned
    assert "\n\n\n" not in cleaned
