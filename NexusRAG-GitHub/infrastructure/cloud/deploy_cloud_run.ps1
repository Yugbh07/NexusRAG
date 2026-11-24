# ==============================================================================
# NexusRAG - Automated Google Cloud Run Deployment Script (PowerShell)
# Region: asia-south1 (Mumbai) | Minimal Cost Tier (0-min instances)
# ==============================================================================

param (
    [string]$ProjectId = $env:GCP_PROJECT_ID,
    [string]$Region = "asia-south1",
    [string]$ServiceName = "nexusrag",
    [string]$RepoName = "nexusrag-repo",
    [string]$ImageTag = "v1.0.0"
)

$ErrorActionPreference = "Stop"

if (-not $ProjectId) {
    $ProjectId = (gcloud config get-value project 2>$null)
}

if (-not $ProjectId) {
    Write-Error "ERROR: Project ID is not specified. Set it via `$env:GCP_PROJECT_ID = 'your-id' or pass -ProjectId 'your-id'"
    exit 1
}

$ImageUri = "${Region}-docker.pkg.dev/${ProjectId}/${RepoName}/${ServiceName}:${ImageTag}"

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "⚡ Starting NexusRAG Google Cloud Run Deployment" -ForegroundColor Cyan
Write-Host "Project ID: $ProjectId"
Write-Host "Region:     $Region"
Write-Host "Image URI:  $ImageUri"
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Enable APIs
Write-Host "Step 1/5: Enabling required Google Cloud APIs..." -ForegroundColor Yellow
gcloud services enable `
    run.googleapis.com `
    artifactregistry.googleapis.com `
    cloudbuild.googleapis.com `
    storage.googleapis.com `
    logging.googleapis.com `
    monitoring.googleapis.com

# 2. Check / Create Artifact Registry
Write-Host "Step 2/5: Verifying Artifact Registry repository..." -ForegroundColor Yellow
$repoCheck = gcloud artifacts repositories describe $RepoName --location=$Region 2>$null
if (-not $repoCheck) {
    Write-Host "Creating Artifact Registry repository '$RepoName' in $Region..."
    gcloud artifacts repositories create $RepoName `
        --repository-format=docker `
        --location=$Region `
        --description="NexusRAG Container Images"
}

# 3. Build & Push via Cloud Build
Write-Host "Step 3/5: Submitting image build to Google Cloud Build..." -ForegroundColor Yellow
gcloud builds submit --tag $ImageUri .

# 4. Deploy to Cloud Run
Write-Host "Step 4/5: Deploying container to Google Cloud Run..." -ForegroundColor Yellow
gcloud run deploy $ServiceName `
    --image=$ImageUri `
    --platform=managed `
    --region=$Region `
    --allow-unauthenticated `
    --memory=1Gi `
    --cpu=1 `
    --min-instances=0 `
    --max-instances=3 `
    --concurrency=40 `
    --timeout=300 `
    --set-env-vars="PORT=8501,STORAGE_BACKEND=local,GEMINI_MODEL=gemini-2.5-flash"

# 5. Output URL
$ServiceUrl = (gcloud run services describe $ServiceName --platform=managed --region=$Region --format="value(status.url)")
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "🎉 SUCCESS: NexusRAG deployed successfully to Google Cloud Run!" -ForegroundColor Green
Write-Host "Service Live URL: $ServiceUrl" -ForegroundColor Green
Write-Host "Check Health:     ${ServiceUrl}/_stcore/health" -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
