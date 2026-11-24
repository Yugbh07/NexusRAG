# NexusRAG - College Project Demo Day Checklist

Use this checklist 30 minutes before your presentation tomorrow to ensure a flawless demonstration.

---

## 1. Environment & Pre-Demo Setup
- [ ] Open PowerShell or Terminal.
- [ ] Navigate to the project directory:
  ```powershell
  cd C:\Users\HP\OneDrive\Desktop\NexusRAG
  ```
- [ ] Verify test suite passes 100%:
  ```powershell
  pytest tests -q
  # Output: 22 passed in ~3s
  ```
- [ ] Launch Streamlit application:
  ```powershell
  streamlit run app.py
  ```
- [ ] Browser opens at `http://localhost:8501`.
- [ ] Keep browser tab in Full Screen (Press `F11`).

---

## 2. Live Demo Sequence (Follow `docs/demo_script.md`)
- [ ] **Step 1: Introduction:** Student 1 introduces NexusRAG problem statement and cloud motivation.
- [ ] **Step 2: UI Tour:** Student 2 points out the header badges, operational metric cards, and sidebar.
- [ ] **Step 3: Document Ingestion:**
  - Click **"📚 Load Sample PDF"** in the sidebar.
  - Show the success message and notice that documents count updates to `1` and vector chunks updates to `13`.
- [ ] **Step 4: Standard Grounded QA:**
  - Click the suggested question: *"What is Google Cloud Run and how does it scale?"*
  - Point out the instant answer, sub-20ms retrieval latency, and the `Standard Search (K=3)` badge.
  - Expand **"View Retrieved Source Evidence"** to show Page 2 citations and cosine similarity scores.
- [ ] **Step 5: Adaptive Retrieval Escalation:**
  - Ask: *"What mathematical relationship exists between normalized vector inner product and cosine similarity?"*
  - Show that the system detected ambiguous initial score, escalated search to $K=6$, recovered context, and answered accurately!
- [ ] **Step 6: Out-of-Domain Guardrail:**
  - Ask: *"What are the historic culinary traditions and landmark bakeries of 18th century Paris?"*
  - Show the examiner that NexusRAG asserts **INSUFFICIENT EVIDENCE** rather than hallucinating!
- [ ] **Step 7: Cloud & Architecture Explanation:**
  - Open `docs/architecture.md` or show the slide deck on Google Cloud Run, Knative serverless scale-to-zero, Docker, and GCS.
- [ ] **Step 8: Research Benchmark:**
  - Show `research/diagrams/retrieval_quality_mrr.png` and `research/diagrams/adaptive_escalation_distribution.png`.

---

## 3. Emergency Backup Plans
- **No Internet / Wi-Fi drops:** NexusRAG automatically runs in **Offline Grounded Synthesizer mode**, synthesizing answers directly from local FAISS vectors without needing internet access.
- **Gemini Quota Exceeded:** Offline synthesizer takes over automatically with zero errors.
- **Examiner asks about Kubernetes:** Open `infrastructure/kubernetes/` and explain `deployment.yaml` (readiness/liveness probes), `hpa.yaml` (autoscaling), and `service.yaml`.
