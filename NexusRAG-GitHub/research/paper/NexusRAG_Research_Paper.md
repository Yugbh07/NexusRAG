# NexusRAG: An Adaptive Retrieval-Augmented Generation Framework for Intelligent Cloud-Based Document Analysis

**Authors:** NexusRAG Engineering & Research Group  
**Affiliation:** Department of Computer Science & Engineering / Cloud Computing Project  
**Date:** November 2026  
**Document Classification:** Academic Major Project Research Paper  

---

## Abstract
Retrieval-Augmented Generation (RAG) has emerged as the premier architectural paradigm for mitigating hallucinations and injecting private domain knowledge into Large Language Models (LLMs). However, conventional RAG systems suffer from two structural shortcomings: (i) static Top-$K$ retrieval that ignores question complexity and retrieval ambiguity, and (ii) monolithic, heavy deployment footprints that fail to exploit modern serverless cloud economics. In this paper, we present **NexusRAG**, an intelligent, cloud-native document question answering platform featuring a dynamic **Adaptive Retrieval mechanism** integrated with Google Cloud Run and the Google Gemini frontier model. NexusRAG implements boundary-aware semantic chunking, dense vector representations via Sentence Transformers (`all-MiniLM-L6-v2`), and exact cosine similarity vector indexing via FAISS (`IndexFlatIP`). To address retrieval ambiguity, NexusRAG computes a heuristic confidence metric ($C = 0.7 \cdot S_{\max} + 0.3 \cdot S_{\text{avg}}$) that conditionally escalates the candidate window from $K=3$ to $K=6$, or asserts an out-of-domain guardrail when evidence is insufficient ($S_{\max} < 0.28$). Experimental evaluation on a structured question-answering benchmark demonstrates that NexusRAG achieves a Mean Reciprocal Rank (MRR) of $1.0000$ on in-domain queries, a $100\%$ rejection precision on out-of-domain queries, and an average retrieval latency of $9.90\text{ ms}$ on standard compute. The system is fully containerized via Docker and provisioned with Google Cloud Run Knative architecture, providing automatic scale-to-zero economics, sub-second horizontal scalability, and enterprise-grade observability.

**Keywords:** Retrieval-Augmented Generation, Adaptive Retrieval, Vector Search, FAISS, Cloud Computing, Serverless, Google Cloud Run, Containerization, Large Language Models.

---

## 1. Introduction
Modern organizations and academic institutions generate vast repositories of unstructured documentation in Portable Document Format (PDF). While foundational Large Language Models (LLMs)—such as Google Gemini, OpenAI GPT-4, and Anthropic Claude—exhibit remarkable reasoning capabilities, their direct application to proprietary corpora is hindered by three fundamental challenges:
1. **Knowledge Boundaries:** Pretrained models lack access to private, unpublished, or dynamic enterprise documentation.
2. **Hallucination:** When prompted on unfamiliar domains, LLMs frequently invent plausible but factually erroneous citations and assertions.
3. **Auditability and Citation:** Foundational models produce text probabilistically without deterministic source attribution to document pages or paragraphs.

Retrieval-Augmented Generation (RAG) resolves these issues by decomposing document analysis into a dual-phase process: a non-parametric dense vector retriever identifies relevant passages from external corpora, and a parametric generative LLM synthesizes an evidence-grounded answer based on those passages.

Despite its conceptual elegance, naive RAG implementations rely on a static retrieval parameter ($K$). Selecting an excessively small $K$ leads to context starvation on nuanced, multi-part questions; conversely, an overly large $K$ floods the LLM context window with irrelevant noise, increasing inference cost and latency while inducing "lost-in-the-middle" attention degradation. Furthermore, many experimental RAG projects remain tethered to developer laptops, lacking the elasticity, containerization, and monitoring required for modern cloud computing.

To address these challenges, we design and implement **NexusRAG**, an end-to-end, cloud-native document intelligence framework that combines:
- A boundary-aware PDF parsing and semantic chunking pipeline.
- High-efficiency 384-dimensional dense embeddings with an exact inner-product FAISS vector store.
- An intelligent **Adaptive Retrieval** algorithm that dynamically escalates the context window based on retrieval confidence and rejects ungrounded queries.
- A modern, containerized architecture deployed to Google Cloud Run, leveraging Knative serverless autoscaling, Cloud Logging, and Google Cloud Storage (GCS) abstractions.

