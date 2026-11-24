# NexusRAG Setup & Execution Guide

## 1. Quickstart (Local Python Execution)

### Step 1: Clone / Navigate to Directory
```bash
cd C:\Users\HP\OneDrive\Desktop\NexusRAG
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: (Optional) Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
copy .env.example .env
```
Add your Google Gemini API key if available:
```ini
GEMINI_API_KEY="AIzaSy..."
```
*(If omitted, NexusRAG executes in Offline Grounded Synthesizer mode and you can also enter the API key directly in the web UI).*

### Step 4: Run the Streamlit Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 2. Running with Docker

### Build the Docker Image
```bash
docker build -t nexusrag:latest .
```

### Run the Container
```bash
docker run -p 8501:8501 -e GEMINI_API_KEY="your-key" nexusrag:latest
```
Access at `http://localhost:8501`.

### Run with Docker Compose
```bash
docker-compose up --build
```

---

## 3. Running the Test Suite
NexusRAG includes 22 automated tests covering the entire pipeline:
```bash
pytest tests -v
```

---

## 4. Running the Benchmark Experiment Suite
To run the automated research benchmark and generate evaluation charts:
```bash
# Run benchmark experiments (compares Basic RAG vs Adaptive RAG)
python -c "import sys; sys.path.insert(0, '.'); from src.evaluation.benchmark import run_benchmark; run_benchmark()"

# Generate visualization charts
python -c "import sys; sys.path.insert(0, '.'); from src.evaluation.generate_charts import generate_charts; generate_charts()"
```
Output charts are saved to `research/diagrams/`:
- `retrieval_quality_mrr.png`
- `latency_comparison.png`
- `adaptive_escalation_distribution.png`
