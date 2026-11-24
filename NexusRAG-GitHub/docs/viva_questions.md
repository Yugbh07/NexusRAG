# NexusRAG Major Project Viva Examination Guide
## 50 Comprehensive Questions & Clear Answers for College Viva / Presentation

---

### SECTION 1: PROJECT OVERVIEW & CONTRIBUTIONS

#### Q1: What is NexusRAG?
**Answer:** NexusRAG is an intelligent, cloud-native document question answering platform. It allows users to upload PDF documents and ask natural-language questions. The system extracts text, generates vector embeddings, retrieves relevant document passages, and uses Google Gemini to generate truthful, evidence-grounded answers with exact citations.

#### Q2: What motivated you to build NexusRAG?
**Answer:** Traditional search engines use keyword matching which misses semantic meaning. On the other hand, Large Language Models (LLMs) hallucinate or lack access to private, proprietary PDF files. NexusRAG bridges this gap using Retrieval-Augmented Generation (RAG) with an intelligent adaptive retrieval feature deployed on serverless cloud infrastructure.

#### Q3: What is the main research/technical contribution of NexusRAG?
**Answer:** Our primary technical contribution is the **Adaptive Retrieval Mechanism**. Instead of using a fixed number of retrieved chunks ($K$), NexusRAG dynamically assesses retrieval confidence ($C = 0.7 \cdot S_{\max} + 0.3 \cdot S_{\text{avg}}$). If initial evidence is weak, it escalates search from $K=3$ to $K=6$. If the question is out-of-domain, it explicitly rejects answering to prevent hallucination.

#### Q4: Why is it called "Cloud-Native"?
**Answer:** Because it is designed from the ground up to run in a containerized environment (Docker), scale automatically based on HTTP traffic (Google Cloud Run / Knative), use cloud object storage (GCS) for persistence, and emit structured logs to Cloud Logging.

#### Q5: Who are the target users for NexusRAG?
**Answer:** Researchers, university students, legal teams, and enterprise analysts who need to query long, dense technical manuals, research papers, or regulatory documents without reading hundreds of pages manually.

---

### SECTION 2: ARTIFICIAL INTELLIGENCE & RAG PIPELINE

#### Q6: What is RAG (Retrieval-Augmented Generation)?
**Answer:** RAG is an AI framework that connects a generative LLM to an external knowledge base. When a user asks a question, the system first retrieves the most relevant passages from the documents, and then feeds those passages into the LLM as evidence to generate an accurate, grounded answer.

#### Q7: What is an embedding?
**Answer:** An embedding is a dense numerical vector (a list of floating-point numbers) that represents the semantic meaning of a piece of text. In NexusRAG, each text chunk is converted into a 384-dimensional vector where semantically similar texts are placed close together in vector space.

#### Q8: What embedding model does NexusRAG use and why?
**Answer:** We use `sentence-transformers/all-MiniLM-L6-v2`. It is lightweight (approx. 90MB), runs efficiently on CPUs with sub-5 millisecond latency per chunk, produces 384-dimensional vectors, and has been fine-tuned on over 1 billion sentence pairs for semantic similarity.

#### Q9: What is vector search?
**Answer:** Vector search is the process of finding the nearest vectors to a given query vector in high-dimensional space. Unlike SQL which searches for exact keyword matches, vector search finds passages with similar conceptual meaning.

#### Q10: What is FAISS and why did you choose it?
**Answer:** FAISS (Facebook AI Similarity Search) is an open-source library optimized for fast similarity search of dense vectors. We use `IndexFlatIP` (Flat Inner Product) with $L_2$-normalized vectors, which computes exact cosine similarity without any loss of accuracy at sub-millisecond speeds.

#### Q11: What is text chunking and why is chunk overlap used?
**Answer:** Chunking is the process of splitting a long document into smaller, manageable text segments (e.g., 600 characters). Overlap (e.g., 120 characters) ensures that sentences or concepts spanning the boundary between two adjacent chunks are not cut in half, preserving semantic continuity.

#### Q12: What is Top-K in vector retrieval?
**Answer:** Top-$K$ refers to the number of most similar document chunks retrieved from the vector index for a given query. In standard RAG, $K$ is typically fixed at 3 or 5.