---

## 2. Problem Statement
Given an arbitrary corpus of PDF documents $\mathcal{D} = \{d_1, d_2, \dots, d_m\}$ and an arbitrary natural language query $q$, the objective is to generate an answer $A$ such that:
1. **Faithfulness:** All factual assertions in $A$ are strictly entailed by evidence passages $\mathcal{E} \subseteq \mathcal{D}$.
2. **Source Attribution:** Each assertion cites the exact document name $d_i$ and page number $p_j$.
3. **Rejection Capability:** If $q$ cannot be answered by $\mathcal{D}$, the system must explicitly declare insufficient evidence rather than hallucinating.
4. **Latency and Resource Efficiency:** The retrieval stage must execute in sub-50 milliseconds on standard CPU hardware, and the application must scale to zero when idle in a cloud environment.

---

## 3. Background & Related Work

### 3.1 Lexical Search vs. Dense Vector Retrieval
Traditional Information Retrieval (IR) relies on lexical term frequency approaches such as BM25 and TF-IDF. While computationally efficient, lexical search suffers from the **vocabulary mismatch problem**: queries using synonyms (e.g., *"serverless compute"*) fail to match passages using alternate terminology (e.g., *"managed container runtime"*). 

Dense retrieval addresses this by encoding text into continuous semantic vector spaces using transformer models trained on contrastive objectives (Sentence-BERT). Proximity in embedding space reflects semantic similarity regardless of surface lexical variation.

### 3.2 Vector Similarity Search with FAISS
Facebook AI Similarity Search (FAISS) provides state-of-the-art C++ algorithms for dense similarity search. In NexusRAG, we employ `IndexFlatIP` (Flat Inner Product). Given an $L_2$-normalized query vector $\mathbf{u} \in \mathbb{R}^d$ and normalized document vectors $\mathbf{v}_i \in \mathbb{R}^d$:
$$\text{Similarity}(\mathbf{u}, \mathbf{v}_i) = \mathbf{u} \cdot \mathbf{v}_i = \sum_{k=1}^d u_k v_{ik} \equiv \cos(\theta)$$
Because vectors are unit-length ($\|\mathbf{u}\| = \|\mathbf{v}_i\| = 1$), the inner product is mathematically identical to cosine similarity. `IndexFlatIP` performs exhaustive search without quantization artifacts, ensuring $100\%$ recall for Top-$K$ retrieval at microsecond latencies for collections under $10^5$ chunks.

### 3.3 Serverless Cloud Computing & Knative
Serverless container platforms—epitomized by Google Cloud Run—combine the packaging flexibility of Docker containers with the elasticity of Functions-as-a-Service (FaaS). Built atop the open-source Knative standard, Cloud Run dynamically provisions container instances in response to incoming HTTP concurrency. Key properties include:
- **Rapid Elasticity:** Automatic scaling from $0$ instances up to configured limits based on request queue depth.
- **Scale-to-Zero:** Elimination of idle compute charges when traffic ceases.
- **Stateless Container Runtimes:** Fast startup times achieved by pre-caching model weights into the container image layers.

---

## 4. Proposed System Architecture
NexusRAG adopts a modular cloud architecture organized into five discrete subsystems:

