"""Retrieval package for FAISS vector search and intelligent adaptive retrieval.
"""
from .vector_store import FAISSVectorStore, get_vector_store
from .adaptive_retriever import AdaptiveRetriever, RetrievalResult

__all__ = ["FAISSVectorStore", "get_vector_store", "AdaptiveRetriever", "RetrievalResult"]