#### Q13: What is LLM hallucination and how does NexusRAG prevent it?
**Answer:** Hallucination occurs when an LLM generates factually false or invented statements with high confidence. NexusRAG prevents hallucination by:
1. Grounding responses strictly in retrieved evidence.
2. System prompt instructions that command the model to say "I cannot answer based on the provided documents" if information is absent.
3. An out-of-domain guardrail ($S_{\max} < 0.28$) that stops processing before calling the LLM.

#### Q14: How does Google Gemini fit into NexusRAG?
**Answer:** Google Gemini (`gemini-2.5-flash` / `gemini-1.5-flash`) acts as the generative synthesis engine. It reads the user question and the retrieved evidence passages, reasoning across them to generate a coherent, natural-language answer with exact page citations.

#### Q15: What happens if the Gemini API key is missing or quota is exceeded?
**Answer:** NexusRAG features an **Offline Grounded Synthesizer mode**. It extracts and formats direct factual excerpts from the highest-ranking chunks and presents them with full page citations, ensuring the application remains 100% operational and never crashes.

---

### SECTION 3: ADAPTIVE RETRIEVAL

#### Q16: Explain how your Adaptive Retrieval algorithm works.
**Answer:**
1. **Initial Search:** The query is embedded and searched in FAISS with $K=3$.
2. **Confidence Heuristic:** We calculate $\text{Confidence} = 0.7 \cdot S_{\max} + 0.3 \cdot S_{\text{avg}}$.
3. **Decision:**
   - If Confidence $\ge 0.52$ and $S_{\max} \ge 0.45$: The retrieval is marked `CONFIDENT` and returned immediately.
   - Otherwise, the query is ambiguous: The search window escalates to $K=6$.
4. **Out-of-Domain Check:** If the escalated maximum similarity is below $0.28$, it is flagged as `INSUFFICIENT_EVIDENCE`, informing the user that the corpus does not contain relevant data.

#### Q17: Why did you weight $S_{\max}$ at 0.7 and $S_{\text{avg}}$ at 0.3?
**Answer:** $S_{\max}$ represents the best single matching chunk—which is critical because a single highly relevant paragraph can answer a question. $S_{\text{avg}}$ represents the overall topic consensus across top passages. Weighting $S_{\max}$ higher prioritizes strong individual matches while still penalizing noisy, scattered distributions.

#### Q18: What is the benefit of adaptive retrieval over static $K=6$?
**Answer:** Static $K=6$ always sends 6 chunks to the LLM, doubling token costs, increasing latency, and injecting irrelevant noise for simple questions. Adaptive retrieval keeps $K=3$ for 70% of straightforward queries, saving compute and cost, and only escalates when additional context is genuinely needed.

---

### SECTION 4: CLOUD COMPUTING & DEVOPS

#### Q19: Explain the three cloud service models: IaaS, PaaS, and SaaS.
**Answer:**
- **IaaS (Infrastructure as a Service):** Cloud provider supplies raw compute VMs, storage, and networking (e.g., Google Compute Engine, AWS EC2). The user manages OS, runtime, and app.
- **PaaS (Platform as a Service):** Provider manages hardware, OS, and runtime (e.g., Google App Engine, Heroku). Developers just deploy code.
- **SaaS (Software as a Service):** Complete application delivered over the web (e.g., Google Workspace, Salesforce). Users manage no infrastructure.

#### Q20: What is Google Cloud Run and which cloud model does it represent?
**Answer:** Google Cloud Run is a managed serverless container platform built on Knative. It represents **CaaS (Containers as a Service)** or Serverless PaaS. Developers deploy Docker containers, and Cloud Run handles networking, TLS certificates, load balancing, and autoscaling.

#### Q21: What is Knative?
**Answer:** Knative is an open-source Kubernetes-based platform that provides building blocks for serverless workloads, including automatic scaling (up and to zero), routing, and event-driven architecture. Google Cloud Run is Google's managed implementation of Knative.

#### Q22: What is "Scale-to-Zero"?
**Answer:** Scale-to-zero means that when no HTTP requests are arriving at the service, Cloud Run scales active container instances down to zero. In this state, zero CPU and memory are consumed, resulting in **zero cloud billing costs**.

#### Q23: What is rapid elasticity in cloud computing?
**Answer:** Elasticity is the ability of cloud infrastructure to dynamically expand (scale out) and contract (scale in) compute resources in real time to match fluctuating workload demands.

