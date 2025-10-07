import requests

print("Testing login endpoint...")
try:
    r = requests.post('http://localhost:5000/api/login', json={
        'username': '224079', 
        'password': 'Midhun@123123'
    })
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:500]}")
except Exception as e:
    print(f"Error: {e}")