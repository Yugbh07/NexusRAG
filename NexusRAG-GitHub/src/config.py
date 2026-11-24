"""NexusRAG Configuration Module
Centralized settings for RAG pipeline, embedding model, FAISS index, and cloud services.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
STORAGE_DIR = DATA_DIR / "storage"
SAMPLE_DIR = DATA_DIR / "sample"
INDEX_DIR = DATA_DIR / "index"
LOGS_DIR = BASE_DIR / "logs"

for directory in [STORAGE_DIR, SAMPLE_DIR, INDEX_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Application Settings
APP_NAME = "NexusRAG"
APP_TAGLINE = "Intelligent Cloud-Native Document Question Answering Platform"
VERSION = "1.0.0"
PORT = int(os.getenv("PORT", 8501))

# Document Processing & Chunking
DEFAULT_CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", 600))  # in characters (~120-150 words)
DEFAULT_CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", 120))  # ~25-30 words
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 25))
SUPPORTED_FILE_TYPES = [".pdf"]

# Embedding Model
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
EMBEDDING_DIMENSION = 384  # Dimension for all-MiniLM-L6-v2

# Vector Store / FAISS
FAISS_INDEX_FILE = INDEX_DIR / "nexus_faiss.index"
METADATA_FILE = INDEX_DIR / "nexus_metadata.json"
DEFAULT_TOP_K = int(os.getenv("DEFAULT_TOP_K", 3))
ESCALATED_TOP_K = int(os.getenv("ESCALATED_TOP_K", 6))

# Adaptive Retrieval Heuristic Thresholds
SIMILARITY_THRESHOLD_CONFIDENT = float(os.getenv("SIMILARITY_THRESHOLD_CONFIDENT", 0.52))
SIMILARITY_THRESHOLD_MINIMUM = float(os.getenv("SIMILARITY_THRESHOLD_MINIMUM", 0.28))

# LLM / Gemini Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY", "")
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
FALLBACK_GEMINI_MODEL = "gemini-1.5-flash"
MAX_OUTPUT_TOKENS = int(os.getenv("MAX_OUTPUT_TOKENS", 1024))
TEMPERATURE = float(os.getenv("TEMPERATURE", 0.2))

# Cloud & Storage Settings
STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local").lower()  # 'local' or 'gcs'
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME", "")
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "")
GCP_REGION = os.getenv("GCP_REGION", "asia-south1")
