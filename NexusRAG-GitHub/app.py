"""NexusRAG - Intelligent Cloud-Native Document Question Answering Platform
Main Streamlit Application.
"""
import os
import time
from pathlib import Path
import streamlit as st

# Set page config as the very first Streamlit command
st.set_page_config(
    page_title="NexusRAG | Intelligent Cloud-Native Document QA",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.config import (
    APP_NAME,
    APP_TAGLINE,
    VERSION,
    SAMPLE_DIR,
    STORAGE_BACKEND,
    GCS_BUCKET_NAME,
    DEFAULT_GEMINI_MODEL,
    SIMILARITY_THRESHOLD_CONFIDENT
)
from src.document_processing.pdf_extractor import PDFExtractor
from src.document_processing.text_chunker import TextChunker
from src.embeddings.embedder import get_embedding_service
from src.retrieval.vector_store import get_vector_store
from src.retrieval.adaptive_retriever import AdaptiveRetriever
from src.llm.gemini_client import get_gemini_client
from src.llm.rag_engine import RAGEngine, get_rag_engine
from src.storage.storage_manager import get_storage_manager
from src.utils.metrics import format_latency

# ---------------------------------------------------------
# Custom Modern SaaS Styling
# ---------------------------------------------------------
CUSTOM_CSS = """
<style>
    /* Global Styles */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Top Header Bar */
    .nexus-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        padding: 24px 28px;
        border-radius: 12px;
        border: 1px solid #334155;
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }
    
    .nexus-title {
        color: #f8fafc;
        font-size: 28px;
        font-weight: 700;
        letter-spacing: -0.5px;
        display: flex;
        align-items: center;
        gap: 12px;
        margin: 0;
    }
    
    .nexus-subtitle {
        color: #94a3b8;
        font-size: 14px;
        margin-top: 6px;
        margin-bottom: 0px;
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        font-size: 12px;
        font-weight: 600;
        border-radius: 9999px;
        letter-spacing: 0.3px;
    }
    .badge-cloud { background-color: #0369a1; color: #e0f2fe; border: 1px solid #0284c7; }
    .badge-rag { background-color: #4338ca; color: #e0e7ff; border: 1px solid #6366f1; }
    .badge-active { background-color: #065f46; color: #d1fae5; border: 1px solid #10b981; }
    .badge-escalated { background-color: #854d0e; color: #fef9c3; border: 1px solid #eab308; }
    .badge-offline { background-color: #374151; color: #d1d5db; border: 1px solid #4b5563; }
    
    /* Metrics Card Grid */
    .metric-card {
        background: #1e293b;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px 20px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.15);
    }
    .metric-val {
        font-size: 26px;
        font-weight: 700;
        color: #38bdf8;
        margin: 4px 0;
    }
    .metric-label {
        font-size: 12px;
        font-weight: 500;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Chat Container & Bubble styling */
    .chat-bubble-user {
        background-color: #1e293b;
        color: #f1f5f9;
        border: 1px solid #475569;
        border-radius: 12px 12px 2px 12px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    .chat-bubble-assistant {
        background-color: #0f172a;
        color: #f8fafc;
        border: 1px solid #334155;
        border-radius: 12px 12px 12px 2px;
        padding: 18px 22px;
        margin-bottom: 16px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.2);
    }
    
    /* Diagnostics Bar */
    .diagnostics-box {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 6px;
        padding: 8px 12px;
        margin-top: 10px;
        font-size: 12px;
        color: #9ca3af;
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
    }
    
    /* Sidebar polish */
    .sidebar-section {
        background: #1e293b;
        border-radius: 8px;
        padding: 14px;
        border: 1px solid #334155;
        margin-bottom: 16px;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ---------------------------------------------------------
# State Initialization
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "total_queries" not in st.session_state:
    st.session_state.total_queries = 0

if "escalations" not in st.session_state:
    st.session_state.escalations = 0

if "retrieval_latencies" not in st.session_state:
    st.session_state.retrieval_latencies = []

# Instantiate core singletons
embedder = get_embedding_service()
vector_store = get_vector_store()
gemini_client = get_gemini_client()
storage = get_storage_manager()
rag_engine = get_rag_engine()

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(f"## ⚡ {APP_NAME}")
    st.caption(f"v{VERSION} • Cloud-Native Architecture")
    
    st.divider()

    # 1. API Key & Model Configuration
    st.markdown("### 🔑 AI Model Settings")
    input_api_key = st.text_input(
        "Google Gemini API Key",
        value=gemini_client.api_key or "",
        type="password",
        placeholder="AIzaSy...",
        help="Optional. If omitted, NexusRAG executes in Local Grounded Synthesizer mode."
    )
    if input_api_key != gemini_client.api_key:
        gemini_client.set_api_key(input_api_key)
        st.success("API Key updated!")

    if gemini_client.is_live_api_ready:
        st.markdown('<span class="badge badge-active">🟢 Live Gemini API Connected</span>', unsafe_allow_html=True)
    else:
        st.markdown('<span class="badge badge-offline">⚪ Offline Synthesizer Mode</span>', unsafe_allow_html=True)

    st.divider()

    # 2. PDF Document Ingestion
    st.markdown("### 📄 Document Upload")
    uploaded_files = st.file_uploader(
        "Upload PDF Documents",
        type=["pdf"],
        accept_multiple_files=True,
        help="Upload single or multiple research papers, reports, or cloud architecture manuals."
    )

    col_up1, col_up2 = st.columns([1, 1])
    with col_up1:
        if st.button("📥 Index Files", use_container_width=True, type="primary"):
            if not uploaded_files:
                st.warning("Please select at least one PDF file.")
            else:
                progress_bar = st.progress(0)
                status_text = st.empty()
                extractor = PDFExtractor()
                chunker = TextChunker()

                total_files = len(uploaded_files)
                for idx, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Processing {uploaded_file.name}...")
                    file_bytes = uploaded_file.read()
                    
                    # 1. Save to storage backend
                    storage.save_file(uploaded_file.name, file_bytes)
                    
                    # 2. Extract text
                    try:
                        extracted_doc = extractor.extract_from_bytes(file_bytes, uploaded_file.name)
                        # 3. Chunk text
                        chunks = chunker.chunk_document(extracted_doc)
                        # 4. Generate embeddings
                        embs = embedder.embed_texts([c.text for c in chunks])
                        # 5. Add to FAISS index
                        vector_store.add_chunks(chunks, embs)
                    except Exception as e:
                        st.error(f"Error processing {uploaded_file.name}: {e}")
                    
                    progress_bar.progress((idx + 1) / total_files)

                # Persist updated index to disk
                vector_store.save_to_disk()
                status_text.text("Ingestion Complete!")
                st.success(f"Indexed {total_files} document(s) successfully.")
                time.sleep(1)
                st.rerun()

    with col_up2:
        if st.button("📚 Load Sample PDF", use_container_width=True, help="Load built-in Cloud Computing reference PDF"):
            sample_file = SAMPLE_DIR / "cloud_computing_sample.pdf"
            if not sample_file.exists():
                from data.create_sample_pdf import create_sample_pdf
                create_sample_pdf(sample_file)
            
            with open(sample_file, "rb") as f:
                sample_bytes = f.read()
            
            extractor = PDFExtractor()
            chunker = TextChunker()
            doc = extractor.extract_from_bytes(sample_bytes, sample_file.name)
            chunks = chunker.chunk_document(doc)
            embs = embedder.embed_texts([c.text for c in chunks])
            vector_store.add_chunks(chunks, embs)
            vector_store.save_to_disk()
            st.success("Sample PDF loaded & indexed!")
            time.sleep(1)
            st.rerun()

    st.divider()

    # 3. Indexed Documents Management
    st.markdown("### 🗂️ Indexed Documents")
    indexed_docs = vector_store.get_indexed_documents()
    if not indexed_docs:
        st.info("No documents currently indexed.")
    else:
        for doc_info in indexed_docs:
            col_d1, col_d2 = st.columns([3, 1])
            with col_d1:
                st.markdown(f"**{doc_info['doc_name']}**")
                st.caption(f"{doc_info['page_count']} pages • {doc_info['chunk_count']} chunks")
            with col_d2:
                if st.button("🗑️", key=f"del_{doc_info['doc_id']}", help="Remove document"):
                    vector_store.remove_document(doc_info["doc_id"])
                    vector_store.save_to_disk()
                    st.toast(f"Removed {doc_info['doc_name']}")
                    time.sleep(0.5)
                    st.rerun()

        if st.button("🧹 Clear All Documents", use_container_width=True):
            vector_store.clear()
            vector_store.save_to_disk()
            st.session_state.messages = []
            st.toast("Vector index cleared.")
            time.sleep(0.5)
            st.rerun()

    st.divider()

    # 4. System Diagnostics
    st.markdown("### ⚙️ System Status")
    st.caption(f"**Storage Backend:** `{STORAGE_BACKEND.upper()}`")
    if STORAGE_BACKEND == "gcs":
        st.caption(f"**GCS Bucket:** `{GCS_BUCKET_NAME or 'Default'}`")
    st.caption(f"**Embedding Model:** `{embedder.model_name}`")
    st.caption(f"**Embedding Dimension:** `384`")
    st.caption(f"**Vector Store:** `FAISS IndexFlatIP (Cosine)`")
    st.caption(f"**Cloud Runtime:** `Google Cloud Run (Knative)`")

# ---------------------------------------------------------
# MAIN DASHBOARD AREA
# ---------------------------------------------------------

# App Header
st.markdown(f"""
<div class="nexus-header">
    <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
        <div>
            <h1 class="nexus-title">⚡ {APP_NAME} <span style="font-size: 16px; font-weight: 400; color: #38bdf8;">v{VERSION}</span></h1>
            <p class="nexus-subtitle">{APP_TAGLINE}</p>
        </div>
        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <span class="badge badge-cloud">☁️ Cloud Run Ready</span>
            <span class="badge badge-rag">🧠 FAISS Vector Search</span>
            <span class="badge badge-active">🎯 Adaptive RAG</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Operational Metrics Cards
avg_retrieval = (
    sum(st.session_state.retrieval_latencies) / len(st.session_state.retrieval_latencies)
    if st.session_state.retrieval_latencies else 0.0
)
esc_rate = (
    (st.session_state.escalations / st.session_state.total_queries * 100.0)
    if st.session_state.total_queries > 0 else 0.0
)

col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
with col_m1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Documents</div>
        <div class="metric-val">{vector_store.total_documents}</div>
    </div>
    """, unsafe_allow_html=True)

with col_m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Vector Chunks</div>
        <div class="metric-val">{vector_store.total_chunks}</div>
    </div>
    """, unsafe_allow_html=True)

