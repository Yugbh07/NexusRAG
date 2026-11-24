"""Tests for embedding service and vector normalization.
"""
import pytest
import numpy as np
from src.embeddings.embedder import get_embedding_service

def test_embedder_dimension_and_shape():
    embedder = get_embedding_service()
    texts = ["Cloud computing is scalable.", "Google Cloud Run manages containers."]
    embeddings = embedder.embed_texts(texts)
    
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (2, 384)
    assert embeddings.dtype == np.float32

def test_embedder_normalization():
    embedder = get_embedding_service()
    vec = embedder.embed_query("Elastic scaling in Kubernetes")
    
    assert vec.ndim == 1
    assert vec.shape == (384,)
    # L2 Norm of normalized vector should be approximately 1.0
    norm = np.linalg.norm(vec)
    assert np.isclose(norm, 1.0, atol=1e-4)

def test_embedder_empty_input():
    embedder = get_embedding_service()
    res = embedder.embed_texts([])
    assert res.shape == (0, 384)

def test_embedder_empty_query_raises():
    embedder = get_embedding_service()
    with pytest.raises(ValueError, match="cannot be empty"):
        embedder.embed_query("   ")
