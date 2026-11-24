# NexusRAG Google Cloud Run Deployment Guide

## 1. Overview
NexusRAG is designed to deploy seamlessly to **Google Cloud Run**, a serverless container platform built on Knative. Cloud Run provides rapid elasticity, automatic HTTPS termination, and scale-to-zero economics.

---

## 2. Prerequisites
1. **Google Cloud Account:** Active GCP project.
2. **Google Cloud SDK (`gcloud`):** Installed and authenticated:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```
3. **Billing:** Cloud Run has a generous Free Tier (2 million requests/month, 360,000 vCPU-seconds, 180,000 GiB-seconds free). With minimum instances set to 0, running a demo costs $0.00.

---

## 3. Step-by-Step Deployment Workflow

### Step 1: Enable Required GCP APIs
```bash
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    storage.googleapis.com \
    logging.googleapis.com \
    monitoring.googleapis.com
```

### Step 2: Create Artifact Registry Docker Repository
```bash
gcloud artifacts repositories create nexusrag-repo \
    --repository-format=docker \
    --location=asia-south1 \
    --description="NexusRAG Docker Images"
```

### Step 3: Build & Push Container Image via Google Cloud Build
Cloud Build builds your image directly in the cloud (no local Docker daemon required):
```bash
gcloud builds submit --tag asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/nexusrag-repo/nexusrag:v1.0.0 .
```

### Step 4: Deploy Container to Google Cloud Run
```bash
gcloud run deploy nexusrag \
    --image=asia-south1-docker.pkg.dev/YOUR_PROJECT_ID/nexusrag-repo/nexusrag:v1.0.0 \
    --platform=managed \
    --region=asia-south1 \
    --allow-unauthenticated \
    --memory=1Gi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=3 \
    --concurrency=40 \
    --timeout=300 \
    --set-env-vars="PORT=8501,STORAGE_BACKEND=local,GEMINI_MODEL=gemini-2.5-flash"
```

### Step 5: (Optional) Inject Gemini API Key Securely
To set your Gemini API key in Cloud Run:
```bash
gcloud run services update nexusrag \
    --region=asia-south1 \
    --update-env-vars="GEMINI_API_KEY=AIzaSy_YOUR_API_KEY_HERE"
```

---

## 4. Automated One-Command Script
We provide automated deployment scripts inside `infrastructure/cloud/`:
- **Linux/macOS Bash:**
  ```bash
  chmod +x infrastructure/cloud/deploy_cloud_run.sh
  ./infrastructure/cloud/deploy_cloud_run.sh
  ```
- **Windows PowerShell:**
  ```powershell
  .\infrastructure\cloud\deploy_cloud_run.ps1
  ```

---

## 5. Verifying Deployment & Monitoring
1. **Access Application:** Open the deployed HTTPS URL returned by Cloud Run.
2. **Health Check Probe:**
   ```bash
   curl -I https://YOUR_SERVICE_URL/_stcore/health
   # Returns: HTTP/2 200 OK
   ```
3. **View Real-Time Logs:**
   ```bash
   gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=nexusrag" --limit=30
   ```
4. **Monitor Metrics:** Open Google Cloud Console -> Cloud Run -> `nexusrag` -> **Metrics** to observe active container instances, CPU/memory utilization, and request latency graphs.
