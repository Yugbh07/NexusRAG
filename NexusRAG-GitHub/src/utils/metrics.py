"""Metrics and timing utilities for NexusRAG.
Collects real operational metrics for performance analysis and UI dashboards.
"""
import time
from typing import Dict, Any

class PerformanceTracker:
    """Tracks latency and execution stages for RAG queries."""

    def __init__(self):
        self.metrics: Dict[str, Any] = {
            "query_count": 0,
            "total_retrieval_ms": 0.0,
            "total_generation_ms": 0.0,
            "escalations_count": 0,
            "queries": []
        }

    def record_query(self, query: str, retrieval_ms: float, generation_ms: float,
                     chunks_retrieved: int, escalated: bool, confidence: float,
                     answer_length: int):
        self.metrics["query_count"] += 1
        self.metrics["total_retrieval_ms"] += retrieval_ms
        self.metrics["total_generation_ms"] += generation_ms
        if escalated:
            self.metrics["escalations_count"] += 1

        record = {
            "query": query,
            "retrieval_ms": round(retrieval_ms, 2),
            "generation_ms": round(generation_ms, 2),
            "total_latency_ms": round(retrieval_ms + generation_ms, 2),
            "chunks_retrieved": chunks_retrieved,
            "escalated": escalated,
            "confidence": round(confidence, 4),
            "answer_length": answer_length,
            "timestamp": time.time()
        }
        self.metrics["queries"].append(record)
        return record

    def get_summary(self) -> Dict[str, Any]:
        count = self.metrics["query_count"]
        if count == 0:
            return {
                "queries_answered": 0,
                "avg_retrieval_ms": 0.0,
                "avg_generation_ms": 0.0,
                "avg_total_latency_ms": 0.0,
                "escalation_rate_pct": 0.0
            }
        return {
            "queries_answered": count,
            "avg_retrieval_ms": round(self.metrics["total_retrieval_ms"] / count, 2),
            "avg_generation_ms": round(self.metrics["total_generation_ms"] / count, 2),
            "avg_total_latency_ms": round((self.metrics["total_retrieval_ms"] + self.metrics["total_generation_ms"]) / count, 2),
            "escalation_rate_pct": round((self.metrics["escalations_count"] / count) * 100, 1)
        }

def format_latency(ms: float) -> str:
    """Formats milliseconds into readable seconds or ms."""
    if ms >= 1000:
        return f"{ms / 1000.0:.2f} s"
    return f"{ms:.0f} ms"
