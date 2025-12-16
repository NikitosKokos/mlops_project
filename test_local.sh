#!/bin/bash
# Quick local testing script for SentinelAI
# Usage: ./test_local.sh [image_path]

set -e

API_URL="http://localhost:8000"
IMAGE_PATH="${1:-}"

echo "=========================================="
echo "SentinelAI Local Testing Script"
echo "=========================================="
echo ""

# Check if API is running
echo "Checking if API is running..."
if curl -s -f "${API_URL}/" > /dev/null 2>&1; then
    echo "✅ API is running at ${API_URL}"
else
    echo "❌ API is not running!"
    echo "   Start it with: cd inference && uvicorn main:app --reload"
    exit 1
fi

# Test health endpoint
echo ""
echo "Testing health endpoint..."
python inference/test_api.py --health "${API_URL}"

# Test detection if image provided
if [ -n "$IMAGE_PATH" ]; then
    echo ""
    echo "Testing detection endpoint..."
    if [ -f "$IMAGE_PATH" ]; then
        python inference/test_api.py "$IMAGE_PATH" "${API_URL}"
    else
        echo "❌ Image file not found: $IMAGE_PATH"
        exit 1
    fi
else
    echo ""
    echo "⚠️  No image provided. Skipping detection test."
    echo "   Usage: ./test_local.sh <image_path>"
fi

echo ""
echo "=========================================="
echo "Testing complete!"
echo "=========================================="

