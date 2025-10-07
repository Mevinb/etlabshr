import requests
import time

def test_web_interface():
    """Test the web interface and API endpoints"""
    print("🧪 Testing Web Interface and API...")
    
    base_url = 'http://localhost:5000'
    
    # Test 1: Check if main page loads
    print("\n1. Testing main page...")
    try:
        response = requests.get(f'{base_url}/')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Web interface loads successfully")
        else:
            print(f"   ❌ Web interface failed to load: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error accessing web interface: {e}")
        return
    
    # Test 2: Check API status endpoint
    print("\n2. Testing API status endpoint...")
    try:
        response = requests.get(f'{base_url}/api/status')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API Status: {data}")
        else:
            print(f"   ❌ API status failed: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error accessing API status: {e}")
    
    # Test 3: Test login endpoint
    print("\n3. Testing login endpoint...")
    try:
        login_data = {
            'username': '224079',
            'password': 'Midhun@123123'
        }
        response = requests.post(f'{base_url}/api/login', json=login_data)
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if 'token' in data:
                print("   ✅ Login successful!")
                token = data['token']
                
                # Test 4: Test authenticated endpoint
                print("\n4. Testing results endpoint with authentication...")
                headers = {'Authorization': f'Bearer {token}'}
                response = requests.get(f'{base_url}/api/results?semester=3', headers=headers)
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   ✅ Results endpoint working!")
                    print(f"   Found {data.get('total_sessional_exams', 0)} sessional exams")
                else:
                    print(f"   ❌ Results endpoint failed: {response.text}")
            else:
                print("   ❌ Login response missing token")
        else:
            print("   ❌ Login failed")
    except Exception as e:
        print(f"   ❌ Error testing login: {e}")
    
    print("\n🎉 Web interface testing completed!")
    print("\n📱 You can now access the web interface at:")
    print("   🌐 http://localhost:5000")
    print("   🌐 http://localhost:5000/dashboard")

if __name__ == "__main__":
    test_web_interface()