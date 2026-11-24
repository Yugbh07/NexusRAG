#!/usr/bin/env bash
# ==============================================================================
# Google Cloud Storage Bucket Setup Script for NexusRAG Document Persistence
# ==============================================================================

set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:-$(gcloud config get-value project 2>/dev/null || echo '')}"
REGION="${GCP_REGION:-asia-south1}"
BUCKET_NAME="${1:-nexusrag-documents-${PROJECT_ID}}"

if [ -z "$PROJECT_ID" ]; then
    echo "ERROR: GCP_PROJECT_ID is not set."
    exit 1
fi

echo "Creating GCS Bucket gs://${BUCKET_NAME} in region ${REGION}..."
gcloud storage buckets create "gs://${BUCKET_NAME}" \
    --project="${PROJECT_ID}" \
    --location="${REGION}" \
    --uniform-bucket-level-access

echo "GCS Bucket created successfully: gs://${BUCKET_NAME}"
echo "Add to your .env file:"
echo "STORAGE_BACKEND=gcs"
echo "GCS_BUCKET_NAME=${BUCKET_NAME}"