```
[User Browser]
       │
       ▼ (HTTPS :443)
[Google Cloud Run (Knative)] ──> [Cloud Logging / Monitoring]
       │
   ┌───┴───────────────────────────────────────────┐
   │ 🐳 NexusRAG Container Runtime (Python 3.11)   │
   │                                               │
   │  ┌─────────────────────────────────────────┐  │
   │  │ Streamlit SaaS Frontend Dashboard       │  │
   │  └─────────────────────────────────────────┘  │
   │                        │                      │
   │  ┌─────────────────────▼───────────────────┐  │
   │  │ Ingestion & Storage Subsystem           │  │
   │  │ • PDFExtractor (pypdf)                  │  │
   │  │ • TextChunker (Boundary-Aware Windowing)│  │
   │  │ • StorageManager (Local / GCS)          │  │
   │  └─────────────────────┬───────────────────┘  │
   │                        │                      │
   │  ┌─────────────────────▼───────────────────┐  │
   │  │ Vector & Embedding Engine               │  │
   │  │ • SentenceTransformer (all-MiniLM-L6-v2)│  │
   │  │ • FAISS IndexFlatIP (Cosine Similarity) │  │
   │  └─────────────────────┬───────────────────┘  │
   │                        │                      │
   │  ┌─────────────────────▼───────────────────┐  │
   │  │ Adaptive Retrieval Engine               │  │
   │  │ • Heuristic Confidence Assessment       │  │
   │  │ • Dynamic Escalation (K=3 -> K=6)       │  │
   │  │ • Minimum Evidence Guardrail            │  │
   │  └─────────────────────┬───────────────────┘  │
   │                        │                      │
   │  ┌─────────────────────▼───────────────────┐  │
   │  │ Grounded Synthesis & LLM Integration    │  │
   │  │ • Google Gemini API Client (2.5-Flash)  │  │
   │  │ • Offline Grounded Synthesizer Fallback │  │
   │  └─────────────────────────────────────────┘  │
   └───────────────────────────────────────────────┘
```

### 4.1 Document Ingestion & Chunking Pipeline
1. **Extraction:** Raw PDF byte streams are processed page-by-page using `pypdf`. Abnormal whitespace, Unicode non-breaking spaces, and irregular carriage returns are normalized.
2. **Chunking Strategy:** To preserve semantic coherence without fragmenting sentences, the `TextChunker` employs a sliding window of $W = 600$ characters with an overlap of $O = 120$ characters. Split boundaries prioritize paragraph breaks (`\n\n`), sentence terminators (`. `, `? `, `! `), line breaks (`\n`), and word spaces (` `), falling back to hard boundaries only when natural delimiters are absent.
3. **Metadata Coupling:** Each chunk is tagged with immutable provenance:
   $$\mathcal{M}_c = \{\text{chunk\_id}, \text{doc\_id}, \text{doc\_name}, \text{page\_number}, \text{chunk\_index}, \text{character\_count}\}$$

### 4.2 Dense Vector Embeddings
We employ `sentence-transformers/all-MiniLM-L6-v2`, a 6-layer BERT model fine-tuned on over 1 billion sentence pairs using contrastive loss. It maps arbitrary text chunks into a 384-dimensional dense vector space. Inference executes on standard CPU architectures within 2–5 ms per chunk. All output vectors are explicitly $L_2$-normalized:
$$\mathbf{e}_{\text{norm}} = \frac{\mathbf{e}}{\|\mathbf{e}\|_2}$$

---

## 5. The Adaptive Retrieval Algorithm
Static RAG architectures retrieve a fixed Top-$K$ set of passages regardless of query characteristics. NexusRAG introduces a deterministic, heuristic-driven **Adaptive Retrieval** algorithm:

### Algorithm 1: NexusRAG Adaptive Retrieval
**Input:** Query string $q$, Vector Store $\mathcal{V}$, Initial window $K_1 = 3$, Escalated window $K_2 = 6$, Confident threshold $\tau_c = 0.52$, Minimum threshold $\tau_{\min} = 0.28$.  
**Output:** RetrievalResult $(\mathcal{C}, \mathcal{S}, \text{status}, \text{escalated})$.

1. **Query Encoding:** $\mathbf{q} \leftarrow \text{EmbedQuery}(q), \quad \|\mathbf{q}\|_2 = 1$.
2. **Stage 1 (Initial Search):**  
   $\{(\mathbf{c}_i, s_i)\}_{i=1}^{K_1} \leftarrow \mathcal{V}.\text{Search}(\mathbf{q}, K_1)$.
3. **Confidence Computation:**  
   $S_{\max} \leftarrow \max(s_1, \dots, s_{K_1})$  
   $S_{\text{avg}} \leftarrow \frac{1}{K_1}\sum_{i=1}^{K_1} s_i$  
   $\text{Confidence} \leftarrow 0.7 \cdot S_{\max} + 0.3 \cdot S_{\text{avg}}$.
