import requests
import json

def test_login():
    """Test the login functionality of the etlab API"""
    
    # API endpoint
    base_url = "http://localhost:5000"
    login_url = f"{base_url}/api/login"
    
    print("=" * 50)
    print("ETLAB API Login Test")
    print("=" * 50)
    
    # Get credentials from user input
    print("\nEnter your etlab credentials:")
    username = input("Username: ")
    password = input("Password: ")
    
    # Prepare the request
    payload = {
        "username": username,
        "password": password
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print(f"\nTesting login at: {login_url}")
    print("Sending request...")
    
    try:
        # Send the login request
        response = requests.post(login_url, json=payload, headers=headers, timeout=30)
        
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        # Parse the response
        try:
            response_data = response.json()
            print(f"Response Body: {json.dumps(response_data, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response Body (raw): {response.text}")
        
        # Check if login was successful
        if response.status_code == 200:
            print("\n✅ LOGIN SUCCESSFUL!")
            if 'token' in response_data:
                token = response_data['token']
                print(f"🔑 Auth Token: {token}")
                
                # Test if we can use the token for another endpoint
                print("\n" + "=" * 30)
                print("Testing token with profile endpoint...")
                test_profile_with_token(base_url, token)
            else:
                print("⚠️  No token found in response")
        
        elif response.status_code == 401:
            print("\n❌ LOGIN FAILED!")
            print("Invalid username or password")
        
        else:
            print(f"\n❌ UNEXPECTED ERROR!")
            print(f"Status code: {response.status_code}")
    
    except requests.exceptions.ConnectionError:
        print("\n❌ CONNECTION ERROR!")
        print("Could not connect to the API. Make sure the server is running on localhost:5000")
    
    except requests.exceptions.Timeout:
        print("\n❌ TIMEOUT ERROR!")
        print("Request timed out. The server might be slow or unresponsive.")
    
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR!")
        print(f"Error: {str(e)}")

def test_profile_with_token(base_url, token):
    """Test the profile endpoint using the auth token"""
    
    profile_url = f"{base_url}/api/profile"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": token
    }
    
    try:
        response = requests.get(profile_url, headers=headers, timeout=15)
        
        print(f"Profile endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Token is valid! Profile data retrieved successfully.")
            try:
                profile_data = response.json()
                print(f"Profile data: {json.dumps(profile_data, indent=2)}")
            except json.JSONDecodeError:
                print("Profile response (raw):", response.text)
        else:
            print("❌ Token validation failed or profile endpoint error")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"❌ Error testing profile endpoint: {str(e)}")

def quick_test():
    """Quick test with hardcoded credentials (for development only)"""
    print("\n" + "=" * 50)
    print("QUICK TEST MODE")
    print("=" * 50)
    print("⚠️  Using hardcoded credentials - update the script with your actual credentials")
    
    # TODO: Replace with actual test credentials
    test_username = "your_test_username"
    test_password = "your_test_password"
    
    if test_username == "your_test_username":
        print("❌ Please update the test_username and test_password in the script first!")
        return
    
    payload = {
        "username": test_username,
        "password": test_password
    }
    
    try:
        response = requests.post("http://localhost:5000/api/login", json=payload, timeout=30)
        print(f"Quick test result: {response.status_code}")
        if response.status_code == 200:
            print("✅ Quick test passed!")
        else:
            print("❌ Quick test failed!")
            print(response.text)
    except Exception as e:
        print(f"❌ Quick test error: {str(e)}")

if __name__ == "__main__":
    print("Choose test mode:")
    print("1. Interactive login test")
    print("2. Quick test (requires editing script with credentials)")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_login()
    elif choice == "2":
        quick_test()
    else:
        print("Invalid choice. Running interactive test...")
        test_login()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("=" * 50)