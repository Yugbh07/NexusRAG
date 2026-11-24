"""FAISS Vector Store module for NexusRAG.
Handles vector indexing, similarity search with cosine distance, metadata association, and persistence.
"""
import json
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import faiss

from ..config import EMBEDDING_DIMENSION, FAISS_INDEX_FILE, METADATA_FILE
from ..document_processing.text_chunker import TextChunk
from ..utils.logger import get_logger

logger = get_logger("nexusrag.vector_store")

_vector_store_instance = None

class FAISSVectorStore:
    """In-memory and file-backed FAISS vector index with metadata mapping."""

    def __init__(self, dimension: int = EMBEDDING_DIMENSION):
        self.dimension = dimension
        # IndexFlatIP with normalized vectors computes exact cosine similarity [-1.0, 1.0]
        self.index = faiss.IndexFlatIP(self.dimension)
        self.chunks: List[TextChunk] = []
        self._doc_id_to_indices: Dict[str, List[int]] = {}

    @property
    def total_chunks(self) -> int:
        return len(self.chunks)

    @property
    def total_documents(self) -> int:
        return len(self.get_indexed_documents())

    def get_indexed_documents(self) -> List[Dict[str, Any]]:
        """Returns unique summary of currently indexed documents."""
        docs = {}
        for chunk in self.chunks:
            if chunk.doc_id not in docs:
                docs[chunk.doc_id] = {
                    "doc_id": chunk.doc_id,
                    "doc_name": chunk.doc_name,
                    "chunk_count": 0,
                    "pages": set()
                }
            docs[chunk.doc_id]["chunk_count"] += 1
            docs[chunk.doc_id]["pages"].add(chunk.page_number)

        result = []
        for d in docs.values():
            result.append({
                "doc_id": d["doc_id"],
                "doc_name": d["doc_name"],
                "chunk_count": d["chunk_count"],
                "page_count": len(d["pages"])
            })
        return result

    def add_chunks(self, chunks: List[TextChunk], embeddings: np.ndarray) -> int:
        """Adds text chunks and their normalized embedding vectors into the FAISS index."""
        if len(chunks) == 0:
            return 0
        if embeddings.shape[0] != len(chunks):
            raise ValueError(f"Number of chunks ({len(chunks)}) does not match embeddings ({embeddings.shape[0]})")
        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Vector dimension mismatch: expected {self.dimension}, got {embeddings.shape[1]}")

        # Ensure float32 contiguous array
        vectors = np.ascontiguousarray(embeddings, dtype="float32")

        start_idx = len(self.chunks)
        self.index.add(vectors)
        self.chunks.extend(chunks)

        # Update index mapping
        for i, chunk in enumerate(chunks, start=start_idx):
            if chunk.doc_id not in self._doc_id_to_indices:
                self._doc_id_to_indices[chunk.doc_id] = []
            self._doc_id_to_indices[chunk.doc_id].append(i)

        logger.info(f"Added {len(chunks)} chunks to FAISS store. Total chunks now: {len(self.chunks)}")
        return len(chunks)

    def search(self, query_vector: np.ndarray, top_k: int = 3) -> List[Tuple[TextChunk, float]]:
        """Performs cosine similarity search against indexed chunks.

        Returns:
            List of (TextChunk, similarity_score) sorted descending by similarity.
        """
        if self.total_chunks == 0:
            logger.warning("Search called on empty vector store.")
            return []

        # Prepare query vector
        if query_vector.ndim == 1:
            query_vector = np.expand_dims(query_vector, axis=0)
        query_vector = np.ascontiguousarray(query_vector, dtype="float32")

        actual_k = min(top_k, self.total_chunks)
        scores, indices = self.index.search(query_vector, actual_k)

        results: List[Tuple[TextChunk, float]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1 and idx < len(self.chunks):
                results.append((self.chunks[idx], float(score)))

        return results

    def remove_document(self, doc_id: str) -> bool:
        """Removes all chunks associated with a doc_id and rebuilds index without them."""
        if doc_id not in self._doc_id_to_indices:
            return False

        remaining_chunks = [c for c in self.chunks if c.doc_id != doc_id]
        if not remaining_chunks:
            self.clear()
            return True

        from ..embeddings.embedder import get_embedding_service
        embedder = get_embedding_service()
        texts = [c.text for c in remaining_chunks]
        new_embeddings = embedder.embed_texts(texts)

        # Re-initialize index
        self.index = faiss.IndexFlatIP(self.dimension)
        self.chunks = []
        self._doc_id_to_indices = {}
        self.add_chunks(remaining_chunks, new_embeddings)
        logger.info(f"Removed document {doc_id}. Remaining chunks: {len(self.chunks)}")
        return True

    def clear(self):
        """Clears all vectors and metadata."""
        self.index = faiss.IndexFlatIP(self.dimension)
        self.chunks = []
        self._doc_id_to_indices = {}
        logger.info("Cleared FAISS vector store.")

    def save_to_disk(self, index_path: Optional[Path] = None, metadata_path: Optional[Path] = None):
        """Persists FAISS index binary and metadata JSON to disk."""
        i_path = Path(index_path or FAISS_INDEX_FILE)
        m_path = Path(metadata_path or METADATA_FILE)

        i_path.parent.mkdir(parents=True, exist_ok=True)
        m_path.parent.mkdir(parents=True, exist_ok=True)

        faiss.write_index(self.index, str(i_path))

        serialized_metadata = [chunk.to_dict() for chunk in self.chunks]
        with open(m_path, "w", encoding="utf-8") as f:
            json.dump(serialized_metadata, f, indent=2)

        logger.info(f"Saved FAISS index ({self.total_chunks} chunks) to {i_path} and {m_path}")

    def load_from_disk(self, index_path: Optional[Path] = None, metadata_path: Optional[Path] = None) -> bool:
        """Loads FAISS index binary and metadata JSON from disk if they exist."""
        i_path = Path(index_path or FAISS_INDEX_FILE)
        m_path = Path(metadata_path or METADATA_FILE)

        if not i_path.exists() or not m_path.exists():
            return False

        try:
            loaded_index = faiss.read_index(str(i_path))
            with open(m_path, "r", encoding="utf-8") as f:
                loaded_metadata = json.load(f)

            self.index = loaded_index
            self.chunks = [TextChunk.from_dict(d) for d in loaded_metadata]
            self._doc_id_to_indices = {}
            for i, chunk in enumerate(self.chunks):
                if chunk.doc_id not in self._doc_id_to_indices:
                    self._doc_id_to_indices[chunk.doc_id] = []
                self._doc_id_to_indices[chunk.doc_id].append(i)

            logger.info(f"Loaded FAISS index from disk ({len(self.chunks)} chunks).")
            return True
        except Exception as e:
            logger.error(f"Failed to load FAISS index from disk: {e}")
            return False

def get_vector_store() -> FAISSVectorStore:
    """Singleton accessor for the global application vector store."""
    global _vector_store_instance
    if _vector_store_instance is None:
        _vector_store_instance = FAISSVectorStore()
        # Attempt auto-loading persisted index if present
        _vector_store_instance.load_from_disk()
    return _vector_store_instance
