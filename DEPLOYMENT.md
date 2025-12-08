# Google Cloud Run Deployment Guide

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **gcloud CLI** installed: https://cloud.google.com/sdk/docs/install
3. **Docker** installed locally (for testing)
4. **Bria API Token** from your Bria account

## Step-by-Step Deployment

### 1. Set Up Google Cloud Project

```bash
# Login to Google Cloud
gcloud auth login

# Create a new project (or use existing)
gcloud projects create brand-localizer-prod --name="Brand Localizer"

# Set the project
gcloud config set project brand-localizer-prod

# Enable required APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable secretmanager.googleapis.com
```

### 2. Store API Token as Secret

```bash
# Create secret for Bria API token
echo -n "YOUR_BRIA_API_TOKEN" | gcloud secrets create bria-api-token --data-file=-

# Grant Cloud Run access to the secret
gcloud secrets add-iam-policy-binding bria-api-token \
    --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
    --role="roles/secretmanager.secretAccessor"

# Find your PROJECT_NUMBER with:
gcloud projects describe brand-localizer-prod --format="value(projectNumber)"
```

### 3. Test Docker Build Locally (Recommended)

```bash
# Build the Docker image
docker build -t brand-localizer:test .

# Test run locally
docker run -p 8080:8080 -e BRIA_API_TOKEN="your_token" brand-localizer:test

# Visit http://localhost:8080 to verify it works
```

### 4. Deploy to Cloud Run

#### Option A: Using Cloud Build (Automated)

```bash
# Submit build and deploy
gcloud builds submit --config cloudbuild.yaml

# Get the service URL
gcloud run services describe brand-localizer --region=us-central1 --format="value(status.url)"
```

#### Option B: Manual Deployment

```bash
# Build and push image
gcloud builds submit --tag gcr.io/brand-localizer-prod/brand-localizer

# Deploy to Cloud Run
gcloud run deploy brand-localizer \
    --image gcr.io/brand-localizer-prod/brand-localizer \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10 \
    --set-secrets BRIA_API_TOKEN=bria-api-token:latest
```

### 5. Verify Deployment

```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe brand-localizer --region=us-central1 --format="value(status.url)")

# Test the endpoint
curl $SERVICE_URL/_stcore/health

# Open in browser
echo "Visit: $SERVICE_URL"
```

## Troubleshooting Common Issues

### Issue 1: Python Dependency Conflicts

**Symptom**: Build fails with dependency resolution errors

**Solution**: The Dockerfile installs dependencies in stages:
1. numpy first (base dependency)
2. PyTorch separately (large package)
3. Remaining packages

If issues persist, try pinning specific versions in `requirements.txt`.

### Issue 2: Memory Errors During Build

**Symptom**: "Killed" or out-of-memory errors

**Solution**: Increase Cloud Build machine type:
```bash
gcloud builds submit --config cloudbuild.yaml --machine-type=N1_HIGHCPU_8
```

### Issue 3: Container Startup Timeout

**Symptom**: Service fails to start within timeout

**Solution**: Increase timeout and ensure health check passes:
```bash
gcloud run services update brand-localizer \
    --region us-central1 \
    --timeout 600
```

### Issue 4: OpenCV/cv2 Import Errors

**Symptom**: `ImportError: libGL.so.1: cannot open shared object file`

**Solution**: Already handled in Dockerfile with system dependencies:
- libgl1-mesa-glx
- libglib2.0-0
- libsm6
- libxext6

### Issue 5: Secret Not Found

**Symptom**: `BRIA_API_TOKEN` environment variable is empty

**Solution**: Verify secret exists and permissions are correct:
```bash
# Check secret
gcloud secrets describe bria-api-token

# Verify IAM binding
gcloud secrets get-iam-policy bria-api-token
```

### Issue 6: Large Image Size / Slow Builds

**Solution**: Use CPU-only PyTorch (already configured):
```bash
# The Dockerfile uses CPU-only PyTorch to reduce size
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

## Cost Optimization

### Estimated Costs
- **Cloud Run**: Pay per request, ~$0.00002400 per request
- **Container Registry**: ~$0.026 per GB/month
- **Secret Manager**: ~$0.06 per secret/month

### Optimization Tips
1. Set `--max-instances` to limit concurrent containers
2. Use `--min-instances 0` to scale to zero when idle
3. Set appropriate `--memory` and `--cpu` (2Gi/2CPU recommended)
4. Enable request timeout to prevent long-running requests

## Monitoring

```bash
# View logs
gcloud run services logs read brand-localizer --region=us-central1

# Monitor metrics
gcloud run services describe brand-localizer --region=us-central1
```

## Custom Domain (Optional)

```bash
# Map custom domain
gcloud run domain-mappings create --service brand-localizer --domain your-domain.com --region us-central1
```

## CI/CD Integration

For automated deployments on git push, connect your repository to Cloud Build:

```bash
# Create trigger
gcloud builds triggers create github \
    --repo-name=brand-localizer \
    --repo-owner=YOUR_GITHUB_USERNAME \
    --branch-pattern="^main$" \
    --build-config=cloudbuild.yaml
```

## Environment Variables

If you need additional environment variables:

```bash
gcloud run services update brand-localizer \
    --region us-central1 \
    --set-env-vars "KEY1=value1,KEY2=value2"
```

## Rollback

If deployment fails, rollback to previous version:

```bash
# List revisions
gcloud run revisions list --service brand-localizer --region us-central1

# Rollback to specific revision
gcloud run services update-traffic brand-localizer \
    --region us-central1 \
    --to-revisions REVISION_NAME=100
```

## Support

For issues specific to:
- **Bria API**: Contact Bria support
- **Google Cloud**: Check Cloud Run documentation
- **Application**: Review logs with `gcloud run services logs read`
