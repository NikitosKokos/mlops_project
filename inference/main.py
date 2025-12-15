from fastapi import FastAPI, UploadFile, File, HTTPException
from ultralytics import YOLO
from PIL import Image
import io
import os

app = FastAPI(title="SentinelAI Gun Detection API")

# Load model (ensure best.pt is in the same folder during Docker build)
# For local testing, use a pretrained model if best.pt doesn't exist
model = None
MODEL_LOADED = False

def load_model():
    """Load the model, using pretrained if best.pt doesn't exist (for local testing)"""
    global model, MODEL_LOADED
    
    if MODEL_LOADED:
        return model
    
    model_path = "best.pt"
    
    # Check if best.pt exists and is valid
    if os.path.exists(model_path) and os.path.getsize(model_path) > 1000:  # At least 1KB
        try:
            model = YOLO(model_path)
            MODEL_LOADED = True
            print(f"✅ Loaded trained model from {model_path}")
            return model
        except Exception as e:
            print(f"⚠️  Warning: Could not load {model_path}: {e}")
            print("   Falling back to pretrained model for testing...")
    
    # Fallback to pretrained model for local testing
    try:
        model = YOLO("yolov8n.pt")  # Use pretrained nano model
        MODEL_LOADED = True
        print("⚠️  Using pretrained YOLOv8n model (best.pt not found or invalid)")
        print("   Note: This will detect general objects, not specifically guns")
        return model
    except Exception as e:
        raise RuntimeError(f"Failed to load any model: {e}")

# Load model on startup
load_model() 

@app.get("/")
def home():
    return {"status": "SentinelAI Active"}

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    # Ensure model is loaded
    if model is None:
        load_model()
    
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded. Please ensure best.pt exists or model is available.")
    
    # Read image
    contents = await file.read()
    image = Image.open(io.BytesIO(contents))
    
    # Inference
    results = model(image)
    
    detections = []
    for result in results:
        for box in result.boxes:
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            label = model.names[cls]
            if conf > 0.5: # Confidence threshold
                detections.append({
                    "label": label,
                    "confidence": conf,
                    "box": box.xyxy[0].tolist()
                })
    
    return {
        "filename": file.filename,
        "detections": detections,
        "alert": len(detections) > 0
    }

