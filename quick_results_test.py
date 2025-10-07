#!/usr/bin/env python3
"""
Quick test to check current results endpoint and see what's available
"""

import json
from app import create_app

def quick_results_test():
    """Test current results endpoint"""
    app = create_app()
    
    with app.test_client() as client:
        print("🧪 Quick Results Test")
        print("=" * 20)
        
        # Login
        print("1. Logging in...")
        login_data = {
            "username": "224789",
            "password": "mevinbenty12+"
        }
        
        response = client.post('/api/login', json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed: {response.get_json()}")
            return
            
        data = response.get_json()
        token = data['token']
        print("✅ Login successful!")
        
        # Test current results endpoint
        print("\n2. Testing current results endpoint...")
        headers = {'Authorization': f'Bearer {token}'}
        
        response = client.get('/api/results', headers=headers)
        
        if response.status_code == 200:
            data = response.get_json()
            print("✅ Results retrieved!")
            
            # Show summary
            print(f"\n📊 Current Results Summary:")
            print(f"   📝 Sessional Exams: {len(data.get('sessional_exams', []))}")
            print(f"   🧪 Module Tests: {len(data.get('module_tests', []))}")
            print(f"   📋 Class Projects: {len(data.get('class_projects', []))}")
            print(f"   📄 Assignments: {len(data.get('assignments', []))}")
            print(f"   📚 Tutorials: {len(data.get('tutorials', []))}")
            
            # Show one example from each category if available
            if data.get('sessional_exams'):
                example = data['sessional_exams'][0]
                print(f"\n   📝 Sessional Example: {example.get('subject_code', 'N/A')} - {example.get('marks_obtained', 'N/A')}/{example.get('maximum_marks', 'N/A')}")
                
        else:
            error_data = response.get_json()
            print(f"❌ Results failed: {error_data.get('message', 'Unknown error')}")

if __name__ == "__main__":
    quick_results_test()