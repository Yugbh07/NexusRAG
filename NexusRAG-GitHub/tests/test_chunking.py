"""Tests for semantic text chunking and metadata preservation.
"""
import pytest
from src.document_processing.text_chunker import TextChunker

def test_chunking_metadata_and_count(mock_extracted_document):
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    chunks = chunker.chunk_document(mock_extracted_document)
    
    assert len(chunks) >= 3
    for chunk in chunks:
        assert chunk.doc_id == "doc_mock_test"
        assert chunk.doc_name == "mock_test.pdf"
        assert chunk.page_number in [1, 2, 3]
        assert chunk.chunk_id.startswith("doc_mock_test_p")
        assert len(chunk.text) > 0
        assert chunk.character_count == len(chunk.text)

def test_chunking_overlap_validation():
    with pytest.raises(ValueError, match="chunk_overlap.*must be strictly less than"):
        TextChunker(chunk_size=200, chunk_overlap=200)

def test_chunk_serialization_roundtrip(mock_extracted_document):
    chunker = TextChunker(chunk_size=150, chunk_overlap=30)
    chunks = chunker.chunk_document(mock_extracted_document)
    first = chunks[0]
    data = first.to_dict()
    reconstructed = first.from_dict(data)
    
    assert reconstructed.chunk_id == first.chunk_id
    assert reconstructed.text == first.text
    assert reconstructed.page_number == first.page_number
