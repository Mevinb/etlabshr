#!/usr/bin/env python3

import requests
import json

def test_results_endpoint():
    base_url = "http://localhost:5000"
    username = "224079"
    password = "Midhun@123123"
    
    print("🔍 Testing Results Endpoint Debug")
    print("=" * 40)
    
    try:
        # Test login first
        print("1. Testing login...")
        login_response = requests.post(f"{base_url}/api/login", json={"username": username, "password": password})
        print(f"   Login Status: {login_response.status_code}")
        
        if login_response.status_code == 200:
            token = login_response.json().get("token")
            print(f"   ✅ Login successful! Token: {token[:20]}...")
            
            headers = {"Authorization": token}
            
            # Test results endpoint with detailed error handling
            print("\n2. Testing Results endpoint...")
            try:
                results_response = requests.get(f"{base_url}/api/results?semester=3", headers=headers, timeout=30)
                print(f"   Results Status: {results_response.status_code}")
                print(f"   Response Headers: {dict(results_response.headers)}")
                
                if results_response.status_code == 200:
                    try:
                        data = results_response.json()
                        print(f"   ✅ Results Response:")
                        print(f"      - Sessional Exams: {data.get('total_sessional_exams', 0)}")
                        print(f"      - Module Tests: {data.get('total_module_tests', 0)}")
                        print(f"      - Class Projects: {data.get('total_class_projects', 0)}")
                        
                        # Show some sample data
                        if data.get('sessional_exams'):
                            print(f"      - Sample Sessional Exam: {data['sessional_exams'][0]}")
                        
                    except json.JSONDecodeError as e:
                        print(f"   ❌ JSON decode error: {e}")
                        print(f"   Raw response: {results_response.text[:500]}...")
                else:
                    print(f"   ❌ Results failed with status {results_response.status_code}")
                    print(f"   Error response: {results_response.text}")
                    
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Request failed: {e}")
                
        else:
            print(f"   ❌ Login failed: {login_response.text}")
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_results_endpoint()