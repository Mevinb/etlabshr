#!/usr/bin/env python3
"""
Direct test of terminal timetable functionality
"""

import json
from app import create_app
from terminal_login_direct import ETLabTerminalDirect

def test_terminal_timetable():
    """Test the terminal timetable method directly"""
    print("🧪 Direct Terminal Timetable Test")
    print("=" * 35)
    
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
            
            # Test the timetable method
            print("\n2. Testing timetable method...")
            
            try:
                terminal.get_timetable()
                print("\n✅ Timetable method test completed!")
            except Exception as e:
                print(f"❌ Error in timetable method: {e}")
        else:
            print("❌ Failed to get token")

if __name__ == "__main__":
    test_terminal_timetable()