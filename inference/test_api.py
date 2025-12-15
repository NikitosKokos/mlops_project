"""
Simple test script for the SentinelAI API
Usage: python test_api.py <image_path>
"""
import requests
import sys

def test_api(image_path, api_url="http://localhost:8000"):
    """Test the detection API with an image"""
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{api_url}/detect", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API Response:")
            print(f"   Filename: {result.get('filename')}")
            print(f"   Alert: {result.get('alert')}")
            print(f"   Detections: {len(result.get('detections', []))}")
            
            for i, detection in enumerate(result.get('detections', []), 1):
                print(f"\n   Detection {i}:")
                print(f"      Label: {detection.get('label')}")
                print(f"      Confidence: {detection.get('confidence'):.2%}")
                print(f"      Bounding Box: {detection.get('box')}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)
            return False
            
    except FileNotFoundError:
        print(f"❌ Error: Image file not found: {image_path}")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Error: Could not connect to API at {api_url}")
        print("   Make sure the API is running: uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_api.py <image_path> [api_url]")
        print("Example: python test_api.py test_image.jpg http://localhost:8000")
        sys.exit(1)
    
    image_path = sys.argv[1]
    api_url = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8000"
    
    print(f"Testing SentinelAI API with image: {image_path}")
    print(f"API URL: {api_url}\n")
    
    success = test_api(image_path, api_url)
    sys.exit(0 if success else 1)