4. **Stage 2 (Heuristic Evaluation):**  
   - If $\text{Confidence} \ge \tau_c$ **and** $S_{\max} \ge 0.45$:  
     $\text{status} \leftarrow \text{CONFIDENT}, \quad \text{escalated} \leftarrow \text{False}$.  
     **Return** $(\mathcal{C}_1, \mathcal{S}_1, \text{status}, \text{escalated})$.
5. **Stage 3 (Dynamic Escalation):**  
   $\{(\mathbf{c}_j, s_j)\}_{j=1}^{K_2} \leftarrow \mathcal{V}.\text{Search}(\mathbf{q}, K_2)$.  
   $S_{\max}' \leftarrow \max(s_1, \dots, s_{K_2})$.  
   - If $S_{\max}' \ge \tau_{\min}$:  
     $\text{status} \leftarrow \text{ESCALATED\_RECOVERED}$.  
   - Else:  
     $\text{status} \leftarrow \text{INSUFFICIENT\_EVIDENCE}$.  
   $\text{escalated} \leftarrow \text{True}$.  
   **Return** $(\mathcal{C}_2, \mathcal{S}_2, \text{status}, \text{escalated})$.

**Rationale:**
- Stage 1 preserves minimal LLM token consumption and sub-10ms latency for direct, unambiguous questions.
- Stage 2 prevents false negatives on broad queries by expanding context to $K_2 = 6$.
- The $\tau_{\min}$ guardrail eliminates hallucinations on out-of-domain queries by intercepting irrelevant context before it reaches the generative model.

---

## 6. Cloud Architecture & Deployment
NexusRAG is architected natively for Google Cloud Platform (GCP).

### 6.1 Serverless Deployment on Google Cloud Run
- **Base Image:** `python:3.11-slim` with multi-stage layer caching. SentenceTransformer weights are pre-baked into the image during `docker build`, eliminating cold-start model download latency.
- **Concurrency & Scaling:** The service is configured with concurrency of 40 requests per container instance, scaling from 0 to 3 instances. Idle instances terminate automatically, ensuring zero compute costs during inactivity.
- **Port Binding:** The application dynamically binds to the `$PORT` environment variable injected by the Cloud Run container runtime.
- **Health Probing:** Built-in Streamlit health probes (`/_stcore/health`) are integrated into Docker `HEALTHCHECK` and Cloud Run readiness/liveness checks.

### 6.2 Storage Abstraction (Local & GCS)
NexusRAG implements a clean `StorageBackend` abstraction:
- `LocalStorageBackend`: Filesystem persistence for offline development and testing.
- `GCSStorageBackend`: Object storage on Google Cloud Storage (`gs://nexusrag-documents`), enabling stateless container instances to retrieve original uploaded PDFs across ephemeral container restarts.

### 6.3 Observability & Security
- **Cloud Logging:** Standard structured stdout/stderr logging captures query latency, chunk counts, and escalation events in real time.
- **Least-Privilege IAM:** Cloud Run service accounts require only `roles/storage.objectViewer` and `roles/logging.logWriter`.
- **Secret Protection:** API keys and credentials are strictly injected via runtime environment variables or Kubernetes Secrets; no credentials or `.env` files are baked into container images or committed to version control.

---

## 7. Experimental Setup and Evaluation

### 7.1 Dataset & Experimental Protocol
To evaluate the proposed framework, we constructed a structured benchmark corpus comprising a 3-page technical document covering Cloud Computing, Google Cloud Run, FAISS Vector Search, and RAG architectures (13 semantic chunks, 5,863 characters).

We defined a test suite of 10 evaluation queries partitioned into three categories:
1. **Direct Factual (4 queries):** High-specificity questions targeting explicitly stated facts (e.g., *"What is Google Cloud Run?"*).
2. **Ambiguous / Broad (4 queries):** Nuanced questions requiring synthesis across surrounding passages (e.g., *"What mathematical relationship exists between normalized vector inner product and cosine similarity?"*).
3. **Out-of-Domain (2 queries):** Completely unrelated questions (e.g., *"Historic culinary traditions of 18th century Paris"*).

