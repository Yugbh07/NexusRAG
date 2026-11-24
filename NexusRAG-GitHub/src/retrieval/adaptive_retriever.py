"""Adaptive Retriever module for NexusRAG.
Implements multi-stage heuristic retrieval escalation and confidence scoring.
"""
import time
from dataclasses import dataclass, field
from typing import List, Tuple, Dict, Any, Optional

from .vector_store import FAISSVectorStore, get_vector_store
from ..embeddings.embedder import EmbeddingService, get_embedding_service
from ..document_processing.text_chunker import TextChunk
from ..config import (
    DEFAULT_TOP_K,
    ESCALATED_TOP_K,
    SIMILARITY_THRESHOLD_CONFIDENT,
    SIMILARITY_THRESHOLD_MINIMUM
)
from ..utils.logger import get_logger

logger = get_logger("nexusrag.adaptive_retriever")

@dataclass
class RetrievalResult:
    """Encapsulates retrieval outputs, diagnostic metrics, and confidence signals."""
    query: str
    chunks: List[TextChunk]
    scores: List[float]
    escalated: bool
    initial_top_k: int
    final_top_k: int
    confidence_score: float
    status: str  # 'CONFIDENT', 'ESCALATED_RECOVERED', 'INSUFFICIENT_EVIDENCE', 'EMPTY_INDEX'
    retrieval_time_ms: float
    heuristics: Dict[str, Any] = field(default_factory=dict)

    @property
    def has_sufficient_evidence(self) -> bool:
        return self.status in ("CONFIDENT", "ESCALATED_RECOVERED")

    @property
    def max_score(self) -> float:
        return max(self.scores) if self.scores else 0.0

    @property
    def avg_score(self) -> float:
        return sum(self.scores) / len(self.scores) if self.scores else 0.0

