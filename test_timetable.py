#!/usr/bin/env python3
"""
Test script for timetable functionality
"""

import json
from app import create_app

def test_timetable():
    """Test the timetable endpoint directly"""
    app = create_app()
    
    with app.test_client() as client:
        print("🧪 Testing Timetable Feature")
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
        
        # Test timetable
        print("2. Testing timetable...")
        headers = {'Authorization': f'Bearer {token}'}
        
        response = client.get('/api/timetable', headers=headers)
        
        if response.status_code == 200:
            data = response.get_json()
            print("✅ Timetable retrieved successfully!")
            
            # Show timetable structure
            print(f"\n📅 Timetable Data:")
            for day, periods in data.items():
                print(f"   📅 {day.upper()}:")
                period_count = 0
                for period_name, period_data in periods.items():
                    if period_data.get('name') and period_data['name'].strip():
                        period_count += 1
                        name = period_data.get('name', 'N/A')
                        teacher = period_data.get('teacher', '')
                        if teacher:
                            print(f"      🕐 {period_name}: {name} - {teacher}")
                        else:
                            print(f"      🕐 {period_name}: {name}")
                
                if period_count == 0:
                    print(f"      ℹ️ No classes scheduled")
                print()
            
        else:
            error_data = response.get_json()
            print(f"❌ Timetable failed: {error_data.get('message', 'Unknown error')}")

if __name__ == "__main__":
    test_timetable()