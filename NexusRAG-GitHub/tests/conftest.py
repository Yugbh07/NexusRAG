"""Pytest configuration and shared test fixtures for NexusRAG.
"""
import pytest
import numpy as np
from pathlib import Path
import sys

# Ensure repository root is on Python path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.document_processing.pdf_extractor import ExtractedDocument, ExtractedPage
from src.document_processing.text_chunker import TextChunk
from src.retrieval.vector_store import FAISSVectorStore

@pytest.fixture
def sample_pdf_path():
    path = REPO_ROOT / "data" / "sample" / "cloud_computing_sample.pdf"
    if not path.exists():
        from data.create_sample_pdf import create_sample_pdf
        create_sample_pdf(path)
    return path

@pytest.fixture
def mock_extracted_document():
    pages = [
        ExtractedPage(page_number=1, text="Cloud computing offers scalable, on-demand compute resources across data centers.", char_count=77),
        ExtractedPage(page_number=2, text="Google Cloud Run enables serverless container execution with automated autoscaling.", char_count=84),
        ExtractedPage(page_number=3, text="FAISS provides ultra-fast vector similarity search for dense embeddings in RAG systems.", char_count=87)
    ]
    return ExtractedDocument(
        doc_id="doc_mock_test",
        doc_name="mock_test.pdf",
        total_pages=3,
        pages=pages,
        total_characters=sum(p.char_count for p in pages)
    )

@pytest.fixture
def empty_vector_store():
    store = FAISSVectorStore(dimension=384)
    store.clear()
    return store
