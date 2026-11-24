# NexusRAG - 12-Slide Presentation Outline

**File Location:** `presentation/NexusRAG_Presentation.pptx`  
**Target:** 10–12 Minute Major Project Defense / College Viva  

---

### Slide 1: Title Slide
- **Title:** ⚡ NexusRAG
- **Subtitle:** Intelligent Cloud-Native Document Question Answering Platform
- **Key Focus:** Dynamic Adaptive Retrieval, Serverless Knative Architecture on Google Cloud Run, FAISS Dense Vector Indexing, and Frontier LLM Grounding.
- **Presenter Details:** CSE Major Project Defense • 2026

### Slide 2: Problem Statement
- **Lexical Search Limitations:** Traditional keyword search misses synonyms and semantic equivalents.
- **LLM Hallucinations:** Foundational models lack proprietary enterprise data and produce ungrounded claims.
- **Static RAG Deficiencies:** Fixed Top-K causes context starvation on broad questions and noise on simple questions.
- **Deployment Barriers:** Lack of cloud-native elasticity and scale-to-zero containerization.

### Slide 3: Project Objectives & Contributions
- **Adaptive Retrieval:** Heuristic confidence evaluation ($C = 0.7 S_{\max} + 0.3 S_{\text{avg}}$) with dynamic escalation to $K=6$ and out-of-domain rejection.
- **High-Speed Vector Search:** FAISS `IndexFlatIP` with 384-dimensional normalized vectors from `all-MiniLM-L6-v2`.
- **Cloud-Native Deployment:** Containerized with Docker and deployable to Google Cloud Run with Knative serverless autoscaling.
- **Grounded Synthesis:** Google Gemini 2.5 integration with prompt guardrails and offline fallback mode.

### Slide 4: System Architecture
- Step-by-step visual pipeline: Ingestion (pypdf) -> Boundary Chunker (600/120) -> SentenceTransformers (384d) -> FAISS Vector Store -> Adaptive Retriever -> Gemini LLM -> Grounded Output with Citations.

### Slide 5: The Adaptive Retrieval Algorithm
- Stage 1: Initial Search ($K=3$).
- Stage 2: Confidence Heuristic Calculation.
- Stage 3: Dynamic Escalation to $K=6$ if confidence $< 0.52$.
- Stage 4: Out-of-domain guardrail assertion (`INSUFFICIENT_EVIDENCE` if $S_{\max} < 0.28$).

### Slide 6: Cloud Computing Principles Demonstrated
- On-Demand Self-Service (Web UI)
- Serverless Knative Autoscaling (Cloud Run)
- Scale-to-Zero ($0.00 idle cost)
- Object Storage Persistence (GCS)
- Broad Network Access (HTTPS TLS)
- Cloud Telemetry (Cloud Logging & Monitoring)

### Slide 7: Docker & Containerization
- `python:3.11-slim` base image
- Pre-cached SentenceTransformer weights in container layer
- Dynamic `$PORT` binding for Cloud Run
- Built-in Healthcheck probe on `/_stcore/health`
- Exact deployment commands for Cloud Build and Cloud Run

### Slide 8: Kubernetes Production Manifests
- Deployment: 2 replicas, resource requests (250m CPU, 512Mi RAM) and limits
- Probes: Readiness and Liveness probes on `/_stcore/health`
- Service: Cloud LoadBalancer
- ConfigMap & Secret: Environment config and base64 API key protection
- HPA: Autoscaling from 2 to 5 pods at 70% CPU utilization

### Slide 9: Experimental Benchmark & Results
- Empirical evaluation table: Basic RAG vs. Adaptive RAG
- In-Domain MRR: 1.0000 (100% Recall)
- Out-of-Domain Rejection Rate: 100.0% (Zero Hallucination)
- Mean Retrieval Latency: 9.90 ms on CPU
- Adaptive Escalation Rate: 30.0%

### Slide 10: User Interface & Demonstration Tour
- Executive Metrics Cards
- 1-Click Sample PDF Ingestion
- Grounded Chat Interface
- Expandable Source Evidence Inspector with Page Citations
- Dynamic Model & API Key Settings with Offline Mode

### Slide 11: Limitations & Future Roadmap
- Limitations: Text-only PDFs (no OCR for pure images), serverless cold starts.
- Roadmap: Hybrid Search (BM25 + FAISS via RRF), distributed microservices on GKE, neural cross-encoder reranking.

### Slide 12: Conclusion & Viva Q&A
- Project summary and open invitation for questions.
