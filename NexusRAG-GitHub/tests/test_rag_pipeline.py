"""Tests for complete RAG engine orchestration, prompt guardrails, and source attribution.
"""
import pytest
from src.llm.rag_engine import RAGEngine
from src.retrieval.adaptive_retriever import AdaptiveRetriever
from src.retrieval.vector_store import FAISSVectorStore
from src.embeddings.embedder import get_embedding_service
from src.document_processing.pdf_extractor import PDFExtractor
from src.document_processing.text_chunker import TextChunker

def test_rag_query_with_sources(sample_pdf_path):
    extractor = PDFExtractor()
    chunker = TextChunker()
    doc = extractor.extract_from_path(sample_pdf_path)
    chunks = chunker.chunk_document(doc)
    
    embedder = get_embedding_service()
    embeddings = embedder.embed_texts([c.text for c in chunks])
    
    store = FAISSVectorStore()
    store.add_chunks(chunks, embeddings)
    
    retriever = AdaptiveRetriever(vector_store=store)
    engine = RAGEngine(retriever=retriever)
    
    response = engine.query("What is Google Cloud Run?")
    assert response.query == "What is Google Cloud Run?"
    assert len(response.answer) > 20
    assert len(response.sources) > 0
    assert response.sources[0].doc_name == "cloud_computing_sample.pdf"
    assert response.total_time_ms > 0

def test_rag_empty_query_raises():
    engine = RAGEngine()
    with pytest.raises(ValueError, match="cannot be empty"):
        engine.query("   ")
