# Quick Start Testing Guide

This is a condensed guide to quickly test your SentinelAI project.

## 🚀 Quick Test (5 minutes)

### Step 1: Start the API

```bash
cd inference
uvicorn main:app --reload
```

Keep this terminal open. The API should be running at `http://localhost:8000`

### Step 2: Test in a New Terminal

**Option A: Using the test script (Recommended)**

```bash
# Test health endpoint
python inference/test_api.py --health

# Test with an image (use any image from your dataset)
python inference/test_api.py "gun-dataset/Gun with webcam views.v1i.yolov8/test/images/6_22_4_0004172_jpg.rf.138bf1cdc451608f4fa6dd98b8d6f853.jpg"
```

**Option B: Using curl**

```bash
# Health check
curl http://localhost:8000/

# Detection (replace with actual image path)
curl -X POST "http://localhost:8000/detect" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_image.jpg"
```

**Option C: Using the browser**

1. Open: `http://localhost:8000/docs`
2. Click on `/detect` endpoint
3. Click "Try it out"
4. Upload an image
5. Click "Execute"

## 📋 What You Already Have

✅ **Test Script**: `inference/test_api.py` - Enhanced with multiple test modes
✅ **Test Pipeline**: `pipeline-job-test.yaml` - Quick Azure ML test (1 epoch)
✅ **Dataset**: Two gun detection datasets ready for testing
✅ **Model**: `best.pt` exists in inference folder
✅ **Dockerfile**: Ready for container testing
✅ **K8s Config**: Deployment manifest ready

## 🧪 Test Modes

### 1. Health Check Only

```bash
python inference/test_api.py --health
```

### 2. Single Image Test

```bash
python inference/test_api.py <image_path>
```

### 3. Comprehensive Test Suite

```bash
python inference/test_api.py --all http://localhost:8000 <image_path>
```

## 🐳 Docker Quick Test

```bash
cd inference
docker build -t sentinel-api:test .
docker run -p 8000:8000 sentinel-api:test

# In another terminal
python inference/test_api.py --health
```

## ☁️ Azure ML Quick Test

```bash
# Submit test pipeline (1 epoch, ~5-10 minutes)
az ml job create --file pipeline-job-test.yaml --stream
```

## 📊 Expected Results

**Health Check:**

```json
{ "status": "SentinelAI Active" }
```

**Detection:**

```json
{
  "filename": "image.jpg",
  "detections": [...],
  "alert": true/false
}
```

## ❌ Troubleshooting

**API won't start:**

-  Check if port 8000 is in use: `netstat -ano | findstr :8000` (Windows)
-  Install dependencies: `pip install -r inference/requirements.txt`

**Model not loading:**

-  Check if `best.pt` exists: `ls inference/best.pt`
-  API will fallback to pretrained YOLOv8n if `best.pt` is missing

**Connection refused:**

-  Make sure API is running in another terminal
-  Check the URL: should be `http://localhost:8000`

## 📚 More Details

For comprehensive testing instructions, see [TESTING.md](TESTING.md)