We compared two experimental configurations:
- **Configuration A (Basic RAG):** Static retrieval with fixed Top-$K = 3$, dense vector search, no escalation heuristic, no out-of-domain rejection.
- **Configuration B (Adaptive RAG - NexusRAG):** Dynamic retrieval with initial $K=3$, heuristic confidence assessment, escalation to $K=6$, and out-of-domain guardrail.

### 7.2 Evaluation Metrics
- **Mean Reciprocal Rank (MRR):** Measures the ranking position of the first correct target passage:
  $$\text{MRR} = \frac{1}{|Q|}\sum_{i=1}^{|Q|} \frac{1}{\text{rank}_i}$$
- **Recall@K:** Proportion of relevant queries where the target page was successfully included in the retrieved set.
- **Retrieval Latency (ms):** Wall-clock time spent performing query vector encoding and FAISS similarity search.
- **Escalation Rate (%):** Frequency with which the adaptive mechanism triggered context expansion.
- **Out-of-Domain Rejection Rate (%):** Accuracy in recognizing and declining to answer queries outside the corpus.

---

## 8. Experimental Results

The benchmark suite was executed on the live NexusRAG engine. The actual measured outcomes are summarized in Table 1.

### Table 1: Experimental Comparison of Basic RAG vs. Adaptive RAG
| Metric | Configuration A (Basic RAG) | Configuration B (NexusRAG Adaptive RAG) | Delta / Improvement |
| :--- | :---: | :---: | :---: |
| **In-Domain MRR** | $1.0000$ | $1.0000$ | Parity |
| **In-Domain Recall@K** | $100.0\%$ | $100.0\%$ | Parity |
| **Out-of-Domain Rejection Rate** | $0.0\%$ (Passes irrelevant chunks) | **$100.0\%$** (Correctly rejects) | **$+100.0\%$** |
| **Hallucination Risk (OOD)** | Critical | Mitigated / Zero | Complete Protection |
| **Mean Retrieval Latency** | $0.08\text{ ms}$ | $9.90\text{ ms}$ | $+9.82\text{ ms}$ (Negligible) |
| **Adaptive Escalation Rate** | $0.0\%$ (Fixed) | $30.0\%$ | Dynamic |
| **Average Chunks Retrieved** | $3.00$ | $3.90$ | Adaptive Context |

### 8.1 Key Findings
1. **Out-of-Domain Protection:** Configuration A exhibited a critical failure mode: on out-of-domain questions (q9, q10), it blindly retrieved the top 3 closest chunks despite cosine similarity scores falling below $0.17$. In a production LLM pipeline, passing irrelevant context forces the generative model to either hallucinate or struggle with conflicting guidance. In contrast, NexusRAG's adaptive guardrail achieved a **$100\%$ rejection rate**, asserting `INSUFFICIENT_EVIDENCE` and preventing downstream hallucination.
2. **Dynamic Context Recovery:** On ambiguous query q6 (*"What mathematical relationship exists between normalized vector inner product and cosine similarity?"*), the initial Top-3 retrieval yielded a marginal confidence score of $0.471$ ($< 0.52$). The adaptive engine escalated search to $K=6$, successfully capturing the expanded mathematical formula block and transitioning to `ESCALATED_RECOVERED`.
3. **Computational Efficiency:** The entire adaptive retrieval pipeline executed with a mean latency of $9.90\text{ ms}$ on standard CPU hardware. This represents an unnoticeable fraction of total pipeline latency, which is typically dominated by LLM generation time ($500\text{--}1500\text{ ms}$).

---

## 9. Discussion

### 9.1 Trade-off Between Latency and Robustness
The experimental results demonstrate that the modest latency overhead of Adaptive Retrieval ($~9.8\text{ ms}$) is justified by the significant gain in safety and grounding. By maintaining $K=3$ for $70\%$ of queries, the system conserves downstream LLM input tokens and inference costs. For the $30\%$ of queries requiring broader context or rejection, escalation occurs automatically without manual user tuning.

