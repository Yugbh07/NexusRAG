"""Tests for FAISS vector store indexing, similarity search, and persistence.
"""
import pytest
import numpy as np
from src.retrieval.vector_store import FAISSVectorStore
from src.document_processing.text_chunker import TextChunk

def test_add_and_search_vector_store(empty_vector_store):
    store = empty_vector_store
    assert store.total_chunks == 0

    chunk1 = TextChunk("c1", "d1", "doc1.pdf", 1, 0, "Cloud computing IaaS PaaS SaaS", 30)
    chunk2 = TextChunk("c2", "d1", "doc1.pdf", 1, 1, "Cooking pasta with tomato sauce", 31)

    # Mock normalized vectors
    v1 = np.zeros((1, 384), dtype="float32")
    v1[0, 0] = 1.0  # Unit vector along axis 0
    v2 = np.zeros((1, 384), dtype="float32")
    v2[0, 1] = 1.0  # Unit vector along axis 1
    embeddings = np.vstack([v1, v2])

    store.add_chunks([chunk1, chunk2], embeddings)
    assert store.total_chunks == 2
    assert store.total_documents == 1

    # Query matching chunk 1
    query_vec = np.zeros(384, dtype="float32")
    query_vec[0] = 1.0

    results = store.search(query_vec, top_k=2)
    assert len(results) == 2
    # First result should be chunk1 with cosine similarity = 1.0
    top_chunk, top_score = results[0]
    assert top_chunk.chunk_id == "c1"
    assert np.isclose(top_score, 1.0, atol=1e-4)

def test_search_empty_store(empty_vector_store):
    query_vec = np.ones(384, dtype="float32")
    results = empty_vector_store.search(query_vec, top_k=3)
    assert results == []

def test_persistence_roundtrip(empty_vector_store, tmp_path):
    store = empty_vector_store
    chunk = TextChunk("c1", "d1", "doc1.pdf", 1, 0, "Serverless architecture", 23)
    vec = np.zeros((1, 384), dtype="float32")
    vec[0, 0] = 1.0
    store.add_chunks([chunk], vec)

    idx_file = tmp_path / "test.index"
    meta_file = tmp_path / "test.json"
    store.save_to_disk(idx_file, meta_file)

    assert idx_file.exists()
    assert meta_file.exists()

    new_store = FAISSVectorStore(dimension=384)
    loaded = new_store.load_from_disk(idx_file, meta_file)
    assert loaded is True
    assert new_store.total_chunks == 1
    assert new_store.chunks[0].chunk_id == "c1"
