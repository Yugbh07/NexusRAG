"""Tests for Adaptive Retrieval escalation heuristics.
"""
import pytest
import numpy as np
from src.retrieval.vector_store import FAISSVectorStore
from src.retrieval.adaptive_retriever import AdaptiveRetriever
from src.document_processing.text_chunker import TextChunk
from src.embeddings.embedder import get_embedding_service

def test_adaptive_retrieval_empty_index(empty_vector_store):
    retriever = AdaptiveRetriever(vector_store=empty_vector_store)
    res = retriever.retrieve("What is cloud computing?")
    assert res.status == "EMPTY_INDEX"
    assert res.escalated is False
    assert len(res.chunks) == 0

def test_adaptive_retrieval_confident(sample_pdf_path):
    # Ingest sample PDF
    from src.document_processing.pdf_extractor import PDFExtractor
    from src.document_processing.text_chunker import TextChunker
    
    extractor = PDFExtractor()
    chunker = TextChunker()
    doc = extractor.extract_from_path(sample_pdf_path)
    chunks = chunker.chunk_document(doc)
    
    embedder = get_embedding_service()
    embeddings = embedder.embed_texts([c.text for c in chunks])
    
    store = FAISSVectorStore()
    store.add_chunks(chunks, embeddings)
    
    retriever = AdaptiveRetriever(vector_store=store, initial_k=3, escalated_k=6)
    
    # Highly relevant query
    res = retriever.retrieve("What is Google Cloud Run and how does it scale?")
    assert res.status == "CONFIDENT"
    assert res.escalated is False
    assert len(res.chunks) == 3
    assert res.max_score >= 0.50

def test_adaptive_retrieval_escalation(sample_pdf_path):
    from src.document_processing.pdf_extractor import PDFExtractor
    from src.document_processing.text_chunker import TextChunker
    
    extractor = PDFExtractor()
    chunker = TextChunker()
    doc = extractor.extract_from_path(sample_pdf_path)
    chunks = chunker.chunk_document(doc)
    embedder = get_embedding_service()
    embeddings = embedder.embed_texts([c.text for c in chunks])
    
    store = FAISSVectorStore()
    store.add_chunks(chunks, embeddings)
    
    # Set high confident threshold so an ambiguous query triggers escalation
    retriever = AdaptiveRetriever(
        vector_store=store,
        initial_k=3,
        escalated_k=6,
        confident_threshold=0.85,  # Deliberately strict to test escalation path
        minimum_threshold=0.25
    )
    
    res = retriever.retrieve("Explain computing resources and sharing")
    assert res.escalated is True
    assert res.status in ("ESCALATED_RECOVERED", "INSUFFICIENT_EVIDENCE")
    assert len(res.chunks) <= 6
