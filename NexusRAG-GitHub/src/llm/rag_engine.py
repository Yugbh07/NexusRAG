"""RAG Engine module for NexusRAG.
Coordinates the end-to-end question answering pipeline:
Query -> Embedding -> Adaptive Retrieval -> Prompt Assembly -> LLM Synthesis -> Source Attribution.
"""
import time
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from .gemini_client import GeminiClient, get_gemini_client
from ..retrieval.adaptive_retriever import AdaptiveRetriever, RetrievalResult
from ..retrieval.vector_store import get_vector_store
from ..embeddings.embedder import get_embedding_service
from ..utils.metrics import PerformanceTracker
from ..utils.logger import get_logger

logger = get_logger("nexusrag.rag_engine")

@dataclass
class SourceReference:
    doc_name: str
    page_number: int
    chunk_id: str
    similarity_score: float
    excerpt: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_name": self.doc_name,
            "page_number": self.page_number,
            "chunk_id": self.chunk_id,
            "similarity_score": round(self.similarity_score, 4),
            "excerpt": self.excerpt
        }

@dataclass
class RAGResponse:
    query: str
    answer: str
    retrieval_result: RetrievalResult
    sources: List[SourceReference]
    model_used: str
    is_offline: bool
    retrieval_time_ms: float
    generation_time_ms: float
    total_time_ms: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "answer": self.answer,
            "sources": [s.to_dict() for s in self.sources],
            "model_used": self.model_used,
            "is_offline": self.is_offline,
            "retrieval_status": self.retrieval_result.status,
            "escalated": self.retrieval_result.escalated,
            "confidence_score": round(self.retrieval_result.confidence_score, 4),
            "retrieval_time_ms": self.retrieval_time_ms,
            "generation_time_ms": self.generation_time_ms,
            "total_time_ms": self.total_time_ms
        }

class RAGEngine:
    """High-level facade orchestrating document search and context-grounded response generation."""

    def __init__(
        self,
        retriever: Optional[AdaptiveRetriever] = None,
        llm_client: Optional[GeminiClient] = None,
        performance_tracker: Optional[PerformanceTracker] = None
    ):
        self.retriever = retriever or AdaptiveRetriever(
            vector_store=get_vector_store(),
            embedding_service=get_embedding_service()
        )
        self.llm_client = llm_client or get_gemini_client()
        self.tracker = performance_tracker or PerformanceTracker()

    def query(self, question: str) -> RAGResponse:
        """Executes full RAG workflow for a given user question."""
        overall_start = time.perf_counter()
        clean_question = question.strip()
        if not clean_question:
            raise ValueError("Query string cannot be empty.")

        # 1. Adaptive Retrieval
        retrieval_result = self.retriever.retrieve(clean_question)

        # 2. LLM / Synthesizer Generation
        llm_output = self.llm_client.generate_grounded_answer(
            query=clean_question,
            retrieved_chunks=retrieval_result.chunks,
            retrieval_status=retrieval_result.status
        )

        overall_elapsed_ms = (time.perf_counter() - overall_start) * 1000.0

        # 3. Format Source References
        sources: List[SourceReference] = []
        for chunk, score in zip(retrieval_result.chunks, retrieval_result.scores):
            sources.append(SourceReference(
                doc_name=chunk.doc_name,
                page_number=chunk.page_number,
                chunk_id=chunk.chunk_id,
                similarity_score=score,
                excerpt=chunk.text[:250] + ("..." if len(chunk.text) > 250 else "")
            ))

        # 4. Record Metrics
        self.tracker.record_query(
            query=clean_question,
            retrieval_ms=retrieval_result.retrieval_time_ms,
            generation_ms=llm_output["generation_time_ms"],
            chunks_retrieved=len(retrieval_result.chunks),
            escalated=retrieval_result.escalated,
            confidence=retrieval_result.confidence_score,
            answer_length=len(llm_output["answer"])
        )

        logger.info(
            f"RAG query completed in {overall_elapsed_ms:.1f}ms "
            f"(Retrieval: {retrieval_result.retrieval_time_ms:.1f}ms, "
            f"LLM: {llm_output['generation_time_ms']:.1f}ms, "
            f"Status: {retrieval_result.status}, Escalated: {retrieval_result.escalated})"
        )

        return RAGResponse(
            query=clean_question,
            answer=llm_output["answer"],
            retrieval_result=retrieval_result,
            sources=sources,
            model_used=llm_output["model_used"],
            is_offline=llm_output["is_offline"],
            retrieval_time_ms=retrieval_result.retrieval_time_ms,
            generation_time_ms=llm_output["generation_time_ms"],
            total_time_ms=round(overall_elapsed_ms, 2)
        )

_rag_engine_instance = None

def get_rag_engine() -> RAGEngine:
    """Returns singleton RAGEngine instance."""
    global _rag_engine_instance
    if _rag_engine_instance is None:
        _rag_engine_instance = RAGEngine()
    return _rag_engine_instance
