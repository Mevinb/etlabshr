#!/usr/bin/env python3
"""
Test separate end semester results functionality
"""

import json
from app import create_app
from terminal_login_direct import ETLabTerminalDirect

def test_separate_end_semester():
    """Test the separate end semester results functionality"""
    print("🧪 Testing Separate End Semester Results")
    print("=" * 40)
    
    # Create terminal instance
    terminal = ETLabTerminalDirect()
    
    # Manually set up the token by logging in through the app
    with terminal.app.test_client() as client:
        print("1. Getting token...")
        login_data = {
            "username": "224789",
            "password": "mevinbenty12+"
        }
        
        response = client.post('/api/login', json=login_data)
        if response.status_code == 200:
            data = response.get_json()
            terminal.token = data['token']
            print("✅ Token obtained!")
            
            # Test the separate end semester API endpoint
            print("\n2. Testing separate end semester API endpoint...")
            headers = {'Authorization': f'Bearer {terminal.token}'}
            
            response = client.get('/api/end-semester-results', headers=headers)
            
            if response.status_code == 200:
                data = response.get_json()
                print("✅ End semester API endpoint working!")
                
                end_semester_count = data.get('total_end_semester_exams', 0)
                print(f"   📊 Found {end_semester_count} end semester exams")
                
                if data.get('available_links'):
                    print(f"   🔗 Found {len(data.get('available_links', []))} additional links")
                
            else:
                print(f"❌ End semester API failed: {response.status_code}")
            
            # Test the main results API (should NOT have end semester results)
            print("\n3. Testing main results API (should exclude end semester)...")
            
            response = client.get('/api/results', headers=headers)
            
            if response.status_code == 200:
                data = response.get_json()
                print("✅ Main results API working!")
                
                # Check that end semester results are NOT in main results
                if 'end_semester_exams' in data:
                    print(f"❌ ERROR: Main results still contains end_semester_exams!")
                else:
                    print("✅ Confirmed: Main results no longer contains end semester exams")
                
                print(f"   📊 Main results summary:")
                print(f"      📝 Sessional Exams: {data.get('total_sessional_exams', 0)}")
                print(f"      🧪 Module Tests: {data.get('total_module_tests', 0)}")
                print(f"      📋 Class Projects: {data.get('total_class_projects', 0)}")
                print(f"      📄 Assignments: {data.get('total_assignments', 0)}")
                print(f"      📚 Tutorials: {data.get('total_tutorials', 0)}")
                
            else:
                print(f"❌ Main results API failed: {response.status_code}")
            
            # Test terminal interface method
            print("\n4. Testing terminal interface for end semester results...")
            
            # Temporarily override input
            import builtins
            original_input = builtins.input
            
            def mock_input(prompt):
                print(f"{prompt}")  # Show the prompt
                return ""  # Return empty string for "all results"
            
            builtins.input = mock_input
            
            try:
                terminal.get_end_semester_results()
                print("\n✅ Terminal end semester method test completed!")
            except Exception as e:
                print(f"❌ Error in terminal end semester method: {e}")
            finally:
                builtins.input = original_input
        else:
            print("❌ Failed to get token")

if __name__ == "__main__":
    test_separate_end_semester()