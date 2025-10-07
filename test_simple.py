#!/usr/bin/env python3

import requests
import time

def test_api():
    print("Testing API connectivity...")
    
    try:
        # Give server time to start
        time.sleep(1)
        
        # Test status endpoint
        url = "http://127.0.0.1:5000/api/status"
        print(f"Testing: {url}")
        
        response = requests.get(url, timeout=5)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ API is working!")
            return True
        else:
            print("❌ API returned error status")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection refused - server not running")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_api()