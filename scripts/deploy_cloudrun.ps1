param(
  [string]$projectId = "baloncestoia-e0724",
  [string]$region = "us-central1",
  [string]$imageName = "plan-basket"
)

Write-Host "Authenticating with gcloud..."
gcloud auth login

gcloud config set project $projectId

Write-Host "Submitting build to Cloud Build..."
gcloud builds submit --tag gcr.io/$projectId/$imageName:latest

Write-Host "Deploying to Cloud Run..."
gcloud run deploy $imageName --image gcr.io/$projectId/$imageName:latest --platform managed --region $region --allow-unauthenticated

Write-Host "Cloud Run deploy finished. You can find the service URL with:"
gcloud run services describe $imageName --region $region --format 'value(status.url)'