with col_m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Queries Answered</div>
        <div class="metric-val">{st.session_state.total_queries}</div>
    </div>
    """, unsafe_allow_html=True)

with col_m4:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Avg Retrieval</div>
        <div class="metric-val">{format_latency(avg_retrieval)}</div>
    </div>
    """, unsafe_allow_html=True)

with col_m5:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Escalation Rate</div>
        <div class="metric-val">{esc_rate:.1f}%</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------------
# Sample Question Starters
# ---------------------------------------------------------
if vector_store.total_chunks > 0 and len(st.session_state.messages) == 0:
    st.markdown("##### 💡 Suggested Questions (Click to Ask):")
    cols_s = st.columns(3)
    preset_query = None
    with cols_s[0]:
        if st.button("🚀 What is Google Cloud Run and how does it scale?", use_container_width=True):
            preset_query = "What is Google Cloud Run and how does it scale?"
    with cols_s[1]:
        if st.button("🏢 Explain IaaS vs PaaS vs SaaS with examples", use_container_width=True):
            preset_query = "Explain IaaS vs PaaS vs SaaS with examples"
    with cols_s[2]:
        if st.button("🎯 How does the Adaptive Retrieval mechanism work?", use_container_width=True):
            preset_query = "How does the Adaptive Retrieval mechanism work in NexusRAG?"

    if preset_query:
        st.session_state.messages.append({"role": "user", "content": preset_query})
        st.rerun()

