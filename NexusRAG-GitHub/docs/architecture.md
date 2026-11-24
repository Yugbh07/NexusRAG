# NexusRAG Architecture Documentation

## 1. System Overview
NexusRAG is an intelligent, cloud-native document intelligence platform designed to ingest PDF documents, index their semantic contents in a dense vector database, and provide natural-language question answering grounded in document evidence.

```
+-----------------------------------------------------------------------------------+
|                                NexusRAG Platform                                  |
+-----------------------------------------------------------------------------------+
|  [Streamlit UI Dashboard] <---> [Adaptive Retriever] <---> [FAISS Vector Store]   |
|            |                             |                             |          |
|            v                             v                             v          |
|    [Document Ingestion]         [Heuristic Evaluator]          [Dense Embeddings] |
|   (pypdf + Chunker)             (K=3 -> K=6 Escalation)      (all-MiniLM-L6-v2)   |
|            |                             |                             |          |
|            v                             v                             v          |
|   [Storage Abstraction]        [Context Grounding]            [Google Gemini API] |
|    (Local FS / GCS)            (Strict Citations)             (gemini-2.5-flash)  |
+-----------------------------------------------------------------------------------+
```

---

## 2. Core Architectural Components

### 2.1 Document Processing (`src/document_processing/`)
- **PDFExtractor:** Uses `pypdf.PdfReader` to extract text page-by-page. Normalizes irregular whitespace, collapses redundant linebreaks, and tags each extracted page with its 1-indexed page number and character count.
- **TextChunker:** Implements a boundary-aware sliding window:
  - Default chunk size: $600$ characters ($\approx 120\text{--}150$ words).
  - Default chunk overlap: $120$ characters ($\approx 25\text{--}30$ words).
  - Boundary splitting: Searches for the nearest paragraph break (`\n\n`), sentence terminator (`. `, `? `, `! `), line break (`\n`), or word boundary (` `) within a 100-character trailing window, preventing truncated words.
  - Metadata: Every chunk carries `chunk_id`, `doc_id`, `doc_name`, `page_number`, `chunk_index`, and `character_count`.

### 2.2 Embedding Engine (`src/embeddings/`)
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Dimensions: $384$
- Normalization: Every vector is explicitly $L_2$-normalized during inference (`normalize_embeddings=True`).
- Optimization: Singleton pattern ensures weights are loaded into CPU memory once and reused across all requests.

### 2.3 Vector Store (`src/retrieval/vector_store.py`)
- Engine: Facebook AI Similarity Search (`faiss-cpu`)
- Index Type: `faiss.IndexFlatIP` (Flat Inner Product)
- Mathematical Principle:
  $$\mathbf{u}_{\text{norm}} \cdot \mathbf{v}_{\text{norm}} = \frac{\mathbf{u} \cdot \mathbf{v}}{\|\mathbf{u}\|_2 \|\mathbf{v}\|_2} = \cos(\theta)$$
  Because the vectors are unit-length, the inner product equals cosine similarity, bounded between $-1.0$ and $+1.0$.
- Persistence: Serialized to `data/index/nexus_faiss.index` and metadata JSON at `data/index/nexus_metadata.json`.

### 2.4 Adaptive Retriever (`src/retrieval/adaptive_retriever.py`)
Dynamic multi-stage retrieval algorithm:
1. **Initial Search:** Retrieves Top-$K_1 = 3$ chunks.
2. **Confidence Heuristic:**
   $$\text{Confidence} = 0.7 \cdot S_{\max} + 0.3 \cdot S_{\text{avg}}$$
3. **Escalation Trigger:**
   - If $\text{Confidence} \ge 0.52$ and $S_{\max} \ge 0.45$: Returns `CONFIDENT` status.
   - Else: Dynamically escalates search to Top-$K_2 = 6$.
4. **Out-of-Domain Guardrail:**
   - If escalated $S_{\max} < 0.28$: Asserts `INSUFFICIENT_EVIDENCE` status. The system explicitly declines to answer rather than hallucinating.

### 2.5 Generative Synthesis (`src/llm/`)
- Primary Provider: Google Gemini API (`google-genai` SDK)
- Default Model: `gemini-2.5-flash` (with automatic fallback to `gemini-1.5-flash`)
- Prompt Guardrails:
  - System instructions treat retrieved context strictly as evidence, never executable commands.
  - Mandatory citation format: `[Document: <name>, Page: <number>]`.
- Offline Grounded Synthesizer: When running without an API key or when network is offline, synthesizes an evidence summary directly from retrieved chunks, ensuring the system never crashes.

### 2.6 Storage Abstraction (`src/storage/`)
- Unified interface `StorageBackend`:
  - `LocalStorageBackend`: Filesystem storage in `data/storage/`.
  - `GCSStorageBackend`: Cloud object storage in Google Cloud Storage (`gs://<bucket_name>`).
