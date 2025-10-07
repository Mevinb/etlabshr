import requests
import json

def test_results():
    print("Testing Results Endpoint...")
    
    # Step 1: Login
    print("1. Testing login...")
    login_response = requests.post('http://localhost:5000/api/login', json={
        'username': '224079',
        'password': 'Midhun@123123'
    })
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(login_response.text)
        return
    
    print("✅ Login successful")
    login_data = login_response.json()
    token = login_data.get('token')
    
    if not token:
        print("❌ No token received")
        return
    
    # Step 2: Test Results with semester 3
    print("\n2. Testing results endpoint with semester 3...")
    headers = {'Authorization': f'Bearer {token}'}
    
    results_response = requests.get('http://localhost:5000/api/results?semester=3', headers=headers)
    
    print(f"Results Response Status: {results_response.status_code}")
    
    if results_response.status_code == 200:
        print("✅ Results endpoint working")
        results_data = results_response.json()
        print(f"Results data: {json.dumps(results_data, indent=2)}")
    else:
        print("❌ Results endpoint failed")
        print(f"Response: {results_response.text}")

if __name__ == "__main__":
    test_results()