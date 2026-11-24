"""Script to generate a rich, multi-page sample PDF for NexusRAG demonstration and testing.
Topic: Principles of Cloud Computing and Retrieval-Augmented Generation.
"""
from pathlib import Path

def create_sample_pdf(output_path: Path):
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    output_path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter

    # Page 1: Introduction to Cloud Computing and Service Models
    c.setFont("Helvetica-Bold", 18)
    c.drawString(54, height - 60, "Cloud Computing Principles & Architecture")
    c.setFont("Helvetica", 10)
    c.drawString(54, height - 80, "Technical Overview Document - NexusRAG Reference Corpus | Page 1")
    c.line(54, height - 90, width - 54, height - 90)

    c.setFont("Helvetica-Bold", 14)
    c.drawString(54, height - 120, "1. Executive Summary")
    c.setFont("Helvetica", 11)
    text1 = (
        "Cloud computing represents the on-demand availability of computer system resources, "
        "especially data storage and computing power, without direct active management by the user. "
        "Large clouds often have functions distributed over multiple locations, each of which is a data center. "
        "Cloud computing relies on sharing of resources to achieve coherence and economies of scale, "
        "typically using a pay-as-you-go model."
    )
    y = height - 140
    for line in [
        "Cloud computing represents the on-demand availability of computer system resources,",
        "especially data storage and computing power, without direct active management by the user.",
        "Large clouds often have functions distributed over multiple locations, each of which is a data center.",
        "Cloud computing relies on sharing of resources to achieve coherence and economies of scale,",
        "typically using a pay-as-you-go model which minimizes capital expenditures for modern software enterprises."
    ]:
        c.drawString(54, y, line)
        y -= 16

    c.setFont("Helvetica-Bold", 14)
    y -= 20
    c.drawString(54, y, "2. Cloud Service Models: IaaS, PaaS, and SaaS")
    y -= 25
    c.setFont("Helvetica", 11)
    points = [
        "Infrastructure as a Service (IaaS): Provides basic compute, networking, and virtual storage (e.g., GCE, EC2).",
        "Users manage the operating system, middleware, application runtimes, and application data.",
        "Platform as a Service (PaaS): Hardware and software tools are provided over the internet (e.g., App Engine, Heroku).",
        "Developers build and run custom applications without managing the underlying virtual machines or disk partitioning.",
        "Software as a Service (SaaS): Complete applications managed entirely by third-party providers (e.g., Google Workspace).",
        "Users simply access the software over a web interface or API without managing infrastructure."
    ]
    for pt in points:
        c.drawString(54, y, pt)
        y -= 18

    c.setFont("Helvetica-Bold", 14)
    y -= 20
    c.drawString(54, y, "3. Key Cloud Characteristics")
    y -= 25
    c.setFont("Helvetica", 11)
    char_points = [
        "- On-Demand Self-Service: Consumers can provision computing capabilities automatically without human interaction.",
        "- Broad Network Access: Capabilities are accessible via standard network protocols across thin or thick client platforms.",
        "- Resource Pooling: Provider computing resources are pooled to serve multiple consumers using a multi-tenant model.",
        "- Rapid Elasticity: Capabilities can be elastically provisioned and released to scale outward and inward with demand.",
        "- Measured Service: Resource usage is monitored, controlled, and reported, providing transparency for provider and consumer."
    ]
    for cp in char_points:
        c.drawString(54, y, cp)
        y -= 18

    c.showPage()

    # Page 2: Google Cloud Run and Serverless Containerization
    c.setFont("Helvetica-Bold", 18)
    c.drawString(54, height - 60, "Serverless Containers & Google Cloud Run")
    c.setFont("Helvetica", 10)
    c.drawString(54, height - 80, "Technical Overview Document - NexusRAG Reference Corpus | Page 2")
    c.line(54, height - 90, width - 54, height - 90)

    y = height - 120
    c.setFont("Helvetica-Bold", 14)
    c.drawString(54, y, "4. Google Cloud Run Architecture")
    y -= 25
    c.setFont("Helvetica", 11)
    cr_text = [
        "Google Cloud Run is a fully managed compute platform that enables developers to run containers directly",
        "on top of Google's scalable infrastructure. Cloud Run is built on Knative, an open-source Kubernetes-based",
        "serverless platform. Developers package their applications inside OCI-compliant container images (Docker),",
        "and Cloud Run abstracts away all cluster management, node provisioning, and operating system patching.",
        "",
        "Key operational features of Google Cloud Run:",
        "1. Automatic Scaling: Cloud Run automatically scales container instances from zero up to hundreds based on incoming HTTP requests.",
        "2. Scale-to-Zero: When no traffic is received, instances terminate, reducing operational billing costs to absolute zero.",
        "3. Concurrency Control: Cloud Run allows configuring maximum concurrent requests per instance (e.g., 80 concurrent connections),",
        "   optimizing CPU and memory utilization across heavy AI workloads.",
        "4. HTTPS Termination: Every Cloud Run deployment automatically receives a TLS-secured HTTPS endpoint and custom domain support.",
        "5. Cold Start Mitigation: Minimum instance configurations can be set to eliminate latency spikes during sudden traffic surges."
    ]
    for line in cr_text:
        c.drawString(54, y, line)
        y -= 18

    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(54, y, "5. Containerization with Docker")
    y -= 25
    c.setFont("Helvetica", 11)
    docker_text = [
        "Containerization isolates application software and its exact dependencies inside a lightweight, standalone executable package.",
        "Unlike hypervisor-driven Virtual Machines (VMs) which virtualize the physical hardware and run guest operating systems,",
        "Docker containers share the host kernel while isolating filesystem namespaces, cgroups, and network interfaces.",
        "This architectural distinction ensures sub-second container startup times and negligible memory overhead.",
        "In NexusRAG, the Docker container bundles Python 3.11, the Streamlit dashboard, FAISS C++ binaries, and ML weights."
    ]
    for line in docker_text:
        c.drawString(54, y, line)
        y -= 18

    c.showPage()

    # Page 3: Retrieval-Augmented Generation & Vector Databases
    c.setFont("Helvetica-Bold", 18)
    c.drawString(54, height - 60, "Retrieval-Augmented Generation & Vector Search")
    c.setFont("Helvetica", 10)
    c.drawString(54, height - 80, "Technical Overview Document - NexusRAG Reference Corpus | Page 3")
    c.line(54, height - 90, width - 54, height - 90)

    y = height - 120
    c.setFont("Helvetica-Bold", 14)
    c.drawString(54, y, "6. The RAG Paradigm")
    y -= 25
    c.setFont("Helvetica", 11)
    rag_text = [
        "Retrieval-Augmented Generation (RAG) is an architectural framework that optimizes the output of Large Language Models (LLMs)",
        "by referencing an authoritative knowledge base outside of its training data before generating a response.",
        "Standard LLMs suffer from temporal hallucination, lack of private domain knowledge, and inability to cite specific evidence.",
        "RAG resolves these limitations through a three-stage pipeline:",
        "- Indexing: Document text extraction, semantic chunking, and dense vector embedding creation.",
        "- Retrieval: Vector similarity search (e.g., FAISS IndexFlatIP) to identify Top-K relevant text passages for a given question.",
        "- Generation: Assembling retrieved passages as verifiable evidence into the system prompt of a frontier LLM (Google Gemini)."
    ]
    for line in rag_text:
        c.drawString(54, y, line)
        y -= 18

    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(54, y, "7. FAISS (Facebook AI Similarity Search)")
    y -= 25
    c.setFont("Helvetica", 11)
    faiss_text = [
        "FAISS is an open-source library developed by Meta AI Research for efficient similarity search and clustering of dense vectors.",
        "NexusRAG utilizes FAISS IndexFlatIP, which performs exact exhaustive inner product search across 384-dimensional vectors.",
        "When vectors are L2-normalized upon ingestion, the inner product is mathematically identical to cosine similarity:",
        "Similarity = dot(u, v) / (||u|| * ||v||) = dot(u_norm, v_norm).",
        "This provides sub-millisecond retrieval latency while guaranteeing 100% recall of top-k closest vectors."
    ]
    for line in faiss_text:
        c.drawString(54, y, line)
        y -= 18

    y -= 20
    c.setFont("Helvetica-Bold", 14)
    c.drawString(54, y, "8. Adaptive Retrieval Mechanism in NexusRAG")
    y -= 25
    c.setFont("Helvetica", 11)
    adaptive_text = [
        "Static RAG systems use a fixed Top-K parameter regardless of question complexity or retrieval ambiguity.",
        "NexusRAG implements an intelligent Adaptive Retrieval mechanism:",
        "- Step 1: Initial retrieval executes with K=3.",
        "- Step 2: Confidence score is evaluated: C = 0.7 * S_max + 0.3 * S_avg.",
        "- Step 3: If C < 0.52 and S_max < 0.45, the retriever dynamically escalates to K=6 to capture broader context.",
        "- Step 4: If S_max remains below 0.28, the system asserts INSUFFICIENT_EVIDENCE to prevent hallucination."
    ]
    for line in adaptive_text:
        c.drawString(54, y, line)
        y -= 18

    c.save()
    print(f"Sample PDF successfully generated at: {output_path}")

if __name__ == "__main__":
    out = Path(r"C:\Users\HP\OneDrive\Desktop\NexusRAG\data\sample\cloud_computing_sample.pdf")
    create_sample_pdf(out)
