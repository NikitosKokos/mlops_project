# SentinelAI Testing Guide

This guide covers all testing scenarios for the SentinelAI project, from local development to production deployment.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local API Testing](#local-api-testing)
3. [Training Testing](#training-testing)
4. [Docker Testing](#docker-testing)
5. [Kubernetes Testing](#kubernetes-testing)
6. [Integration Testing](#integration-testing)
7. [Test Data](#test-data)

## Prerequisites

Before testing, ensure you have:

```bash
# Install Python dependencies
cd inference
pip install -r requirements.txt

# Verify model file exists
ls best.pt  # Should exist in inference/ directory
```

## Local API Testing

### 1. Start the API Server

```bash
cd inference
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 2. Test Health Endpoint

```bash
# Using curl
curl http://localhost:8000/

# Expected response:
# {"status":"SentinelAI Active"}
```

### 3. Test Detection Endpoint

**Using the provided test script:**

```bash
cd inference
python test_api.py <path-to-image.jpg>
```

**Using curl:**

```bash
curl -X POST "http://localhost:8000/detect" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_image.jpg"
```

**Using Python requests:**

```python
import requests

with open('test_image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/detect',
        files={'file': f}
    )
    print(response.json())
```

**Expected Response:**

```json
{
  "filename": "test_image.jpg",
  "detections": [
    {
      "label": "gun",
      "confidence": 0.95,
      "box": [100, 150, 200, 250]
    }
  ],
  "alert": true
}
```

### 4. Test with Sample Images

You can use images from your dataset:

```bash
# Test with dataset images
python test_api.py "../gun-dataset/Gun with webcam views.v1i.yolov8/test/images/<image-name>.jpg"
```

## Training Testing

### Local Training Test

Test the training script locally before deploying to Azure:

```bash
cd components/training

# Test with 1 epoch (quick test)
python train.py \
  --data_path "../../gun-dataset/Gun with webcam views.v1i.yolov8" \
  --epochs 1 \
  --model_output "../../test_output"

# Check output
ls ../../test_output/best.pt
```

### Azure ML Pipeline Testing

**Option 1: Using the test pipeline (1 epoch)**

```bash
# Configure Azure ML defaults
az configure --defaults group=<YOUR_RESOURCE_GROUP> workspace=<YOUR_WORKSPACE> location=<YOUR_LOCATION>

# Submit test pipeline
az ml job create --file pipeline-job-test.yaml --stream
```

**Option 2: Using the full pipeline**

```bash
az ml job create --file pipeline-job.yaml --stream
```

**Monitor the job:**

```bash
# List recent jobs
az ml job list --query "[?experiment_name=='gun-detection-exp']" -o table

# Stream logs
az ml job stream --name <job-name>
```

## Docker Testing

### 1. Build Docker Image

```bash
cd inference

# Build image
docker build -t sentinel-api:local .

# Verify image
docker images | grep sentinel-api
```

### 2. Run Container Locally

```bash
# Run container
docker run -d \
  --name sentinel-test \
  -p 8000:8000 \
  sentinel-api:local

# Check logs
docker logs -f sentinel-test

# Test API
curl http://localhost:8000/
```

### 3. Test with Image File

```bash
# Copy test image into container
docker cp test_image.jpg sentinel-test:/tmp/

# Or mount a volume
docker run -d \
  --name sentinel-test \
  -p 8000:8000 \
  -v $(pwd):/app/test_images \
  sentinel-api:local
```

### 4. Stop and Cleanup

```bash
docker stop sentinel-test
docker rm sentinel-test
docker rmi sentinel-api:local
```

## Kubernetes Testing

### Prerequisites

```bash
# Ensure kubectl is configured
kubectl get nodes

# Ensure you have access to your cluster
kubectl cluster-info
```

### 1. Update Deployment File

Edit `k8s/deployment.yaml` and replace:
- `PLACEHOLDER_USERNAME` with your GitHub username
- Or use a local image: `image: sentinel-api:local`

### 2. Deploy to Kubernetes

```bash
# Apply deployment
kubectl apply -f k8s/deployment.yaml

# Check deployment status
kubectl get deployments
kubectl get pods
kubectl get services
```

### 3. Test the Service

```bash
# Get service IP/URL
kubectl get service sentinel-service

# Port forward for local testing
kubectl port-forward service/sentinel-service 8000:80

# Test API
curl http://localhost:8000/
```

### 4. Check Logs

```bash
# Get pod name
kubectl get pods

# View logs
kubectl logs -f <pod-name>

# View logs from all pods
kubectl logs -f -l app=sentinel-api
```

### 5. Cleanup

```bash
kubectl delete -f k8s/deployment.yaml
```

## Integration Testing

### Automated Test Suite

Run the comprehensive test suite:

```bash
cd inference
python -m pytest test_api.py -v
```

Or use the enhanced test script:

```bash
python test_api.py test_image.jpg http://localhost:8000
```

### Test Scenarios

1. **Health Check Test**
   - Verify API is running
   - Check response format

2. **Detection Test**
   - Upload valid image
   - Verify detection results
   - Check confidence thresholds

3. **Error Handling Test**
   - Invalid file format
   - Missing file
   - Large file size

4. **Performance Test**
   - Response time < 2 seconds
   - Concurrent requests
   - Memory usage

## Test Data

### Using Dataset Images

Your project includes test images in:

```
gun-dataset/
├── Gun with webcam views.v1i.yolov8/
│   └── test/
│       └── images/
└── New.v1i.yolov8/
    └── test/
        └── images/
```

### Create Test Image List

```bash
# List test images
find gun-dataset -name "*.jpg" -path "*/test/*" | head -5 > test_images.txt

# Use for batch testing
while IFS= read -r img; do
  python inference/test_api.py "$img"
done < test_images.txt
```

## Troubleshooting

### API Not Starting

```bash
# Check if port is in use
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Mac/Linux

# Check Python dependencies
pip list | grep -E "fastapi|uvicorn|ultralytics"
```

### Model Not Loading

```bash
# Verify model file exists and is valid
ls -lh inference/best.pt
file inference/best.pt  # Should show PyTorch model

# Check model size (should be > 1MB)
du -h inference/best.pt
```

### Docker Build Fails

```bash
# Check Dockerfile syntax
docker build --no-cache -t sentinel-api:test .

# Check for missing files
docker build -t sentinel-api:test . 2>&1 | grep -i error
```

### Kubernetes Pods Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name>

# Check events
kubectl get events --sort-by='.lastTimestamp'

# Check image pull errors
kubectl describe pod <pod-name> | grep -i image
```

## Performance Benchmarks

Expected performance metrics:

- **API Response Time**: < 2 seconds per image
- **Model Loading**: < 5 seconds on first request
- **Memory Usage**: < 1GB per pod
- **CPU Usage**: < 50% under normal load

## Next Steps

After successful testing:

1. ✅ Verify all endpoints work
2. ✅ Test with production-like data
3. ✅ Monitor resource usage
4. ✅ Set up CI/CD pipeline
5. ✅ Configure monitoring and alerting

