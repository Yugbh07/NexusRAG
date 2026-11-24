"""Embedding Service module for NexusRAG.
Provides singleton dense vector generation using SentenceTransformers with L2 normalization.
"""
from typing import List, Union
import numpy as np
from sentence_transformers import SentenceTransformer

from ..config import EMBEDDING_MODEL_NAME, EMBEDDING_DIMENSION
from ..utils.logger import get_logger

logger = get_logger("nexusrag.embedder")

_embedding_instance = None

class EmbeddingService:
    """Manages model loading and inference for dense text embeddings."""

    def __init__(self, model_name: str = EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        self.dimension = EMBEDDING_DIMENSION
        logger.info(f"Initializing EmbeddingService with model: {model_name}...")
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Model '{model_name}' loaded successfully. Vector dimension: {self.dimension}")
        except Exception as e:
            logger.error(f"Failed to load embedding model '{model_name}': {e}")
            raise RuntimeError(f"Could not initialize embedding model: {e}")

    def embed_texts(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generates normalized vector embeddings for a list of text strings.

        Returns:
            np.ndarray: 2D array of shape (N, dimension) of dtype float32, normalized to unit length.
        """
        if not texts:
            return np.empty((0, self.dimension), dtype="float32")

        # Sanitize texts (replace empty/whitespace with a single space to avoid tokenizer errors)
        sanitized = [t.strip() if (t and t.strip()) else " " for t in texts]

        embeddings = self.model.encode(
            sanitized,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,  # Crucial: cosine similarity == inner product
            convert_to_numpy=True
        )
        return embeddings.astype("float32")

    def embed_query(self, query: str) -> np.ndarray:
        """Generates a normalized 1D vector embedding for a single user query.

        Returns:
            np.ndarray: 1D array of shape (dimension,) of dtype float32.
        """
        if not query or not query.strip():
            raise ValueError("Query string cannot be empty.")

        query_emb = self.model.encode(
            [query.strip()],
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return query_emb[0].astype("float32")

def get_embedding_service(model_name: str = EMBEDDING_MODEL_NAME) -> EmbeddingService:
    """Singleton accessor to ensure model is loaded only once across the application."""
    global _embedding_instance
    if _embedding_instance is None:
        _embedding_instance = EmbeddingService(model_name)
    return _embedding_instance
