#!/usr/bin/env python3

import requests
import json

def test_all_endpoints():
    base_url = "http://localhost:5000"
    username = "224079"
    password = "Midhun@123123"
    
    print("🚀 Quick ETLab API Test")
    print("=" * 40)
    
    # Test login
    print("\n🧪 Testing Login...")
    login_response = requests.post(f"{base_url}/api/login", json={"username": username, "password": password})
    if login_response.status_code == 200:
        token = login_response.json().get("token")
        print(f"✅ Login successful! Token: {token[:20]}...")
        
        headers = {"Authorization": token}
        
        # Test results endpoint
        print("\n🧪 Testing Results (Semester 3)...")
        results_response = requests.get(f"{base_url}/api/results?semester=3", headers=headers)
        print(f"Status: {results_response.status_code}")
        if results_response.status_code == 200:
            data = results_response.json()
            print(f"✅ Results: {data.get('total_sessional_exams', 0)} sessional exams, {data.get('total_module_tests', 0)} module tests, {data.get('total_class_projects', 0)} class projects")
        else:
            print(f"❌ Results failed: {results_response.text}")
        
        # Test profile
        print("\n🧪 Testing Profile...")
        profile_response = requests.get(f"{base_url}/api/profile", headers=headers)
        print(f"Status: {profile_response.status_code}")
        if profile_response.status_code == 200:
            data = profile_response.json()
            print(f"✅ Profile: {data.get('name', 'Unknown')}")
        else:
            print(f"❌ Profile failed: {profile_response.text}")
        
        # Test attendance
        print("\n🧪 Testing Attendance (Semester 3)...")
        attendance_response = requests.get(f"{base_url}/api/attendance?semester=3", headers=headers)
        print(f"Status: {attendance_response.status_code}")
        if attendance_response.status_code == 200:
            data = attendance_response.json()
            print(f"✅ Attendance: {data.get('name', 'Unknown')}")
        else:
            print(f"❌ Attendance failed: {attendance_response.text}")
            
    else:
        print(f"❌ Login failed: {login_response.text}")

if __name__ == "__main__":
    test_all_endpoints()