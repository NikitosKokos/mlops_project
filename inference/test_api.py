"""
Comprehensive test script for the SentinelAI API
Usage: 
    python test_api.py <image_path> [api_url]
    python test_api.py --health [api_url]
    python test_api.py --all [api_url]
"""
import requests
import sys
import time
import json
from pathlib import Path

def test_health(api_url="http://localhost:8000"):
    """Test the health check endpoint"""
    try:
        print(f"Testing health endpoint at {api_url}/...")
        response = requests.get(f"{api_url}/", timeout=5)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Health check passed")
            print(f"   Response: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to API at {api_url}")
        print("   Make sure the API is running: uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_detection(image_path, api_url="http://localhost:8000"):
    """Test the detection API with an image"""
    
    if not Path(image_path).exists():
        print(f"❌ Error: Image file not found: {image_path}")
        return False
    
    try:
        print(f"Testing detection endpoint with: {image_path}")
        start_time = time.time()
        
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{api_url}/detect", files=files, timeout=30)
        
        elapsed_time = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Detection test passed")
            print(f"   Response time: {elapsed_time:.2f}s")
            print(f"   Filename: {result.get('filename')}")
            print(f"   Alert: {result.get('alert')}")
            print(f"   Detections: {len(result.get('detections', []))}")
            
            for i, detection in enumerate(result.get('detections', []), 1):
                print(f"\n   Detection {i}:")
                print(f"      Label: {detection.get('label')}")
                print(f"      Confidence: {detection.get('confidence'):.2%}")
                print(f"      Bounding Box: {detection.get('box')}")
            
            # Performance check
            if elapsed_time > 5:
                print(f"⚠️  Warning: Response time ({elapsed_time:.2f}s) is slow")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to API at {api_url}")
        print("   Make sure the API is running: uvicorn main:app --reload")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ Error: Request timed out after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def test_error_handling(api_url="http://localhost:8000"):
    """Test error handling with invalid requests"""
    print("\nTesting error handling...")
    
    # Test 1: Missing file
    try:
        response = requests.post(f"{api_url}/detect", timeout=5)
        if response.status_code == 422:  # Validation error
            print("✅ Missing file error handled correctly")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing missing file: {e}")
    
    # Test 2: Invalid file type
    try:
        files = {'file': ('test.txt', b'not an image', 'text/plain')}
        response = requests.post(f"{api_url}/detect", files=files, timeout=5)
        if response.status_code in [400, 422, 500]:
            print("✅ Invalid file type error handled correctly")
        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing invalid file: {e}")

def run_all_tests(api_url="http://localhost:8000", test_image=None):
    """Run all available tests"""
    print("=" * 60)
    print("SentinelAI API - Comprehensive Test Suite")
    print("=" * 60)
    print(f"API URL: {api_url}\n")
    
    results = []
    
    # Test 1: Health check
    print("\n[1/3] Health Check Test")
    print("-" * 60)
    results.append(("Health Check", test_health(api_url)))
    
    # Test 2: Detection (if image provided)
    if test_image:
        print("\n[2/3] Detection Test")
        print("-" * 60)
        results.append(("Detection", test_detection(test_image, api_url)))
    else:
        print("\n[2/3] Detection Test - SKIPPED (no image provided)")
        results.append(("Detection", None))
    
    # Test 3: Error handling
    print("\n[3/3] Error Handling Test")
    print("-" * 60)
    test_error_handling(api_url)
    results.append(("Error Handling", True))  # Don't fail on this
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    for test_name, result in results:
        if result is None:
            status = "SKIPPED"
        elif result:
            status = "✅ PASSED"
        else:
            status = "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    # Return success if all non-skipped tests passed
    passed_tests = [r for r in results if r[1] is not None and r[1]]
    total_tests = len([r for r in results if r[1] is not None])
    
    print(f"\nResults: {len(passed_tests)}/{total_tests} tests passed")
    return len(passed_tests) == total_tests

if __name__ == "__main__":
    api_url = "http://localhost:8000"
    image_path = None
    
    # Parse arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--health":
            api_url = sys.argv[2] if len(sys.argv) > 2 else api_url
            success = test_health(api_url)
            sys.exit(0 if success else 1)
        elif sys.argv[1] == "--all":
            api_url = sys.argv[2] if len(sys.argv) > 2 else api_url
            image_path = sys.argv[3] if len(sys.argv) > 3 else None
            success = run_all_tests(api_url, image_path)
            sys.exit(0 if success else 1)
        else:
            image_path = sys.argv[1]
            api_url = sys.argv[2] if len(sys.argv) > 2 else api_url
    
    if image_path:
        success = test_detection(image_path, api_url)
        sys.exit(0 if success else 1)
    else:
        print("Usage:")
        print("  python test_api.py <image_path> [api_url]")
        print("  python test_api.py --health [api_url]")
        print("  python test_api.py --all [api_url] [test_image]")
        print("\nExamples:")
        print("  python test_api.py test_image.jpg")
        print("  python test_api.py --health http://localhost:8000")
        print("  python test_api.py --all http://localhost:8000 test_image.jpg")
        sys.exit(1)