# ---------------------------------------------------------
# Chat History Display
# ---------------------------------------------------------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    else:
        with st.chat_message("assistant"):
            st.markdown(msg["content"])
            
            # Show diagnostic details & sources if available
            if "response_data" in msg:
                data = msg["response_data"]
                
                # Diagnostics Badges
                status_badge = (
                    '<span class="badge badge-escalated">⚠️ Escalated Search (K=6)</span>'
                    if data.get("escalated")
                    else '<span class="badge badge-active">✅ Standard Search (K=3)</span>'
                )
                
                model_badge = (
                    f'<span class="badge badge-rag">🤖 {data.get("model_used")}</span>'
                )

                st.markdown(f"""
                <div class="diagnostics-box">
                    <div>{status_badge}</div>
                    <div>{model_badge}</div>
                    <div>⏱️ <b>Retrieval:</b> {format_latency(data.get("retrieval_time_ms", 0))}</div>
                    <div>⚡ <b>Generation:</b> {format_latency(data.get("generation_time_ms", 0))}</div>
                    <div>🎯 <b>Confidence:</b> {data.get("confidence_score", 0):.2f}</div>
                </div>
                """, unsafe_allow_html=True)

                # Source Evidence Accordion
                sources = data.get("sources", [])
                if sources:
                    with st.expander(f"📑 View Retrieved Source Evidence ({len(sources)} Chunks)"):
                        for i, src in enumerate(sources, start=1):
                            st.markdown(f"**Chunk {i} • Source: `{src['doc_name']}` (Page {src['page_number']})** — *Similarity: `{src['similarity_score']:.4f}`*")
                            st.code(src["excerpt"], language="text")

