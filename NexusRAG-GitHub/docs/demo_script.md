# NexusRAG 3–5 Minute College Demonstration Script

**Project Title:** NexusRAG – Intelligent Cloud-Native Document Question Answering Platform  
**Team Members:** Student 1 & Student 2  
**Target Audience:** Project Guide, External Examiner, Department Faculty  

---

### Phase 1: Introduction (0:00 – 0:45)

**Student 1:**
> "Good morning, respected examiners and professors. Today, my teammate [Student 2] and I are proud to present our Cloud Computing major project: **NexusRAG – Intelligent Cloud-Native Document Question Answering Platform**.
>
> In real-world enterprise environments, organizations possess thousands of unstructured PDF documents, such as technical manuals, research papers, and compliance reports. Standard keyword search fails because it cannot understand semantic context. On the other hand, relying directly on Large Language Models often leads to hallucinations or reveals that the model lacks private company knowledge.
>
> To solve this, we designed **NexusRAG**, an end-to-end cloud-ready platform that combines **Retrieval-Augmented Generation**, an intelligent **Adaptive Retrieval mechanism**, and **Google Cloud serverless architecture**."

---

### Phase 2: Live UI & Document Ingestion (0:45 – 1:30)

**Student 2:**
> "Here on the screen is our live NexusRAG interface. We developed a modern, dark-themed SaaS dashboard built with Python and Streamlit.
>
> In the sidebar, you can see our AI configuration options, supporting both live Google Gemini models and an offline fallback synthesizer. Below that is our document ingestion engine.
>
> Users can upload single or multiple PDFs. For this demonstration, I will click our **'Load Sample PDF'** button.
>
> Behind the scenes, three key steps just took place:
> 1. Our `PDFExtractor` parsed all 3 pages, preserving metadata.
> 2. Our `TextChunker` split the text into 13 boundary-aware chunks with 120-character overlap so sentences are never broken.
> 3. Our `SentenceTransformer` generated 384-dimensional dense vector embeddings, which were indexed into our FAISS vector database using `IndexFlatIP` for exact cosine similarity search.
>
> You can see our dashboard metrics instantly update to show 1 indexed document and 13 total vector chunks."

---

### Phase 3: Conversational QA & Source Grounding (1:30 – 2:30)

**Student 1:**
> "Now let us ask a technical question directly to the indexed document:  
> *'What is Google Cloud Run and how does it scale?'*
>
> Within just 15 milliseconds, the answer appears!
>
> Notice the diagnostics badge above the response:
> - **Search Status:** Standard Search ($K=3$), meaning our system recognized high retrieval confidence and did not need to waste tokens on escalation.
> - **Model:** Grounded synthesis using Gemini.
> - **Retrieval Latency:** 14.1 milliseconds.
>
> When we open the **'View Retrieved Source Evidence'** accordion, examiners can see the exact chunks retrieved from the PDF, along with the source document name, exact page number (Page 2), and cosine similarity score ($0.761$). This guarantees 100% auditability with zero hallucination."

---

### Phase 4: Demonstrating the Adaptive Retrieval Feature (2:30 – 3:30)

**Student 2:**
> "Now, we would like to showcase the core research contribution of NexusRAG: **Adaptive Retrieval**.
>
> Most existing RAG projects retrieve a fixed $K=3$ or $K=5$ chunks every single time. NexusRAG is adaptive.
>
> If we ask a complex or ambiguous question requiring wider context, our confidence heuristic detects the lower initial similarity and **automatically escalates search to $K=6$**, expanding the context window to capture the complete answer.
>
> Even more importantly, let's test an **out-of-domain question**:  
> *'What are the historic culinary traditions and landmark bakeries of 18th century Paris?'*
>
> Look at the response: Instead of hallucinating a fake answer about bakeries, NexusRAG's guardrail immediately detects that the similarity score is below our minimum threshold ($0.28$) and asserts **INSUFFICIENT EVIDENCE**. It politely informs the user that the uploaded documents do not contain information on this topic."

---

### Phase 5: Cloud Architecture & DevOps (3:30 – 4:30)

**Student 1:**
> "From a Cloud Computing perspective, NexusRAG is built entirely cloud-native:
> 1. **Docker Containerization:** The entire application is packaged in a lightweight `python:3.11-slim` container, with SentenceTransformer weights pre-cached to ensure rapid container startup.
> 2. **Google Cloud Run:** We deploy to Google Cloud Run in the `asia-south1` region. Cloud Run provides **serverless Knative scaling**. When traffic arrives, it scales dynamically up to multiple instances; when idle, it **scales to zero**, incurring zero billing cost.
> 3. **Google Cloud Storage (GCS):** We designed a cloud storage abstraction layer so original PDF files are persisted in GCS buckets rather than ephemeral container disks.
> 4. **Kubernetes Readiness:** In our codebase under `infrastructure/kubernetes/`, we have authored complete Kubernetes manifests, including Deployments with liveness and readiness health probes, Services, ConfigMaps, Secrets, and a Horizontal Pod Autoscaler."

---

### Phase 6: Research Findings & Conclusion (4:30 – 5:00)

**Student 2:**
> "Finally, we evaluated NexusRAG across a structured 10-query benchmark dataset.
>
> Our experimental results confirmed:
> - **$1.0000$ Mean Reciprocal Rank (MRR)** and $100\%$ Recall on in-domain queries.
> - **$100\%$ precision on out-of-domain queries**, completely preventing hallucinations where naive RAG failed.
> - An average retrieval latency of just **$9.90$ milliseconds**.
>
> In our repository, we have included our complete research paper, 22 automated test cases with a 100% pass rate, architecture diagrams, and our presentation deck.
>
> Thank you, professors. We are now open for your questions and viva discussion."