class AdaptiveRetriever:
    """Orchestrates heuristic-guided multi-stage retrieval.

    Algorithm:
    1. Phase 1 (Initial Search):
       Encode query into a 384-dimensional unit vector and perform cosine similarity search
       using initial Top-K (default=3).
    2. Phase 2 (Confidence Evaluation):
       Compute heuristic metrics:
       - S_max: Highest cosine similarity score.
       - S_avg: Average similarity among retrieved items.
       - Confidence = S_max * 0.7 + S_avg * 0.3
       If S_max < SIMILARITY_THRESHOLD_MINIMUM (0.28):
           Evidence is very weak / likely out of domain.
       If Confidence >= SIMILARITY_THRESHOLD_CONFIDENT (0.52) and S_max >= 0.45:
           Classification: 'CONFIDENT' -> Return immediately (cost/latency optimal).
       Else:
           Classification: 'AMBIGUOUS' -> Trigger escalation.
    3. Phase 3 (Escalation):
       Expand search window to ESCALATED_TOP_K (default=6) to retrieve wider surrounding context.
       Re-evaluate confidence on the expanded set.
       If expanded S_max >= SIMILARITY_THRESHOLD_MINIMUM (0.28):
           Classification: 'ESCALATED_RECOVERED'.
       Else:
           Classification: 'INSUFFICIENT_EVIDENCE'.
    """

    def __init__(
        self,
        vector_store: Optional[FAISSVectorStore] = None,
        embedding_service: Optional[EmbeddingService] = None,
        initial_k: int = DEFAULT_TOP_K,
        escalated_k: int = ESCALATED_TOP_K,
        confident_threshold: float = SIMILARITY_THRESHOLD_CONFIDENT,
        minimum_threshold: float = SIMILARITY_THRESHOLD_MINIMUM
    ):
        self.vector_store = vector_store or get_vector_store()
        self.embedding_service = embedding_service or get_embedding_service()
        self.initial_k = initial_k
        self.escalated_k = escalated_k
        self.confident_threshold = confident_threshold
        self.minimum_threshold = minimum_threshold

    def retrieve(self, query: str) -> RetrievalResult:
        """Executes adaptive retrieval for the given natural language query."""
        start_time = time.perf_counter()

        # Handle empty index
        if self.vector_store.total_chunks == 0:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.warning("AdaptiveRetriever called with 0 chunks in vector store.")
            return RetrievalResult(
                query=query,
                chunks=[],
                scores=[],
                escalated=False,
                initial_top_k=self.initial_k,
                final_top_k=0,
                confidence_score=0.0,
                status="EMPTY_INDEX",
                retrieval_time_ms=round(elapsed_ms, 2),
                heuristics={"reason": "No documents currently indexed in vector store."}
            )

        # 1. Embed query
        query_vec = self.embedding_service.embed_query(query)

        # 2. Stage 1: Initial search (Top-K = 3)
        initial_results: List[Tuple[TextChunk, float]] = self.vector_store.search(
            query_vector=query_vec,
            top_k=self.initial_k
        )

        initial_chunks = [r[0] for r in initial_results]
        initial_scores = [r[1] for r in initial_results]

        s_max = max(initial_scores) if initial_scores else 0.0
        s_avg = (sum(initial_scores) / len(initial_scores)) if initial_scores else 0.0
        # Heuristic confidence calculation
        confidence = (0.7 * s_max) + (0.3 * s_avg)

        # 3. Assess retrieval quality
        is_confident = (confidence >= self.confident_threshold) and (s_max >= 0.45)
        is_severely_out_of_domain = (s_max < (self.minimum_threshold - 0.05))

        if is_confident and not is_severely_out_of_domain:
            # Confident match - no need to escalate
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            logger.info(
                f"AdaptiveRetriever: Confident match (Score={s_max:.3f}, Conf={confidence:.3f}). "
                f"Retrieved {len(initial_chunks)} chunks without escalation."
            )
            return RetrievalResult(
                query=query,
                chunks=initial_chunks,
                scores=initial_scores,
                escalated=False,
                initial_top_k=self.initial_k,
                final_top_k=len(initial_chunks),
                confidence_score=confidence,
                status="CONFIDENT",
                retrieval_time_ms=round(elapsed_ms, 2),
                heuristics={
                    "stage": 1,
                    "s_max": round(s_max, 4),
                    "s_avg": round(s_avg, 4),
                    "escalation_triggered": False
                }
            )

        # 4. Stage 2: Escalation to expanded Top-K (e.g., 6)
        logger.info(
            f"AdaptiveRetriever: Weak/Ambiguous initial confidence ({confidence:.3f} < {self.confident_threshold}). "
            f"Escalating search from K={self.initial_k} to K={self.escalated_k}..."
        )

        escalated_results: List[Tuple[TextChunk, float]] = self.vector_store.search(
            query_vector=query_vec,
            top_k=self.escalated_k
        )

        escalated_chunks = [r[0] for r in escalated_results]
        escalated_scores = [r[1] for r in escalated_results]

        esc_max = max(escalated_scores) if escalated_scores else 0.0
        esc_avg = (sum(escalated_scores) / len(escalated_scores)) if escalated_scores else 0.0
        esc_confidence = (0.7 * esc_max) + (0.3 * esc_avg)

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if esc_max >= self.minimum_threshold:
            status = "ESCALATED_RECOVERED"
            logger.info(f"AdaptiveRetriever: Escalation recovered context (Score={esc_max:.3f}). Status: {status}")
        else:
            status = "INSUFFICIENT_EVIDENCE"
            logger.warning(f"AdaptiveRetriever: Even after escalation, evidence is weak (Score={esc_max:.3f} < {self.minimum_threshold}).")

        return RetrievalResult(
            query=query,
            chunks=escalated_chunks,
            scores=escalated_scores,
            escalated=True,
            initial_top_k=self.initial_k,
            final_top_k=len(escalated_chunks),
            confidence_score=esc_confidence,
            status=status,
            retrieval_time_ms=round(elapsed_ms, 2),
            heuristics={
                "stage": 2,
                "initial_s_max": round(s_max, 4),
                "escalated_s_max": round(esc_max, 4),
                "escalated_s_avg": round(esc_avg, 4),
                "escalation_triggered": True,
                "threshold_required": self.minimum_threshold
            }
        )
