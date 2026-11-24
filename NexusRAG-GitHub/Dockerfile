# =========================================================
# NexusRAG - Cloud-Native Dockerfile
# Optimized for Google Cloud Run (Knative) & Local Execution
# =========================================================

FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8501 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

WORKDIR /app

# Install system dependencies needed for compiling C extensions and health probes
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download SentenceTransformer weights during build to ensure ultra-fast cold starts
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application source code and configurations
COPY src/ ./src/
COPY data/ ./data/
COPY app.py .
COPY .env.example .

# Create directory structure for runtime storage and logs
RUN mkdir -p /app/data/storage /app/data/index /app/logs

# Cloud Run dynamic PORT binding
EXPOSE 8501

# Streamlit Healthcheck probe
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl --fail http://localhost:${PORT}/_stcore/health || exit 1

# Launch Streamlit bound to Cloud Run PORT environment variable
CMD streamlit run app.py \
    --server.port=${PORT} \
    --server.address=0.0.0.0 \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false
