# ⚡ NexusRAG: Intelligent Cloud-Native Document Question Answering Platform

[![Python 3.11](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.45-FF4B4B.svg)](https://streamlit.io/)
[![Google Cloud Run](https://img.shields.io/badge/Google%20Cloud-Run%20(Knative)-4285F4.svg)](https://cloud.google.com/run)
[![FAISS](https://img.shields.io/badge/Vector%20Search-FAISS%20IndexFlatIP-00599C.svg)](https://github.com/facebookresearch/faiss)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-22%2F22%20Passing-brightgreen.svg)](docs/testing.md)

NexusRAG is an enterprise-grade, cloud-native document intelligence platform designed to ingest complex multi-page PDF documents, generate dense 384-dimensional vector embeddings, perform ultra-fast semantic similarity search, and synthesize truthful, evidence-grounded answers using Google Gemini.

Built for scalability, cost-efficiency, and academic rigor, NexusRAG introduces an intelligent **Adaptive Retrieval Mechanism** that dynamically escalates search windows and enforces strict out-of-domain guardrails to eliminate Large Language Model (LLM) hallucinations.

---

## 📑 Table of Contents
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [How Adaptive RAG Works](#-how-adaptive-rag-works)
- [Cloud Architecture & Concepts](#-cloud-architecture--concepts)
- [Technology Stack](#-technology-stack)
- [Quickstart: Running Locally](#-quickstart-running-locally)
- [Docker Execution](#-docker-execution)
- [Google Cloud Run Deployment](#-google-cloud-run-deployment)
- [Kubernetes Infrastructure](#-kubernetes-infrastructure)
- [Automated Testing](#-automated-testing)
- [Experimental Benchmarks & Results](#-experimental-benchmarks--results)
- [Research Paper & Viva Preparation](#-research-paper--viva-preparation)
- [Project Structure](#-project-structure)
- [Limitations & Future Scope](#-limitations--future-scope)

---

## 🌟 Key Features

- **Multi-Page PDF Ingestion:** Robust text extraction using `pypdf` with whitespace normalization and per-page metadata tracking.
- **Boundary-Aware Semantic Chunking:** Sliding window chunker (600 characters, 120 character overlap) that breaks cleanly on paragraph, sentence, and word boundaries.
- **Normalized Dense Embeddings:** Sentence Transformers (`all-MiniLM-L6-v2`) generating 384-dimensional unit vectors optimized for CPU inference.
- **Exact Vector Search via FAISS:** Sub-millisecond similarity search using FAISS `IndexFlatIP` (Flat Inner Product) mathematically identical to cosine similarity.
- **🎯 Dynamic Adaptive Retrieval:** Intelligently evaluates retrieval confidence ($C = 0.7 \cdot S_{\max} + 0.3 \cdot S_{\text{avg}}$). Automatically expands context from $K=3$ to $K=6$ on ambiguous queries, and asserts `INSUFFICIENT_EVIDENCE` on out-of-domain queries to prevent hallucination.
- **Frontier LLM Grounding:** Google Gemini (`gemini-2.5-flash` / `gemini-1.5-flash`) prompt-hardened against prompt injections, with mandatory page-level source citations.
- **🛡️ Offline Grounded Synthesizer Mode:** Runs 100% offline without an API key or internet connection, synthesizing direct evidence excerpts with zero crash risk.
- **Modern SaaS Dashboard:** Clean, responsive dark-themed Streamlit UI featuring live operational metrics (documents, chunks, queries answered, latency, and escalation rate).
- **☁️ Cloud-Native Deployment:** Containerized with Docker, deployable to Google Cloud Run with Knative serverless autoscaling (scale-to-zero) and GCS object storage.

---

## 📐 System Architecture

```
User (Browser)
      │
      ▼  HTTPS :443
Google Cloud Run (Knative Autoscaling)
      │
      ▼  Container Runtime (Docker Python 3.11)
Streamlit Dashboard (app.py)
   ├── Sidebar: Document Ingestion & Model Configuration
   ├── Metrics Dashboard: Latency, Escalation %, Vector Chunks
   └── Chat Interface: Conversational Grounded QA
      │
      ├── Ingestion Pipeline: PDFExtractor -> TextChunker (600/120)
      ├── Vector Engine: SentenceTransformer (384d) -> FAISS IndexFlatIP
      ├── Adaptive Engine: K=3 Initial -> Confidence Check -> K=6 Escalation
      ├── LLM Layer: Google Gemini 2.5 Flash / Offline Synthesizer
      └── Storage Layer: Local Filesystem / Google Cloud Storage (GCS)
```

---

## 🎯 How Adaptive RAG Works

Static RAG systems always retrieve a fixed $K=3$ or $K=5$ chunks, causing context starvation on broad questions and hallucination on out-of-domain questions. NexusRAG implements a dynamic 4-step heuristic algorithm:

```
[User Query] ──> [Embed Vector (384d)] ──> [Initial Search (K=3)]
                                                   │
                                                   ▼
                                       [Compute Confidence Metric]
                                  C = 0.7 * S_max + 0.3 * S_avg
                                                   │
                    ┌──────────────────────────────┴──────────────────────────────┐
                    ▼                                                             ▼
         If C >= 0.52 and S_max >= 0.45                                  If C < 0.52 (Ambiguous)
         [Status: CONFIDENT (K=3)]                                                │
                    │                                                             ▼
                    │                                                 [Escalate Search (K=6)]
                    │                                                             │
                    │                                           ┌─────────────────┴─────────────────┐
                    │                                           ▼                                   ▼
                    │                                    If S_max >= 0.28                   If S_max < 0.28
                    │                             [Status: ESCALATED_RECOVERED]       [Status: INSUFFICIENT_EVIDENCE]
                    │                                           │                                   │
                    ▼                                           ▼                                   ▼
             [Synthesize Grounded Answer with Gemini & Source Citations]               [Decline to Answer (Zero Hallucination)]
```

---

## ☁️ Cloud Architecture & Concepts

NexusRAG demonstrates genuine cloud computing principles:
- **On-Demand Self-Service:** Instant access through a secure web browser without managing underlying servers.
- **Managed Container Runtime:** Google Cloud Run abstracts all OS provisioning, node patching, and virtual networking.
- **Rapid Elasticity & Scalability:** Automatically scales container instances up based on concurrent incoming requests.
- **Scale-to-Zero Economics:** Automatically terminates instances when no traffic is present, achieving $0.00 idle cost.
- **Object Storage (GCS):** Decouples state from compute, storing original PDFs in `gs://nexusrag-documents`.
- **Cloud Observability:** Real-time structured logging and resource metrics emitted to Google Cloud Logging and Cloud Monitoring.

---

## 🛠️ Technology Stack

| Layer | Component | Technology Used | Description |
| :--- | :--- | :--- | :--- |
| **Frontend** | UI Dashboard | Streamlit 1.45 | Modern reactive SaaS interface with custom CSS |
| **Runtime** | Programming Language | Python 3.11 | High-performance modular architecture |
| **PDF Extraction** | Document Parser | PyPDF 4.0 | Page-aware text extraction and cleaning |
| **Chunking** | Text Segmentation | Custom TextChunker | 600 chars, 120 overlap, boundary-aware |
| **Embeddings** | Dense Representation | Sentence-Transformers | `all-MiniLM-L6-v2` (384 dimensions, normalized) |
| **Vector DB** | Similarity Search | FAISS (`IndexFlatIP`) | Exact cosine distance search, sub-millisecond |
| **Generative LLM**| Answer Synthesis | Google Gemini API | `gemini-2.5-flash` via `google-genai` SDK |
| **Storage** | Document Persistence | Local / GCS | Cloud-agnostic `StorageBackend` abstraction |
| **Container** | Packaging | Docker | Multi-stage image with cached model weights |
| **Cloud Target** | Serverless Compute | Google Cloud Run | Knative managed autoscaling in `asia-south1` |
| **Orchestration** | K8s Manifests | Kubernetes | Deployments, Services, ConfigMaps, Secrets, HPA |
| **Testing** | Automated QA | Pytest 9.2 | 22 unit & integration test cases (100% pass) |

---

## 🚀 Quickstart: Running Locally

### 1. Prerequisites
- Python 3.11 installed.

### 2. Installation
```bash
# Clone or navigate to the repository
cd C:\Users\HP\OneDrive\Desktop\NexusRAG

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Configuration
```bash
# Copy example environment configuration
copy .env.example .env
```
*(Optional: Add your `GEMINI_API_KEY="AIzaSy..."` into `.env`. If left empty, NexusRAG runs in Local Grounded Synthesizer mode, and you can also input the key directly in the web UI sidebar).*

### 4. Launch Application
```bash
streamlit run app.py
```
Open your browser at: **`http://localhost:8501`**

Click the **"📚 Load Sample PDF"** button in the sidebar to index the pre-packaged Cloud Computing reference document and start asking questions!

---

## 🐳 Docker Execution

Build and run NexusRAG inside a containerized environment:

```bash
# Build the Docker image (pre-caches SentenceTransformer weights)
docker build -t nexusrag:latest .

# Run the container
docker run -p 8501:8501 -e GEMINI_API_KEY="your-key-here" nexusrag:latest

# Or run with Docker Compose
docker-compose up --build
```
Access the application at `http://localhost:8501`.

---

## ☁️ Google Cloud Run Deployment

Deploy NexusRAG to Google Cloud in a single automated command:

### Windows PowerShell:
```powershell
.\infrastructure\cloud\deploy_cloud_run.ps1
```

### Linux / macOS Bash:
```bash
chmod +x infrastructure/cloud/deploy_cloud_run.sh
./infrastructure/cloud/deploy_cloud_run.sh
```

### Manual `gcloud` Commands:
```bash
# 1. Enable APIs
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com

# 2. Build and push image using Cloud Build
gcloud builds submit --tag asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/nexusrag-repo/nexusrag:v1.0.0 .

# 3. Deploy to Cloud Run (Scale-to-Zero, Minimal Cost Tier)
gcloud run deploy nexusrag \
    --image=asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/nexusrag-repo/nexusrag:v1.0.0 \
    --platform=managed \
    --region=asia-south1 \
    --allow-unauthenticated \
    --memory=1Gi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=3
```
*See [docs/cloud_deployment.md](file:///C:/Users/HP/OneDrive/Desktop/NexusRAG/docs/cloud_deployment.md) for full instructions.*

---

## ☸️ Kubernetes Infrastructure

Kubernetes manifests are located in `infrastructure/kubernetes/`:
- `deployment.yaml`: 2 replicas, resource requests/limits, readiness & liveness health probes on `/_stcore/health`.
- `service.yaml`: LoadBalancer service exposing port 80 -> container port 8501.
- `configmap.yaml`: System configuration parameters.
- `secret-example.yaml`: Base64 secret template for `GEMINI_API_KEY`.
- `hpa.yaml`: HorizontalPodAutoscaler scaling from 2 to 5 pods at 70% CPU utilization.

To deploy on Minikube or GKE:
```bash
kubectl apply -f infrastructure/kubernetes/configmap.yaml
kubectl apply -f infrastructure/kubernetes/secret-example.yaml
kubectl apply -f infrastructure/kubernetes/deployment.yaml
kubectl apply -f infrastructure/kubernetes/service.yaml
kubectl apply -f infrastructure/kubernetes/hpa.yaml
```

---

## 🧪 Automated Testing

NexusRAG includes 22 automated tests covering PDF extraction, boundary chunking, vector normalization, FAISS indexing, adaptive escalation, prompt guardrails, and storage backends:

```bash
pytest tests -v
```

**Results:** `22 passed in 2.91s (100% Pass Rate)`.  
*Full report: [docs/testing.md](file:///C:/Users/HP/OneDrive/Desktop/NexusRAG/docs/testing.md)*

---

## 📊 Experimental Benchmarks & Results

We evaluated NexusRAG against a structured benchmark of 10 evaluation queries comparing **Basic RAG (Fixed K=3)** against **NexusRAG (Adaptive RAG)** on a live technical corpus.

### Benchmark Results Table
| Metric | Configuration A (Basic RAG) | Configuration B (NexusRAG Adaptive RAG) |
| :--- | :---: | :---: |
| **In-Domain Mean Reciprocal Rank (MRR)** | $1.0000$ | **$1.0000$** |
| **In-Domain Recall@K** | $100.0\%$ | **$100.0\%$** |
| **Out-of-Domain Rejection Rate** | $0.0\%$ *(Critical hallucination risk)* | **$100.0\%$** *(Zero hallucination)* |
| **Mean Retrieval Latency** | $0.08\text{ ms}$ | **$9.90\text{ ms}$** *(CPU)* |
| **Adaptive Escalation Rate** | $0.0\%$ | **$30.0\%$** |
| **Avg Chunks Retrieved** | $3.00$ | **$3.90$** |

### Generated Benchmark Charts
Charts are saved in `research/diagrams/`:
- `retrieval_quality_mrr.png` — Comparison of MRR and Recall between configurations.
- `latency_comparison.png` — Mean retrieval latency comparison.
- `adaptive_escalation_distribution.png` — Query decision breakdown (Confident vs Escalated vs Insufficient Evidence).

---

## 🎓 Research Paper & Viva Preparation

- **Academic Research Paper:** [research/paper/NexusRAG_Research_Paper.md](file:///C:/Users/HP/OneDrive/Desktop/NexusRAG/research/paper/NexusRAG_Research_Paper.md)  
  *Title: "NexusRAG: An Adaptive Retrieval-Augmented Generation Framework for Intelligent Cloud-Based Document Analysis"*
- **50-Question Viva Guide:** [docs/viva_questions.md](file:///C:/Users/HP/OneDrive/Desktop/NexusRAG/docs/viva_questions.md)  
  *Comprehensive answers covering AI, RAG, FAISS, Cloud Run, Docker, Kubernetes, and Research Metrics.*
- **3–5 Minute Demo Script:** [docs/demo_script.md](file:///C:/Users/HP/OneDrive/Desktop/NexusRAG/docs/demo_script.md)  
  *Exact stage-by-stage speaking script for tomorrow's project demonstration.*
- **Demo Day Checklist:** [DEMO_CHECKLIST.md](file:///C:/Users/HP/OneDrive/Desktop/NexusRAG/DEMO_CHECKLIST.md)
- **Submission Checklist:** [SUBMISSION_CHECKLIST.md](file:///C:/Users/HP/OneDrive/Desktop/NexusRAG/SUBMISSION_CHECKLIST.md)

---

## 📁 Project Structure

```
NexusRAG/
├── app.py                         # Streamlit Modern SaaS Dashboard
├── requirements.txt               # Frozen dependencies
├── Dockerfile                     # Cloud Run production containerfile
├── docker-compose.yml             # Local Docker Compose setup
├── .dockerignore                  # Docker exclusion rules
├── .gitignore                     # Git secret & cache exclusion rules
├── .env.example                   # Environment configuration template
├── README.md                      # Comprehensive project documentation
├── PROJECT_STATUS.md              # Milestone tracking & status
├── DEMO_CHECKLIST.md              # 30-minute pre-demo checklist
├── SUBMISSION_CHECKLIST.md        # Final submission audit checklist
│
├── src/
│   ├── config.py                  # Global application configuration
│   ├── document_processing/       # PDF parsing & text chunking
│   ├── embeddings/                # Sentence Transformers dense embeddings
│   ├── retrieval/                 # FAISS vector store & Adaptive Retriever
│   ├── llm/                       # Gemini client & RAG orchestration
│   ├── storage/                   # Local & GCS storage backends
│   ├── evaluation/                # Benchmark runner & chart generation
│   └── utils/                     # Structured logging & performance metrics
│
├── tests/                         # 22 automated pytest unit & integration tests
│
├── data/
│   ├── sample/                    # Sample Cloud Computing reference PDF
│   └── storage/                   # Local document storage directory
│
├── infrastructure/
│   ├── cloud/                     # Cloud Run & GCS automated deploy scripts
│   └── kubernetes/                # Deployment, Service, ConfigMap, Secret, HPA
│
├── research/
│   ├── paper/                     # Full Academic Research Paper
│   ├── results/                   # Benchmark JSON and CSV metrics
│   ├── datasets/                  # 10-query structured evaluation dataset
│   └── diagrams/                  # Mermaid files & generated PNG charts
│
├── docs/                          # Architecture, Cloud, Setup, Testing, Viva guides
│
└── presentation/                  # PowerPoint PPTX & generation script
```

---

## ⚠️ Limitations & Future Scope

### Limitations
1. **Scanned Documents:** Relies on text-layer extraction via `pypdf`; scanned image-only PDFs require an OCR pre-processor.
2. **Cold Starts:** Serverless scale-to-zero can introduce a 5–10 second delay on the initial request while container runtime initializes.

### Future Scope
1. **Hybrid Retrieval:** Integrating Reciprocal Rank Fusion (RRF) combining dense FAISS vectors with sparse BM25 lexical search.
2. **Distributed Microservices:** Decoupling ingestion, embedding, and inference into independent Kubernetes microservices communicating over Cloud Pub/Sub.
3. **Cross-Encoder Reranking:** Adding a secondary neural reranker (`bge-reranker-base`) for fine-grained multi-hop reasoning.

---

## 👥 Authors
Developed by the **NexusRAG Major Project Team**  
Department of Computer Science & Engineering / Cloud Computing  
Submission Date: November 2026
