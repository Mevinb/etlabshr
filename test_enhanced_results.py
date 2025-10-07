#!/usr/bin/env python3
"""
Test the enhanced results functionality with end semester support
"""

import json
from app import create_app

def test_enhanced_results():
    """Test the enhanced results endpoint with end semester support"""
    app = create_app()
    
    with app.test_client() as client:
        print("🧪 Testing Enhanced Results with End Semester Support")
        print("=" * 52)
        
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
        
        # Test enhanced results endpoint
        print("\n2. Testing enhanced results endpoint...")
        headers = {'Authorization': f'Bearer {token}'}
        
        response = client.get('/api/results', headers=headers)
        
        if response.status_code == 200:
            data = response.get_json()
            print("✅ Enhanced results retrieved!")
            
            # Show comprehensive summary
            print(f"\n📊 Enhanced Results Summary:")
            print(f"   📝 Sessional Exams: {data.get('total_sessional_exams', 0)}")
            print(f"   🧪 Module Tests: {data.get('total_module_tests', 0)}")
            print(f"   📋 Class Projects: {data.get('total_class_projects', 0)}")
            print(f"   📄 Assignments: {data.get('total_assignments', 0)}")
            print(f"   📚 Tutorials: {data.get('total_tutorials', 0)}")
            print(f"   🎓 End Semester Exams: {data.get('total_end_semester_exams', 0)}")
            
            # Show end semester examples if available
            end_semester_exams = data.get('end_semester_exams', [])
            if end_semester_exams:
                print(f"\n🎓 End Semester Exam Examples:")
                for i, exam in enumerate(end_semester_exams[:3]):  # Show first 3
                    subject_code = exam.get('subject_code', 'N/A')
                    subject_name = exam.get('subject_name', 'N/A')
                    semester = exam.get('semester', 'N/A')
                    marks = exam.get('marks_obtained', 'N/A')
                    max_marks = exam.get('maximum_marks', 'N/A')
                    print(f"   {i+1}. {subject_code} - {subject_name}")
                    print(f"      Semester: {semester} | Marks: {marks}/{max_marks}")
            else:
                print(f"\n❗ No end semester exams found in current parsing")
            
            # Show debug info
            debug_info = data.get('debug_info', {})
            print(f"\n🔧 Debug Info:")
            print(f"   Sections Found: {debug_info.get('sections_found', [])}")
            
            # Test with specific semester
            print(f"\n3. Testing with semester filter (semester 1)...")
            response = client.get('/api/results?semester=1', headers=headers)
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Semester 1 results: {data.get('total_end_semester_exams', 0)} end semester exams")
            else:
                print(f"❌ Semester filter test failed")
                
        else:
            error_data = response.get_json()
            print(f"❌ Enhanced results failed: {error_data.get('message', 'Unknown error')}")

if __name__ == "__main__":
    test_enhanced_results()