# ---------------------------------------------------------
# Chat Input & Response Generation
# ---------------------------------------------------------
user_query = st.chat_input("Ask a question about your indexed documents...")

if user_query:
    if vector_store.total_chunks == 0:
        st.warning("⚠️ No documents indexed yet. Please upload a PDF or click 'Load Sample PDF' in the sidebar.")
    else:
        # Append and display user message
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Searching document vectors and synthesizing grounded answer..."):
                rag_res = rag_engine.query(user_query)

            st.markdown(rag_res.answer)

            # Update session metrics
            st.session_state.total_queries += 1
            if rag_res.retrieval_result.escalated:
                st.session_state.escalations += 1
            st.session_state.retrieval_latencies.append(rag_res.retrieval_time_ms)

            # Show diagnostics bar
            status_badge = (
                '<span class="badge badge-escalated">⚠️ Escalated Search (K=6)</span>'
                if rag_res.retrieval_result.escalated
                else '<span class="badge badge-active">✅ Standard Search (K=3)</span>'
            )
            model_badge = f'<span class="badge badge-rag">🤖 {rag_res.model_used}</span>'

            st.markdown(f"""
            <div class="diagnostics-box">
                <div>{status_badge}</div>
                <div>{model_badge}</div>
                <div>⏱️ <b>Retrieval:</b> {format_latency(rag_res.retrieval_time_ms)}</div>
                <div>⚡ <b>Generation:</b> {format_latency(rag_res.generation_time_ms)}</div>
                <div>🎯 <b>Confidence:</b> {rag_res.retrieval_result.confidence_score:.2f}</div>
            </div>
            """, unsafe_allow_html=True)

            # Source Accordion
            if rag_res.sources:
                with st.expander(f"📑 View Retrieved Source Evidence ({len(rag_res.sources)} Chunks)"):
                    for i, src in enumerate(rag_res.sources, start=1):
                        st.markdown(f"**Chunk {i} • Source: `{src.doc_name}` (Page {src.page_number})** — *Similarity: `{src.similarity_score:.4f}`*")
                        st.code(src.excerpt, language="text")

            # Save in chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": rag_res.answer,
                "response_data": rag_res.to_dict()
            })

# Clear Chat history button at the bottom
if st.session_state.messages:
    if st.button("🗑️ Clear Chat History"):
        st.session_state.messages = []
        st.rerun()
