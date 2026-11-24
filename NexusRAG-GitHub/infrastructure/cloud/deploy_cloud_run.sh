#!/usr/bin/env bash
# ==============================================================================
# NexusRAG - Automated Google Cloud Run Deployment Script
# Region: asia-south1 (Mumbai) | Minimal Cost Tier (0-min instances)
# ==============================================================================

set -euo pipefail

# Configuration parameters
PROJECT_ID="${GCP_PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || echo '')}"
REGION="${GCP_REGION:-asia-south1}"
SERVICE_NAME="nexusrag"
REPO_NAME="nexusrag-repo"
IMAGE_TAG="v1.0.0"

if [ -z "$PROJECT_ID" ]; then
    echo "ERROR: GCP_PROJECT_ID is not set. Please set it via export GCP_PROJECT_ID=your-project-id"
    exit 1
fi

IMAGE_URI="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${SERVICE_NAME}:${IMAGE_TAG}"

echo "=========================================================="
echo "⚡ Starting NexusRAG Google Cloud Run Deployment"
echo "Project ID: $PROJECT_ID"
echo "Region:     $REGION"
echo "Image URI:  $IMAGE_URI"
echo "=========================================================="

# 1. Enable Required Cloud APIs
echo "Step 1/5: Enabling required Google Cloud APIs..."
gcloud services enable \
    run.googleapis.com \
    artifactregistry.googleapis.com \
    cloudbuild.googleapis.com \
    storage.googleapis.com \
    logging.googleapis.com \
    monitoring.googleapis.com

# 2. Create Artifact Registry Repository if not exists
echo "Step 2/5: Verifying Artifact Registry repository..."
if ! gcloud artifacts repositories describe "$REPO_NAME" --location="$REGION" >/dev/null 2>&1; then
    echo "Creating Artifact Registry repository '$REPO_NAME' in $REGION..."
    gcloud artifacts repositories create "$REPO_NAME" \
        --repository-format=docker \
        --location="$REGION" \
        --description="NexusRAG Container Images"
else
    echo "Artifact Registry repository '$REPO_NAME' already exists."
fi

# 3. Build & Push Image using Cloud Build (No local Docker daemon required)
echo "Step 3/5: Submitting image build to Google Cloud Build..."
gcloud builds submit --tag "$IMAGE_URI" .

# 4. Deploy to Cloud Run
echo "Step 4/5: Deploying container to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
    --image="$IMAGE_URI" \
    --platform=managed \
    --region="$REGION" \
    --allow-unauthenticated \
    --memory=1Gi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=3 \
    --concurrency=40 \
    --timeout=300 \
    --set-env-vars="PORT=8501,STORAGE_BACKEND=local,GEMINI_MODEL=gemini-2.5-flash"

# 5. Retrieve Service URL and verify deployment
echo "Step 5/5: Verifying deployed Cloud Run service..."
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --platform=managed --region="$REGION" --format="value(status.url)")

echo "=========================================================="
echo "🎉 SUCCESS: NexusRAG deployed successfully to Google Cloud Run!"
echo "Service Live URL: $SERVICE_URL"
echo "Check Health:     ${SERVICE_URL}/_stcore/health"
echo "=========================================================="
