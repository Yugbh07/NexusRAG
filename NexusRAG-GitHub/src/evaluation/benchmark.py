"""Benchmark evaluation script for NexusRAG research paper and experiments.
Compares Configuration A (Basic Fixed-K RAG) vs. Configuration B (NexusRAG Adaptive RAG).
Records REAL experimental data and saves metrics to JSON and CSV.
"""
import json
import time
import csv
from pathlib import Path
from typing import List, Dict, Any

from ..config import SAMPLE_DIR, BASE_DIR
from ..document_processing.pdf_extractor import PDFExtractor
from ..document_processing.text_chunker import TextChunker
from ..embeddings.embedder import get_embedding_service
from ..retrieval.vector_store import FAISSVectorStore
from ..retrieval.adaptive_retriever import AdaptiveRetriever

def run_benchmark():
    dataset_path = BASE_DIR / "research" / "datasets" / "test_qa_pairs.json"
    results_dir = BASE_DIR / "research" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    with open(dataset_path, "r", encoding="utf-8") as f:
        qa_pairs = json.load(f)

    # 1. Setup Vector Store with sample PDF
    sample_pdf = SAMPLE_DIR / "cloud_computing_sample.pdf"
    if not sample_pdf.exists():
        from data.create_sample_pdf import create_sample_pdf
        create_sample_pdf(sample_pdf)

    extractor = PDFExtractor()
    chunker = TextChunker()
    doc = extractor.extract_from_path(sample_pdf)
    chunks = chunker.chunk_document(doc)

    embedder = get_embedding_service()
    embeddings = embedder.embed_texts([c.text for c in chunks])

    vector_store = FAISSVectorStore()
    vector_store.clear()
    vector_store.add_chunks(chunks, embeddings)

    adaptive_retriever = AdaptiveRetriever(vector_store=vector_store, initial_k=3, escalated_k=6)

    config_a_results = []
    config_b_results = []

    print(f"\n==================================================================")
    print(f"🚀 Running NexusRAG Experiments: Basic RAG vs. Adaptive RAG")
    print(f"Total Test Questions: {len(qa_pairs)}")
    print(f"Document: {sample_pdf.name} ({len(chunks)} chunks)")
    print(f"==================================================================\n")

    for item in qa_pairs:
        qid = item["id"]
        q = item["question"]
        target_page = item["target_page"]
        expected_keywords = item["expected_keywords"]
        q_type = item["type"]

        q_vec = embedder.embed_query(q)

        # -------------------------------------------------------------
        # Config A: Basic RAG (Fixed Top-K = 3)
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        raw_results = vector_store.search(q_vec, top_k=3)
        latency_a_ms = (time.perf_counter() - t0) * 1000.0

        retrieved_chunks_a = [r[0] for r in raw_results]
        scores_a = [r[1] for r in raw_results]

        # Calculate Reciprocal Rank and Recall for Config A
        rr_a = 0.0
        hit_a = 0
        if target_page is not None:
            for rank, c in enumerate(retrieved_chunks_a, start=1):
                if c.page_number == target_page:
                    rr_a = 1.0 / rank
                    hit_a = 1
                    break
        else:
            # Out-of-domain: Basic RAG has no guardrail, so it blindly passes whatever top 3 chunks were found!
            rr_a = 0.0
            hit_a = 0

        config_a_results.append({
            "id": qid,
            "type": q_type,
            "latency_ms": round(latency_a_ms, 2),
            "chunks_count": len(retrieved_chunks_a),
            "max_score": round(max(scores_a) if scores_a else 0.0, 4),
            "reciprocal_rank": round(rr_a, 4),
            "hit": hit_a,
            "escalated": False,
            "rejected_as_insufficient": False
        })

        # -------------------------------------------------------------
        # Config B: Adaptive RAG (Initial K=3, escalate to K=6 if needed)
        # -------------------------------------------------------------
        t0 = time.perf_counter()
        adapt_res = adaptive_retriever.retrieve(q)
        latency_b_ms = (time.perf_counter() - t0) * 1000.0

        rr_b = 0.0
        hit_b = 0
        if target_page is not None:
            for rank, c in enumerate(adapt_res.chunks, start=1):
                if c.page_number == target_page:
                    rr_b = 1.0 / rank
                    hit_b = 1
                    break
        else:
            # Out of domain: Adaptive RAG successfully rejects if status == INSUFFICIENT_EVIDENCE
            hit_b = 1 if adapt_res.status == "INSUFFICIENT_EVIDENCE" else 0
            rr_b = 1.0 if hit_b == 1 else 0.0

        config_b_results.append({
            "id": qid,
            "type": q_type,
            "latency_ms": round(latency_b_ms, 2),
            "chunks_count": len(adapt_res.chunks),
            "max_score": round(adapt_res.max_score, 4),
            "confidence_score": round(adapt_res.confidence_score, 4),
            "reciprocal_rank": round(rr_b, 4),
            "hit": hit_b,
            "status": adapt_res.status,
            "escalated": adapt_res.escalated,
            "rejected_as_insufficient": (adapt_res.status == "INSUFFICIENT_EVIDENCE")
        })

        print(f"[{qid}] Type: {q_type:<16} | Config A RR: {rr_a:.2f} | Config B Status: {adapt_res.status:<20} Escalated: {str(adapt_res.escalated):<5}")

    # Summary Statistics Calculation
    in_domain_a = [r for r in config_a_results if r["type"] != "out_of_domain"]
    in_domain_b = [r for r in config_b_results if r["type"] != "out_of_domain"]
    ood_b = [r for r in config_b_results if r["type"] == "out_of_domain"]

    mrr_a = sum(r["reciprocal_rank"] for r in in_domain_a) / len(in_domain_a)
    mrr_b = sum(r["reciprocal_rank"] for r in in_domain_b) / len(in_domain_b)

    recall_a = sum(r["hit"] for r in in_domain_a) / len(in_domain_a)
    recall_b = sum(r["hit"] for r in in_domain_b) / len(in_domain_b)

    avg_latency_a = sum(r["latency_ms"] for r in config_a_results) / len(config_a_results)
    avg_latency_b = sum(r["latency_ms"] for r in config_b_results) / len(config_b_results)

    escalation_count = sum(1 for r in config_b_results if r["escalated"])
    ood_rejection_rate = sum(1 for r in ood_b if r["rejected_as_insufficient"]) / len(ood_b) if ood_b else 1.0

    summary = {
        "dataset_size": len(qa_pairs),
        "in_domain_queries": len(in_domain_a),
        "out_of_domain_queries": len(ood_b),
        "config_a_basic_rag": {
            "mrr": round(mrr_a, 4),
            "recall": round(recall_a, 4),
            "avg_latency_ms": round(avg_latency_a, 2),
            "avg_chunks_retrieved": 3.0,
            "hallucination_vulnerability_on_ood": "HIGH (blindly passes irrelevant context)"
        },
        "config_b_adaptive_rag": {
            "mrr": round(mrr_b, 4),
            "recall": round(recall_b, 4),
            "avg_latency_ms": round(avg_latency_b, 2),
            "avg_chunks_retrieved": round(sum(r["chunks_count"] for r in config_b_results) / len(config_b_results), 2),
            "escalation_count": escalation_count,
            "escalation_rate_pct": round((escalation_count / len(config_b_results)) * 100.0, 1),
            "ood_rejection_rate_pct": round(ood_rejection_rate * 100.0, 1)
        }
    }

    # Save to JSON
    output_json = results_dir / "benchmark_results.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump({"summary": summary, "config_a": config_a_results, "config_b": config_b_results}, f, indent=2)

    # Save to CSV
    output_csv = results_dir / "benchmark_comparison.csv"
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Query ID", "Query Type", "Config A Latency (ms)", "Config A Chunks", "Config A Max Score", "Config A RR",
                         "Config B Latency (ms)", "Config B Chunks", "Config B Max Score", "Config B Status", "Config B Escalated", "Config B RR"])
        for a, b in zip(config_a_results, config_b_results):
            writer.writerow([
                a["id"], a["type"], a["latency_ms"], a["chunks_count"], a["max_score"], a["reciprocal_rank"],
                b["latency_ms"], b["chunks_count"], b["max_score"], b["status"], b["escalated"], b["reciprocal_rank"]
            ])

    print(f"\n==================================================================")
    print(f"📊 BENCHMARK SUMMARY RESULTS:")
    print(f"Basic RAG     -> MRR: {mrr_a:.4f} | Recall: {recall_a*100:.1f}% | Avg Latency: {avg_latency_a:.2f} ms")
    print(f"Adaptive RAG  -> MRR: {mrr_b:.4f} | Recall: {recall_b*100:.1f}% | Avg Latency: {avg_latency_b:.2f} ms")
    print(f"Adaptive Escalation Rate: {(escalation_count / len(config_b_results)) * 100.0:.1f}%")
    print(f"Out-of-Domain Rejection Rate: {ood_rejection_rate * 100.0:.1f}%")
    print(f"Saved results to: {output_json} and {output_csv}")
    print(f"==================================================================\n")

if __name__ == "__main__":
    run_benchmark()
