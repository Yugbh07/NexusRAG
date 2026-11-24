"""Script to generate a professional 12-slide PowerPoint presentation (.pptx)
for the NexusRAG Cloud Computing Major Project Defense.
"""
from pathlib import Path
import pptx
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_presentation(output_path: Path):
    prs = pptx.Presentation()
    prs.slide_width = Inches(13.333)  # 16:9 Widescreen
    prs.slide_height = Inches(7.5)

    # Color Palette: Deep Slate, Electric Cyan, Emerald, White
    COLOR_BG = RGBColor(15, 23, 42)      # #0f172a
    COLOR_CARD = RGBColor(30, 41, 59)    # #1e293b
    COLOR_CYAN = RGBColor(56, 189, 248)  # #38bdf8
    COLOR_WHITE = RGBColor(248, 250, 252)# #f8fafc
    COLOR_GRAY = RGBColor(148, 163, 184) # #94a3b8
    COLOR_ACCENT = RGBColor(99, 102, 241)# #6366f1

    blank_layout = prs.slide_layouts[6]

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_BG
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category_text="NEXUSRAG • CLOUD COMPUTING MAJOR PROJECT"):
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11), Inches(0.4))
        tf_cat = cat_box.text_frame
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_CYAN

        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.5), Inches(0.8))
        tf_title = title_box.text_frame
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(26)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_WHITE

    # -------------------------------------------------------------
    # SLIDE 1: TITLE SLIDE
    # -------------------------------------------------------------
    slide1 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide1)

    # Accent decorative box
    card1 = slide1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(1.2), Inches(10.33), Inches(5.1))
    card1.fill.solid()
    card1.fill.fore_color.rgb = COLOR_CARD
    card1.line.color.rgb = COLOR_ACCENT

    tf1 = card1.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "⚡ NexusRAG"
    p1.alignment = PP_ALIGN.CENTER
    p1.font.size = Pt(44)
    p1.font.bold = True
    p1.font.color.rgb = COLOR_CYAN

    p1_sub = tf1.add_paragraph()
    p1_sub.text = "Intelligent Cloud-Native Document Question Answering Platform"
    p1_sub.alignment = PP_ALIGN.CENTER
    p1_sub.font.size = Pt(20)
    p1_sub.font.color.rgb = COLOR_WHITE

    p1_desc = tf1.add_paragraph()
    p1_desc.text = "\nFeaturing Dynamic Adaptive Retrieval, Serverless Knative Architecture on Google Cloud Run,\nFAISS Dense Vector Indexing, and Frontier LLM Grounding"
    p1_desc.alignment = PP_ALIGN.CENTER
    p1_desc.font.size = Pt(14)
    p1_desc.font.color.rgb = COLOR_GRAY

    p1_meta = tf1.add_paragraph()
    p1_meta.text = "\n\nMajor Project Presentation • Department of Computer Science & Engineering • 2026"
    p1_meta.alignment = PP_ALIGN.CENTER
    p1_meta.font.size = Pt(13)
    p1_meta.font.bold = True
    p1_meta.font.color.rgb = COLOR_CYAN

    # -------------------------------------------------------------
    # SLIDE 2: PROBLEM STATEMENT
    # -------------------------------------------------------------
    slide2 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide2)
    add_header(slide2, "Problem Statement: The Enterprise Document Gap")

    cards_data = [
        ("1. Lexical Search Limitations", "Traditional keyword and boolean search relies on exact string matching. It fails to comprehend semantic synonyms, context, or conceptual equivalence (e.g. 'serverless compute' vs 'managed container runtime').", COLOR_CARD),
        ("2. LLM Hallucinations", "Pretrained Large Language Models lack access to private, proprietary enterprise PDFs. When queried on domain documents, they invent plausible but factually erroneous statements without citation.", COLOR_CARD),
        ("3. Static RAG Deficiencies", "Existing RAG systems use fixed Top-K retrieval parameters. Small K causes context starvation on broad questions, while large K injects noise, increases token costs, and induces attention degradation.", COLOR_CARD),
        ("4. Deployment Barriers", "Most academic AI projects remain uncontainerized on developer laptops, failing to utilize cloud elasticity, scale-to-zero economics, and enterprise monitoring.", COLOR_CARD)
    ]
    for i, (title, desc, color) in enumerate(cards_data):
        x = Inches(0.8 + (i % 2) * 5.9)
        y = Inches(1.8 + (i // 2) * 2.5)
        c = slide2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.6), Inches(2.2))
        c.fill.solid()
        c.fill.fore_color.rgb = color
        c.line.color.rgb = COLOR_CYAN
        tf = c.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(16)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_CYAN
        p_d = tf.add_paragraph()
        p_d.text = "\n" + desc
        p_d.font.size = Pt(13)
        p_d.font.color.rgb = COLOR_WHITE

    # -------------------------------------------------------------
    # SLIDE 3: RESEARCH & PROJECT OBJECTIVES
    # -------------------------------------------------------------
    slide3 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide3)
    add_header(slide3, "Project Objectives & Key Contributions")

    objs = [
        ("🎯 Adaptive Retrieval Engine", "Develop a heuristic confidence metric (C = 0.7 * S_max + 0.3 * S_avg) that dynamically expands search from K=3 to K=6 on ambiguous queries and asserts INSUFFICIENT_EVIDENCE on out-of-domain queries."),
        ("⚡ High-Speed Vector Retrieval", "Implement FAISS IndexFlatIP with 384-dimensional normalized vectors from Sentence Transformers (all-MiniLM-L6-v2), achieving sub-10ms retrieval latency on standard CPU hardware."),
        ("☁️ Serverless Cloud-Native Deployment", "Containerize the entire platform with Docker and deploy to Google Cloud Run (Knative) in asia-south1, achieving automatic scale-to-zero economics ($0 idle billing) and rapid elasticity."),
        ("🛡️ Grounded Synthesis & Guardrails", "Integrate Google Gemini 2.5 Flash with prompt-level protection against malicious document injections, mandatory page citations, and an offline synthesizer fallback.")
    ]
    for i, (title, desc) in enumerate(objs):
        y = Inches(1.8 + i * 1.3)
        c = slide3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, Inches(11.7), Inches(1.15))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_CARD
        c.line.color.rgb = COLOR_ACCENT
        tf = c.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = f"{title}: "
        p_t.font.size = Pt(15)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_CYAN
        run = p_t.add_run()
        run.text = desc
        run.font.size = Pt(13)
        run.font.bold = False
        run.font.color.rgb = COLOR_WHITE

    # -------------------------------------------------------------
    # SLIDE 4: SYSTEM ARCHITECTURE
    # -------------------------------------------------------------
    slide4 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide4)
    add_header(slide4, "End-to-End System Architecture")

    steps = [
        ("1. Ingestion", "PDF Extraction (pypdf)\nClean whitespace\nPage metadata tracking"),
        ("2. Chunking", "Sliding Window Chunker\n600 chars, 120 overlap\nBoundary-aware splits"),
        ("3. Embedding", "all-MiniLM-L6-v2\n384-dim continuous vectors\nL2 unit normalization"),
        ("4. Indexing", "FAISS IndexFlatIP\nCosine similarity math\nDisk persistence"),
        ("5. Adaptive RAG", "Initial K=3 search\nConfidence evaluation\nEscalate K=6 / Reject"),
        ("6. Generation", "Google Gemini 2.5 Flash\nStrict source grounding\nPage-level citations")
    ]
    for i, (st_title, st_desc) in enumerate(steps):
        x = Inches(0.8 + i * 1.95)
        c = slide4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, Inches(2.2), Inches(1.8), Inches(4.2))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_CARD
        c.line.color.rgb = COLOR_CYAN
        tf = c.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = st_title
        p.alignment = PP_ALIGN.CENTER
        p.font.size = Pt(15)
        p.font.bold = True
        p.font.color.rgb = COLOR_CYAN
        p_d = tf.add_paragraph()
        p_d.text = "\n" + st_desc
        p_d.alignment = PP_ALIGN.CENTER
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = COLOR_WHITE

    # -------------------------------------------------------------
    # SLIDE 5: ADAPTIVE RETRIEVAL ALGORITHM
    # -------------------------------------------------------------
    slide5 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide5)
    add_header(slide5, "The Adaptive Retrieval Mechanism")

    c_box = slide5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    c_box.fill.solid()
    c_box.fill.fore_color.rgb = COLOR_CARD
    c_box.line.color.rgb = COLOR_CYAN
    tf5 = c_box.text_frame
    tf5.word_wrap = True

    p = tf5.paragraphs[0]
    p.text = "Heuristic Confidence-Guided Context Escalation"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    points5 = [
        ("\n• Step 1: Initial Retrieval (K=3)", "Perform dense inner product similarity search in FAISS using top-3 chunks. Fast, latency-optimal, low token usage."),
        ("\n• Step 2: Quality & Confidence Assessment", "Compute Confidence = 0.7 * S_max + 0.3 * S_avg.\n  - S_max captures strongest individual evidence piece.\n  - S_avg captures consensus across retrieved candidate set."),
        ("\n• Step 3: Heuristic Decision Boundary", "  - If Confidence >= 0.52 and S_max >= 0.45: Status is CONFIDENT. Return K=3 immediately (70% of queries).\n  - If Confidence < 0.52: Query is ambiguous. Dynamically escalate search window to K=6."),
        ("\n• Step 4: Out-of-Domain Guardrail", "  - If expanded S_max >= 0.28: Status is ESCALATED_RECOVERED. Context recovered successfully.\n  - If expanded S_max < 0.28: Status is INSUFFICIENT_EVIDENCE. The system declines to answer, eliminating hallucination entirely!")
    ]
    for h, b in points5:
        p_h = tf5.add_paragraph()
        p_h.text = h
        p_h.font.size = Pt(14)
        p_h.font.bold = True
        p_h.font.color.rgb = COLOR_WHITE
        p_b = tf5.add_paragraph()
        p_b.text = b
        p_b.font.size = Pt(12)
        p_b.font.color.rgb = COLOR_GRAY

    # -------------------------------------------------------------
    # SLIDE 6: CLOUD COMPUTING PRINCIPLES DEMONSTRATED
    # -------------------------------------------------------------
    slide6 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide6)
    add_header(slide6, "Cloud Computing Principles & GCP Implementation")

    cloud_cards = [
        ("On-Demand Self-Service", "Users access NexusRAG over HTTPS without managing server infrastructure.", COLOR_CARD),
        ("Serverless Knative (Cloud Run)", "Managed container runtime automatically scales compute instances based on request queue depth.", COLOR_CARD),
        ("Scale-to-Zero Economics", "When idle, active instances scale to zero, resulting in $0.00 compute charges during downtime.", COLOR_CARD),
        ("Decoupled Cloud Storage", "Original PDFs persist in Google Cloud Storage (GCS) buckets, decoupling state from ephemeral containers.", COLOR_CARD),
        ("Broad Network Access", "Accessible via TLS-secured HTTPS endpoints with automated global CDN load balancing.", COLOR_CARD),
        ("Cloud Telemetry & Auditing", "Real-time structured logs and metrics streamed to Google Cloud Logging & Cloud Monitoring.", COLOR_CARD)
    ]
    for i, (title, desc, color) in enumerate(cloud_cards):
        x = Inches(0.8 + (i % 3) * 3.9)
        y = Inches(1.8 + (i // 3) * 2.5)
        c = slide6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(3.7), Inches(2.2))
        c.fill.solid()
        c.fill.fore_color.rgb = color
        c.line.color.rgb = COLOR_CYAN
        tf = c.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(15)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_CYAN
        p_d = tf.add_paragraph()
        p_d.text = "\n" + desc
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = COLOR_WHITE

    # -------------------------------------------------------------
    # SLIDE 7: DOCKER & CONTAINERIZATION
    # -------------------------------------------------------------
    slide7 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide7)
    add_header(slide7, "Docker Containerization & Cold-Start Optimization")

    c7_left = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
    c7_left.fill.solid()
    c7_left.fill.fore_color.rgb = COLOR_CARD
    c7_left.line.color.rgb = COLOR_ACCENT
    tf7_l = c7_left.text_frame
    tf7_l.word_wrap = True
    p = tf7_l.paragraphs[0]
    p.text = "Dockerfile Architectural Highlights"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    l_pts = [
        ("\n• Base Image:", "python:3.11-slim (minimal attack surface, ~150MB base)."),
        ("\n• Pre-Cached ML Weights:", "SentenceTransformer model is downloaded and cached during docker build layer creation. This eliminates cold-start model download latency during container boot!"),
        ("\n• Dynamic PORT Binding:", "Binds dynamically to ${PORT:-8501} as required by Google Cloud Run."),
        ("\n• Built-in Healthcheck Probe:", "HEALTHCHECK probe evaluates /_stcore/health every 30s.")
    ]
    for h, b in l_pts:
        p_h = tf7_l.add_paragraph()
        p_h.text = h
        p_h.font.size = Pt(13)
        p_h.font.bold = True
        p_h.font.color.rgb = COLOR_WHITE
        p_b = tf7_l.add_paragraph()
        p_b.text = b
        p_b.font.size = Pt(12)
        p_b.font.color.rgb = COLOR_GRAY

    c7_right = slide7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.8), Inches(5.6), Inches(5.0))
    c7_right.fill.solid()
    c7_right.fill.fore_color.rgb = COLOR_CARD
    c7_right.line.color.rgb = COLOR_CYAN
    tf7_r = c7_right.text_frame
    tf7_r.word_wrap = True
    p = tf7_r.paragraphs[0]
    p.text = "Deployment Command Summary"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    r_pts = [
        ("\n1. Cloud Build & Artifact Registry:", "gcloud builds submit --tag asia-south1-docker.pkg.dev/$PROJECT/nexusrag-repo/nexusrag:v1 ."),
        ("\n2. Deploy to Google Cloud Run:", "gcloud run deploy nexusrag \\\n  --image=... \\\n  --platform=managed \\\n  --region=asia-south1 \\\n  --allow-unauthenticated \\\n  --memory=1Gi \\\n  --cpu=1 \\\n  --min-instances=0 \\\n  --max-instances=3"),
        ("\n3. Local Docker Compose:", "docker-compose up --build")
    ]
    for h, b in r_pts:
        p_h = tf7_r.add_paragraph()
        p_h.text = h
        p_h.font.size = Pt(13)
        p_h.font.bold = True
        p_h.font.color.rgb = COLOR_WHITE
        p_b = tf7_r.add_paragraph()
        p_b.text = b
        p_b.font.size = Pt(11)
        p_b.font.color.rgb = COLOR_CYAN

    # -------------------------------------------------------------
    # SLIDE 8: KUBERNETES CONFIGURATION
    # -------------------------------------------------------------
    slide8 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide8)
    add_header(slide8, "Kubernetes (K8s) Production Manifests")

    k8s_items = [
        ("Deployment (deployment.yaml)", "Manages 2 container replicas. Specifies CPU requests (250m) and limits (1000m), memory requests (512Mi) and limits (1536Mi). Automatically replaces failed pods."),
        ("Probes (Readiness & Liveness)", "Readiness Probe prevents routing traffic until model weights load. Liveness Probe restarts deadlocked containers. Configured against /_stcore/health."),
        ("Service (service.yaml)", "Provisions a cloud LoadBalancer exposing port 80 and routing to container port 8501."),
        ("ConfigMap & Secret (configmap.yaml, secret-example.yaml)", "Decouples application configuration (CHUNK_SIZE, MODEL) and protects sensitive credentials (GEMINI_API_KEY) via base64 encoded secrets."),
        ("Autoscaling (hpa.yaml)", "HorizontalPodAutoscaler automatically scales pod replicas from 2 to 5 based on 70% target CPU utilization.")
    ]
    for i, (title, desc) in enumerate(k8s_items):
        y = Inches(1.8 + i * 1.05)
        c = slide8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), y, Inches(11.7), Inches(0.95))
        c.fill.solid()
        c.fill.fore_color.rgb = COLOR_CARD
        c.line.color.rgb = COLOR_CYAN
        tf = c.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = f"• {title}: "
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = COLOR_CYAN
        run = p.add_run()
        run.text = desc
        run.font.size = Pt(12)
        run.font.bold = False
        run.font.color.rgb = COLOR_WHITE

    # -------------------------------------------------------------
    # SLIDE 9: EXPERIMENTAL EVALUATION & RESULTS
    # -------------------------------------------------------------
    slide9 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide9)
    add_header(slide9, "Benchmark Evaluation: Basic RAG vs. Adaptive RAG")

    c9 = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(11.7), Inches(5.0))
    c9.fill.solid()
    c9.fill.fore_color.rgb = COLOR_CARD
    c9.line.color.rgb = COLOR_CYAN
    tf9 = c9.text_frame
    tf9.word_wrap = True

    p = tf9.paragraphs[0]
    p.text = "Empirical Results from Structured 10-Query Technical Benchmark"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN

    res_pts = [
        ("\n• In-Domain Retrieval Accuracy:", "Both Basic RAG and NexusRAG achieved 1.0000 MRR (Mean Reciprocal Rank) and 100% Recall on factual and broad technical queries."),
        ("\n• Out-of-Domain Guardrail Precision:", "Basic RAG scored 0.0% (blindly retrieved irrelevant passages, causing high hallucination risk).\nNexusRAG achieved 100.0% rejection precision, successfully asserting INSUFFICIENT_EVIDENCE."),
        ("\n• Adaptive Context Escalation Rate:", "30.0% of queries triggered dynamic escalation to K=6, demonstrating intelligent intervention without bloating normal queries."),
        ("\n• Mean Retrieval Latency:", "9.90 milliseconds on CPU (FAISS IndexFlatIP + SentenceTransformers). Negligible overhead compared to LLM generation time (~1 second).")
    ]
    for h, b in res_pts:
        p_h = tf9.add_paragraph()
        p_h.text = h
        p_h.font.size = Pt(14)
        p_h.font.bold = True
        p_h.font.color.rgb = COLOR_WHITE
        p_b = tf9.add_paragraph()
        p_b.text = b
        p_b.font.size = Pt(12)
        p_b.font.color.rgb = COLOR_GRAY

    # -------------------------------------------------------------
    # SLIDE 10: USER INTERFACE & DEMONSTRATION HIGHLIGHTS
    # -------------------------------------------------------------
    slide10 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide10)
    add_header(slide10, "Application User Interface & Feature Tour")

    ui_cards = [
        ("🖥️ Executive Dashboard", "Real-time metrics tracking documents indexed, vector chunks, queries answered, average latency, and escalation rate.", COLOR_CARD),
        ("📚 1-Click Sample Ingestion", "Pre-packaged Cloud Computing reference PDF allows instant demonstration without manual file searching.", COLOR_CARD),
        ("💬 Grounded Conversational QA", "Natural language chat with streaming feedback, prompt injection protection, and contextual chat history.", COLOR_CARD),
        ("📑 Expandable Evidence Inspector", "Exposes exact retrieved chunks with source PDF filename, page number, and FAISS similarity scores.", COLOR_CARD),
        ("⚙️ Dynamic Settings Sidebar", "On-the-fly Gemini API key configuration with automated fallback to Offline Synthesizer mode.", COLOR_CARD),
        ("🗑️ Per-Document Management", "Selective document deletion with automatic FAISS index rebuilding to eliminate orphaned vectors.", COLOR_CARD)
    ]
    for i, (title, desc, color) in enumerate(ui_cards):
        x = Inches(0.8 + (i % 3) * 3.9)
        y = Inches(1.8 + (i // 3) * 2.5)
        c = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(3.7), Inches(2.2))
        c.fill.solid()
        c.fill.fore_color.rgb = color
        c.line.color.rgb = COLOR_CYAN
        tf = c.text_frame
        tf.word_wrap = True
        p_t = tf.paragraphs[0]
        p_t.text = title
        p_t.font.size = Pt(15)
        p_t.font.bold = True
        p_t.font.color.rgb = COLOR_CYAN
        p_d = tf.add_paragraph()
        p_d.text = "\n" + desc
        p_d.font.size = Pt(12)
        p_d.font.color.rgb = COLOR_WHITE

    # -------------------------------------------------------------
    # SLIDE 11: LIMITATIONS & FUTURE ROADMAP
    # -------------------------------------------------------------
    slide11 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide11)
    add_header(slide11, "Limitations & Proposed Future Roadmap")

    c11_left = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.8), Inches(5.6), Inches(5.0))
    c11_left.fill.solid()
    c11_left.fill.fore_color.rgb = COLOR_CARD
    c11_left.line.color.rgb = COLOR_CYAN
    tf11_l = c11_left.text_frame
    tf11_l.word_wrap = True
    p = tf11_l.paragraphs[0]
    p.text = "Current System Limitations"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN
    lim_pts = [
        ("\n• Scanned Document Handling:", "Current pipeline extracts text layers from digital PDFs. Pure scanned images require an upstream OCR engine."),
        ("\n• Cold Start Initialization:", "Serverless scale-to-zero can induce 5-10s delay on the very first incoming request."),
        ("\n• Linear Heuristic Weighting:", "Adaptive thresholds are rule-based rather than parameterized via trained neural rerankers.")
    ]
    for h, b in lim_pts:
        p_h = tf11_l.add_paragraph()
        p_h.text = h
        p_h.font.size = Pt(13)
        p_h.font.bold = True
        p_h.font.color.rgb = COLOR_WHITE
        p_b = tf11_l.add_paragraph()
        p_b.text = b
        p_b.font.size = Pt(12)
        p_b.font.color.rgb = COLOR_GRAY

    c11_right = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.9), Inches(1.8), Inches(5.6), Inches(5.0))
    c11_right.fill.solid()
    c11_right.fill.fore_color.rgb = COLOR_CARD
    c11_right.line.color.rgb = COLOR_ACCENT
    tf11_r = c11_right.text_frame
    tf11_r.word_wrap = True
    p = tf11_r.paragraphs[0]
    p.text = "Future Architecture Roadmap"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = COLOR_CYAN
    fut_pts = [
        ("\n• Hybrid Search (Dense + Lexical):", "Integrate Reciprocal Rank Fusion (RRF) combining dense FAISS search with BM25 keyword matching."),
        ("\n• Distributed Microservices on GKE:", "Decouple ingestion, embedding, and LLM synthesis into microservices communicating over Cloud Pub/Sub queues."),
        ("\n• Neural Cross-Encoder Reranking:", "Add a secondary transformer reranker (bge-reranker-base) for complex multi-hop question answering.")
    ]
    for h, b in fut_pts:
        p_h = tf11_r.add_paragraph()
        p_h.text = h
        p_h.font.size = Pt(13)
        p_h.font.bold = True
        p_h.font.color.rgb = COLOR_WHITE
        p_b = tf11_r.add_paragraph()
        p_b.text = b
        p_b.font.size = Pt(12)
        p_b.font.color.rgb = COLOR_GRAY

    # -------------------------------------------------------------
    # SLIDE 12: CONCLUSION & VIVA Q&A
    # -------------------------------------------------------------
    slide12 = prs.slides.add_slide(blank_layout)
    set_slide_background(slide12)

    card12 = slide12.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(1.2), Inches(10.33), Inches(5.1))
    card12.fill.solid()
    card12.fill.fore_color.rgb = COLOR_CARD
    card12.line.color.rgb = COLOR_CYAN

    tf12 = card12.text_frame
    tf12.word_wrap = True
    p12 = tf12.paragraphs[0]
    p12.text = "🎉 Thank You!"
    p12.alignment = PP_ALIGN.CENTER
    p12.font.size = Pt(40)
    p12.font.bold = True
    p12.font.color.rgb = COLOR_CYAN

    p12_sub = tf12.add_paragraph()
    p12_sub.text = "NexusRAG: Intelligent Cloud-Native Document Question Answering Platform"
    p12_sub.alignment = PP_ALIGN.CENTER
    p12_sub.font.size = Pt(18)
    p12_sub.font.bold = True
    p12_sub.font.color.rgb = COLOR_WHITE

    p12_sum = tf12.add_paragraph()
    p12_sum.text = "\n• Fully Functional Modular Application (Python 3.11 + Streamlit)\n• Dynamic Adaptive Retrieval Mechanism with 100% OOD Rejection\n• Production Containerization (Docker) & Google Cloud Run Knative Architecture\n• 22/22 Automated Tests Passing & Reproducible Research Benchmark"
    p12_sum.alignment = PP_ALIGN.CENTER
    p12_sum.font.size = Pt(14)
    p12_sum.font.color.rgb = COLOR_GRAY

    p12_qa = tf12.add_paragraph()
    p12_qa.text = "\nWe are now open for Viva Questions and Discussion."
    p12_qa.alignment = PP_ALIGN.CENTER
    p12_qa.font.size = Pt(16)
    p12_qa.font.bold = True
    p12_qa.font.color.rgb = COLOR_CYAN

    output_path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(output_path))
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    out_file = Path(r"C:\Users\HP\OneDrive\Desktop\NexusRAG\presentation\NexusRAG_Presentation.pptx")
    build_presentation(out_file)
