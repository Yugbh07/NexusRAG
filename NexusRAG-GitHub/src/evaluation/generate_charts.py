"""Generates publication-quality charts from actual collected benchmark results.
"""
import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

from ..config import BASE_DIR

def generate_charts():
    results_path = BASE_DIR / "research" / "results" / "benchmark_results.json"
    diagrams_dir = BASE_DIR / "research" / "diagrams"
    diagrams_dir.mkdir(parents=True, exist_ok=True)

    if not results_path.exists():
        print(f"Error: {results_path} not found. Run benchmark first.")
        return

    with open(results_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    summary = data["summary"]
    cfg_a = summary["config_a_basic_rag"]
    cfg_b = summary["config_b_adaptive_rag"]

    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # -------------------------------------------------------------
    # Chart 1: Retrieval Quality Comparison (MRR & Recall@K)
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7, 5))
    metrics = ["MRR (Mean Reciprocal Rank)", "Recall@K"]
    basic_vals = [cfg_a["mrr"], cfg_a["recall"]]
    adaptive_vals = [cfg_b["mrr"], cfg_b["recall"]]

    x = np.arange(len(metrics))
    width = 0.35

    rects1 = ax.bar(x - width/2, basic_vals, width, label="Basic RAG (Fixed K=3)", color="#64748b")
    rects2 = ax.bar(x + width/2, adaptive_vals, width, label="Adaptive RAG (NexusRAG)", color="#0284c7")

    ax.set_ylabel("Score (0.0 to 1.0)", fontsize=11, fontweight="bold")
    ax.set_title("Retrieval Quality: Basic RAG vs. Adaptive RAG", fontsize=13, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels(metrics, fontsize=10, fontweight="bold")
    ax.set_ylim(0, 1.15)
    ax.legend(frameon=True, loc="upper right")

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f"{height:.2f}",
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 4),
                        textcoords="offset points",
                        ha="center", va="bottom", fontsize=10, fontweight="bold")

    autolabel(rects1)
    autolabel(rects2)

    plt.tight_layout()
    chart1_path = diagrams_dir / "retrieval_quality_mrr.png"
    plt.savefig(chart1_path, dpi=300)
    plt.close()
    print(f"Generated chart: {chart1_path}")

    # -------------------------------------------------------------
    # Chart 2: Latency & Computational Overhead Comparison
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6, 5))
    categories = ["Basic RAG (K=3)", "Adaptive RAG (NexusRAG)"]
    latencies = [cfg_a["avg_latency_ms"], cfg_b["avg_latency_ms"]]
    colors = ["#475569", "#0ea5e9"]

    bars = ax.bar(categories, latencies, color=colors, width=0.45)
    ax.set_ylabel("Mean Retrieval Latency (ms)", fontsize=11, fontweight="bold")
    ax.set_title("Retrieval Latency Comparison", fontsize=13, fontweight="bold", pad=12)
    ax.set_ylim(0, max(latencies) * 1.35)

    for bar in bars:
        height = bar.get_height()
        ax.annotate(f"{height:.2f} ms",
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4),
                    textcoords="offset points",
                    ha="center", va="bottom", fontsize=10, fontweight="bold")

    plt.tight_layout()
    chart2_path = diagrams_dir / "latency_comparison.png"
    plt.savefig(chart2_path, dpi=300)
    plt.close()
    print(f"Generated chart: {chart2_path}")

    # -------------------------------------------------------------
    # Chart 3: Adaptive Retrieval Status Distribution
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6, 5))
    statuses = {}
    for item in data["config_b"]:
        st = item["status"]
        statuses[st] = statuses.get(st, 0) + 1

    labels = list(statuses.keys())
    sizes = list(statuses.values())
    colors_pie = ["#10b981", "#f59e0b", "#ef4444", "#6366f1"][:len(labels)]

    wedges, texts, autotexts = ax.pie(
        sizes, labels=labels, autopct="%1.1f%%",
        startangle=140, colors=colors_pie,
        wedgeprops=dict(width=0.4, edgecolor="w")
    )
    for at in autotexts:
        at.set_color("white")
        at.set_fontsize(10)
        at.set_weight("bold")

    ax.set_title("Adaptive RAG Query Decision Breakdown", fontsize=13, fontweight="bold", pad=12)
    plt.tight_layout()
    chart3_path = diagrams_dir / "adaptive_escalation_distribution.png"
    plt.savefig(chart3_path, dpi=300)
    plt.close()
    print(f"Generated chart: {chart3_path}")

if __name__ == "__main__":
    generate_charts()
