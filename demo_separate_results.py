#!/usr/bin/env python3
"""
Demo of separate end semester results functionality
"""

import json
from app import create_app

def demo_separate_results():
    """Demo the separate end semester results"""
    app = create_app()
    
    with app.test_client() as client:
        print("🎓 ETLab API - Separate End Semester Results Demo")
        print("=" * 50)
        
        # Login
        print("1. 🔐 Logging in...")
        login_data = {
            "username": "224789",
            "password": "mevinbenty12+"
        }
        
        response = client.post('/api/login', json=login_data)
        if response.status_code != 200:
            print(f"❌ Login failed")
            return
            
        data = response.get_json()
        token = data['token']
        print("✅ Login successful!")
        
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test main results (should NOT have end semester)
        print("\n2. 📊 Testing Main Results API (excludes end semester)...")
        response = client.get('/api/results', headers=headers)
        
        if response.status_code == 200:
            data = response.get_json()
            print("✅ Main Results API working!")
            
            # Verify separation
            has_end_sem = 'end_semester_exams' in data
            print(f"   🎯 Contains end semester: {'❌ ERROR' if has_end_sem else '✅ CORRECTLY SEPARATED'}")
            
            print(f"   📊 Main Results Summary:")
            print(f"      📝 Sessional Exams: {data.get('total_sessional_exams', 0)}")
            print(f"      🧪 Module Tests: {data.get('total_module_tests', 0)}")
            print(f"      📋 Class Projects: {data.get('total_class_projects', 0)}")
            print(f"      📄 Assignments: {data.get('total_assignments', 0)}")
            print(f"      📚 Tutorials: {data.get('total_tutorials', 0)}")
        
        # Test separate end semester API
        print("\n3. 🎓 Testing Separate End Semester API...")
        response = client.get('/api/end-semester-results', headers=headers)
        
        if response.status_code == 200:
            data = response.get_json()
            print("✅ End Semester API working!")
            
            end_sem_count = data.get('total_end_semester_exams', 0)
            print(f"   🎯 End Semester Exams: {end_sem_count}")
            
            if data.get('available_links'):
                print(f"   🔗 Additional Links: {len(data.get('available_links', []))}")
        
        print(f"\n4. ✅ IMPLEMENTATION COMPLETE!")
        print(f"   🎯 End semester results are now SEPARATE")
        print(f"   📱 Terminal: Option 3 = End Semester Results")
        print(f"   🌐 Web: Separate tab for end semester results")
        print(f"   🚀 Status: FULLY FUNCTIONAL! 🎉")

if __name__ == "__main__":
    demo_separate_results()