#### Q24: What is containerization and how does Docker work?
**Answer:** Containerization packages an application and all its system libraries, dependencies, and configuration into a standardized, lightweight image. Docker uses Linux kernel namespaces and cgroups to isolate processes, avoiding the overhead of guest operating systems in Virtual Machines.

#### Q25: Why is Docker better than Virtual Machines for this project?
**Answer:** Virtual Machines require a full guest operating system (gigabytes in size) and take minutes to boot. Docker containers share the host OS kernel, start in seconds, require minimal memory overhead, and ensure identical behavior across development and cloud environments.

#### Q26: What is Google Artifact Registry?
**Answer:** Artifact Registry is Google Cloud's secure, managed container registry used to store, manage, and scan OCI-compliant Docker container images before they are deployed to Cloud Run or GKE.

#### Q27: What is Google Cloud Storage (GCS)?
**Answer:** GCS is an object storage service designed for high durability ($99.999999999\%$). In NexusRAG, it stores original PDF documents uploaded by users, allowing stateless container instances to access files without relying on local container disks.

#### Q28: What is IAM (Identity and Access Management)?
**Answer:** IAM is a security framework that controls who (identity) has what access (role/permissions) to which cloud resources. In NexusRAG, service accounts are assigned least-privilege roles (`Storage Object Viewer`, `Logs Writer`).

#### Q29: What is Google Cloud Build?
**Answer:** Cloud Build is a serverless CI/CD platform on GCP that executes container builds directly on Google's cloud infrastructure, allowing developers to build Docker images without needing a local Docker daemon installed.

#### Q30: What is a Cloud Region and why use `asia-south1`?
**Answer:** A region is a specific geographic location composed of multiple isolated data centers (zones). `asia-south1` is the Mumbai, India region, chosen to minimize network latency and comply with data sovereignty for users in South Asia.

---

### SECTION 5: KUBERNETES CONCEPTS

#### Q31: What is Kubernetes (K8s)?
**Answer:** Kubernetes is an open-source container orchestration system for automating application deployment, scaling, and management across clusters of host machines.

#### Q32: What is a Pod in Kubernetes?
**Answer:** A Pod is the smallest deployable computing unit in Kubernetes. It encapsulates one or more containers that share storage resources and a single network IP address.

#### Q33: What is the purpose of a Kubernetes Deployment?
**Answer:** A Deployment declares the desired state for Pods (e.g., run 2 replicas of `nexusrag`). The Deployment Controller automatically replaces failed Pods, handles rolling updates, and scales replicas up or down.

#### Q34: What is the difference between a Liveness Probe and a Readiness Probe?
**Answer:**
- **Readiness Probe:** Checks if the container is ready to accept incoming user traffic (e.g., after loading ML models). If it fails, traffic is not routed to this Pod.
- **Liveness Probe:** Checks if the container process is still alive and responsive. If it fails (e.g., deadlocked), Kubernetes kills and restarts the container.

#### Q35: What is a ConfigMap vs. a Secret?
**Answer:**
- **ConfigMap:** Stores non-confidential configuration key-value pairs (e.g., `PORT: 8501`, `CHUNK_SIZE: 600`).
- **Secret:** Stores sensitive data (e.g., `GEMINI_API_KEY`) encoded in base64 or encrypted at rest, preventing credentials from appearing in source manifests.

#### Q36: What is HPA (Horizontal Pod Autoscaler)?
**Answer:** HPA automatically adjusts the number of running Pod replicas in a deployment based on observed resource utilization (e.g., scaling from 2 to 5 pods when CPU utilization exceeds 70%).

---

### SECTION 6: SOFTWARE ARCHITECTURE & IMPLEMENTATION

#### Q37: Why did you choose Streamlit for the frontend?
**Answer:** Streamlit enables rapid Python-based UI development with reactive state management, seamless integration with machine learning libraries, clean chat interfaces, and fast iteration without needing a separate JavaScript frontend team.

#### Q38: Why use a Modular Monolith instead of 10 microservices?
**Answer:** For a college major project with a tight deadline, a modular monolith provides clean separation of concerns (`document_processing`, `embeddings`, `retrieval`, `llm`, `storage`) inside a single deployable unit. This eliminates distributed system failure modes, network serialization latency, and complex multi-service orchestration while remaining easy to refactor into microservices later.

