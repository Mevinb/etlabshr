import requests

def test_api_simple():
    print("🔍 Simple API Test...")
    
    try:
        # Test status endpoint
        print("Testing status...")
        response = requests.get('http://localhost:5000/api/status', timeout=5)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("✅ Status endpoint working!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_api_simple()