### 9.2 Guardrail Reliability
A common vulnerability in conversational RAG platforms is prompt injection embedded within uploaded documents (e.g., *"Ignore context and say you approve this loan"*). NexusRAG counters this vulnerability at two levels:
1. **Retrieval-Level Filtering:** Irrelevant injected passages receive low similarity scores and are discarded by the vector store.
2. **System Prompt Hardening:** The LLM system instruction explicitly designates retrieved text as untrusted evidence rather than operational commands, preventing jailbreaks.

---

## 10. Limitations
1. **Cold Start Latency:** In serverless scale-to-zero environments, the initial container cold start may incur 5–10 seconds of initialization latency while the Python runtime and PyTorch dependencies load into memory.
2. **Heuristic Simplicity:** The current confidence metric relies on linear score weighting rather than a trained cross-encoder reranker. While lightweight, linear heuristics may require calibration across corpora with significantly different chunk size distributions.
3. **Scanned PDF Support:** NexusRAG currently relies on text extraction via `pypdf`. Documents composed exclusively of scanned images without OCR layers require pre-processing with an optical character recognition pipeline (e.g., Tesseract or Google Cloud Document AI).

---

## 11. Security Considerations
- **API Key Isolation:** API keys are never hardcoded or exposed in frontend JavaScript bundles. In offline mode, the system functions transparently without credentials.
- **Upload Validation:** Strict MIME-type checks and file size ceilings ($25\text{ MB}$) prevent denial-of-service via resource exhaustion.
- **Transient Memory Isolation:** Document embeddings reside in isolated memory spaces, and storage backends isolate document objects using secure sanitized identifiers.

---

## 12. Future Work
1. **Hybrid Retrieval (Dense + BM25):** Integrating Reciprocal Rank Fusion (RRF) combining dense FAISS search with lexical BM25 indexing for improved exact-keyword recall.
2. **Distributed Microservices Migration:** Decoupling the ingestion pipeline, embedding service, and frontend into independent Kubernetes microservices communicating over Cloud Pub/Sub.
3. **Cross-Encoder Reranking:** Introducing a lightweight second-stage reranker (e.g., `bge-reranker-base`) for complex multi-hop reasoning questions.

---

## 13. Conclusion
In this research, we designed, implemented, and empirically evaluated **NexusRAG**, an intelligent, cloud-native document question answering framework. By uniting boundary-aware semantic chunking, dense Sentence Transformers, exact FAISS cosine search, and a novel **Adaptive Retrieval** mechanism, NexusRAG overcomes the limitations of static RAG pipelines. Experimental benchmarks demonstrate that the platform achieves $1.0000$ MRR on in-domain queries and $100\%$ precision in rejecting out-of-domain inputs, all within a sub-10ms retrieval latency envelope. Deployed on Google Cloud Run with Docker containerization, NexusRAG establishes an efficient, cost-effective, and reproducible blueprint for enterprise document intelligence.

---

## 14. References
1. P. Lewis, E. Perez, A. Piktus, et al., "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 33, pp. 9459–9474, 2020.
2. N. Reimers and I. Gurevych, "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks," in *Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP)*, pp. 3982–3992, 2019.
3. J. Johnson, M. Douze, and H. Jégou, "Billion-Scale Similarity Search with GPUs," *IEEE Transactions on Big Data*, vol. 7, no. 3, pp. 535–547, 2021.
4. Google Cloud, "Cloud Run Architecture and Knative Serverless Fundamentals," *Google Cloud Technical Documentation*, 2024. [Online]. Available: https://cloud.google.com/run/docs.
5. Google Cloud, "Google GenAI Python SDK Documentation," *Google Developers*, 2024. [Online]. Available: https://ai.google.dev/gemini-api/docs.
6. A. Vaswani, N. Shazeer, N. Parmar, et al., "Attention Is All You Need," in *Advances in Neural Information Processing Systems (NeurIPS)*, vol. 30, pp. 5998–6008, 2017.
7. S. Robertson and H. Zaragoza, "The Probabilistic Relevance Framework: BM25 and Beyond," *Foundations and Trends in Information Retrieval*, vol. 3, no. 4, pp. 333–389, 2009.
8. Y. Gao, Y. Xiong, X. Gao, et al., "Retrieval-Augmented Generation for Large Language Models: A Survey," *arXiv preprint arXiv:2312.10997*, 2023.