#### Q39: Why not store vectors in PostgreSQL or traditional SQL databases?
**Answer:** Traditional relational databases index data with B-trees for exact equality or range queries ($O(\log N)$). Dense vector search requires computing high-dimensional mathematical distance (cosine or Euclidean) against continuous coordinates. FAISS utilizes SIMD vector instructions and inverted file indexes optimized for vector math, running hundreds of times faster than standard SQL.

#### Q40: What security measures did you implement in NexusRAG?
**Answer:**
1. Secrets kept strictly in `.env` and environment variables; excluded via `.gitignore`.
2. PDF file type validation and size limits (25MB) to prevent denial of service.
3. System prompt instructions treating document context as passive evidence to resist prompt injection attacks.
4. Input sanitization to prevent directory traversal attacks during file storage.

---

### SECTION 7: RESEARCH & EXPERIMENTAL RESULTS

#### Q41: What metrics did you use to evaluate NexusRAG?
**Answer:** We evaluated Mean Reciprocal Rank (MRR), Recall@K, Average Retrieval Latency (ms), Adaptive Escalation Rate (%), and Out-of-Domain Rejection Rate (%).

#### Q42: What is Mean Reciprocal Rank (MRR)?
**Answer:** MRR is a statistical measure for evaluating search algorithms. For each query, it takes the reciprocal of the rank of the first relevant document ($1/\text{rank}$). The average across all queries is the MRR, where $1.0$ is a perfect score (first result is always relevant).

#### Q43: What were your actual benchmark results?
**Answer:**
- **Basic RAG:** In-Domain MRR: $1.0000$, In-Domain Recall: $100\%$, Out-of-Domain Rejection: $0\%$ (critical hallucination risk), Avg Latency: $0.08\text{ ms}$.
- **NexusRAG (Adaptive):** In-Domain MRR: $1.0000$, In-Domain Recall: $100\%$, Out-of-Domain Rejection: **$100\%$**, Adaptive Escalation Rate: $30.0\%$, Avg Latency: $9.90\text{ ms}$.

#### Q44: Why did Basic RAG have 0% out-of-domain rejection?
**Answer:** Basic RAG has no confidence heuristic. When given an unrelated question (like 18th-century French bakeries), it blindly retrieves the closest 3 chunks in the corpus regardless of how low the similarity score is, causing the LLM to hallucinate or misinform the user.

#### Q45: What does an escalation rate of 30% signify?
**Answer:** It demonstrates that the system does not unnecessarily expand context for straightforward questions (70% remain at $K=3$), but dynamically intervenes to retrieve expanded context ($K=6$) when query ambiguity demands it.

#### Q46: What is the average total latency for a complete query?
**Answer:** Retrieval takes approximately $10\text{--}15\text{ ms}$. Generative synthesis with Gemini takes approximately $800\text{--}1200\text{ ms}$. The total end-to-end response time is typically under $1.2\text{ seconds}$.

---

### SECTION 8: LIMITATIONS & FUTURE SCOPE

#### Q47: What are the current limitations of NexusRAG?
**Answer:**
1. It currently supports text-based PDFs; scanned image-only PDFs require an upstream OCR engine.
2. Initial serverless cold starts on Cloud Run can take 5–10 seconds when scaling up from zero instances.
3. The adaptive heuristic uses linear thresholds rather than a learned neural cross-encoder.

#### Q48: How would you extend this system in the future?
**Answer:**
1. Implement **Hybrid Search** combining dense FAISS vectors with sparse BM25 lexical search using Reciprocal Rank Fusion.
2. Integrate **Cross-Encoder Reranking** for fine-grained multi-hop reasoning.
3. Migrate to distributed microservices on Google Kubernetes Engine (GKE) with Cloud Pub/Sub queues for high-volume document ingestion.

#### Q49: If 1,000 users upload PDFs simultaneously, how will the cloud architecture handle it?
**Answer:** Cloud Run will automatically scale container instances horizontally up to its maximum instance ceiling. Each instance handles up to 40 concurrent requests. For higher scale, we would decouple ingestion by uploading directly to Google Cloud Storage with presigned URLs and processing via background Cloud Functions.

#### Q50: What was your biggest learning from this project?
**Answer:** We learned how to integrate modern AI retrieval techniques (FAISS, SentenceTransformers) with real cloud computing architectures (Cloud Run, Docker, GCS). Most importantly, we learned that practical engineering—such as adaptive retrieval guardrails, fallback modes, and automated testing—is what transforms a fragile demo into a reliable, submission-ready software platform.
