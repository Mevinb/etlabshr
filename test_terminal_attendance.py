#!/usr/bin/env python3
"""
Direct test of terminal attendance functionality
"""

import json
from app import create_app
from terminal_login_direct import ETLabTerminalDirect

def test_terminal_attendance():
    """Test the terminal attendance method directly"""
    print("🧪 Direct Terminal Attendance Test")
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
            
            # Now test the attendance method by simulating user input
            print("\n2. Testing attendance method...")
            
            # Temporarily override input to provide semester
            import builtins
            original_input = builtins.input
            
            def mock_input(prompt):
                print(f"{prompt}1")  # Show the prompt and our response
                return "1"  # Return semester 1
            
            builtins.input = mock_input
            
            try:
                terminal.get_attendance()
                print("\n✅ Attendance method test completed!")
            except Exception as e:
                print(f"❌ Error in attendance method: {e}")
            finally:
                builtins.input = original_input
        else:
            print("❌ Failed to get token")

if __name__ == "__main__":
    test_terminal_attendance()