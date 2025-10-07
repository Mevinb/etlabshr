#!/usr/bin/env python3
"""
Direct test of login functionality
"""

import requests
import json
import time
from app import create_app

def test_direct_login():
    """Test login directly through the Flask app"""
    
    app = create_app()
    
    with app.test_client() as client:
        print("🔍 Testing login with Flask test client...")
        
        login_data = {
            "username": "224789",
            "password": "mevinbenty12+"
        }
        
        print(f"📤 Login data: {json.dumps(login_data, indent=2)}")
        
        response = client.post('/api/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📝 Response: {response.get_data(as_text=True)}")
        
        if response.status_code == 200:
            try:
                data = response.get_json()
                print(f"✅ Login successful!")
                print(f"🔑 Token: {data.get('token', 'No token')}")
                return True
            except:
                print(f"❌ Success but invalid JSON")
                return False
        else:
            print(f"❌ Login failed")
            try:
                error_data = response.get_json()
                print(f"📝 Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"📝 Raw error: {response.get_data(as_text=True)}")
            return False

if __name__ == "__main__":
    print("🎓 Direct ETLab Login Test")
    print("=" * 50)
    test_direct_login()