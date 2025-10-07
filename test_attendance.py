#!/usr/bin/env python3
"""
Test script for attendance functionality
"""

import json
from app import create_app

def test_attendance():
    """Test the attendance endpoint directly"""
    app = create_app()
    
    # Test login first
    with app.test_client() as client:
        print("🧪 Testing Attendance Feature")
        print("=" * 30)
        
        # Login
        print("1. Testing login...")
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
        
        # Test attendance
        print("2. Testing attendance...")
        headers = {'Authorization': f'Bearer {token}'}
        
        # Test different semesters
        for semester in [1, 2, 3, 4]:
            print(f"\n📅 Testing semester {semester}:")
            response = client.get(f'/api/attendance?semester={semester}', headers=headers)
            
            if response.status_code == 200:
                data = response.get_json()
                print(f"✅ Semester {semester} attendance retrieved!")
                
                # Show basic info
                print(f"   👤 Name: {data.get('name', 'N/A')}")
                print(f"   📋 Reg No: {data.get('university_reg_no', 'N/A')}")
                print(f"   🎯 Roll No: {data.get('roll_no', 'N/A')}")
                
                # Count subjects
                subject_count = 0
                for key, value in data.items():
                    if isinstance(value, dict) and 'present_hours' in value:
                        subject_count += 1
                        
                print(f"   📚 Subjects: {subject_count}")
                print(f"   📊 Overall: {data.get('total_perecentage', 'N/A')}")
                
                if subject_count > 0:
                    print(f"   📖 Sample subject attendance:")
                    for key, value in data.items():
                        if isinstance(value, dict) and 'present_hours' in value:
                            print(f"      {key}: {value.get('attendance_percentage', 'N/A')}")
                            break
            else:
                error_data = response.get_json()
                print(f"❌ Semester {semester} failed: {error_data.get('message', 'Unknown error')}")

if __name__ == "__main__":
    test_attendance()