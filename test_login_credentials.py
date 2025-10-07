#!/usr/bin/env python3
"""
Test login credentials directly with the API
"""

import requests
import json

def test_login(username, password):
    """Test login with provided credentials"""
    
    url = "http://127.0.0.1:5000/api/login"
    
    login_data = {
        "username": username,
        "password": password
    }
    
    print(f"🔍 Testing login for user: {username}")
    print(f"🌐 URL: {url}")
    print(f"📤 Data: {json.dumps(login_data, indent=2)}")
    print("-" * 50)
    
    try:
        response = requests.post(url, json=login_data, timeout=10)
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        print(f"📝 Response Text: {response.text}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✅ Success! Token received: {data.get('token', 'No token')}")
                return True, data.get('token')
            except json.JSONDecodeError:
                print("❌ Success but invalid JSON response")
                return False, None
        else:
            print(f"❌ Login failed with status {response.status_code}")
            try:
                error_data = response.json()
                print(f"📝 Error details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📝 Raw error: {response.text}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - server not running")
        return False, None
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return False, None
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False, None

def test_status():
    """Test if API is responding"""
    try:
        response = requests.get("http://127.0.0.1:5000/api/status", timeout=5)
        print(f"🔍 API Status: {response.status_code}")
        print(f"📝 Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ API Status check failed: {e}")
        return False

if __name__ == "__main__":
    print("🎓 ETLab Login Credential Test")
    print("=" * 50)
    
    # Test API status first
    print("1. Testing API connectivity...")
    if not test_status():
        print("❌ API is not responding. Make sure the Flask server is running.")
        exit(1)
    
    print("\n2. Testing login credentials...")
    username = "224789"
    password = "mevinbenty12+"
    
    success, token = test_login(username, password)
    
    if success:
        print(f"\n🎉 Login successful!")
        print(f"🔑 Token: {token}")
    else:
        print(f"\n❌ Login failed!")
        print("\nPossible issues:")
        print("- Wrong username or password")
        print("- ETLab portal is down") 
        print("- Network connectivity issues")
        print("- API server error")