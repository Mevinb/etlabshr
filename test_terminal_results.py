#!/usr/bin/env python3
"""
Test terminal interface with enhanced results display
"""

import json
from app import create_app
from terminal_login_direct import ETLabTerminalDirect

def test_terminal_results():
    """Test the terminal results display"""
    print("🧪 Testing Terminal Results Display")
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
            
            # Test the enhanced results method by simulating user input
            print("\n2. Testing enhanced results display...")
            
            # Temporarily override input to provide no specific semester (show all)
            import builtins
            original_input = builtins.input
            
            def mock_input(prompt):
                print(f"{prompt}")  # Show the prompt
                return ""  # Return empty string for "all results"
            
            builtins.input = mock_input
            
            try:
                terminal.get_results()
                print("\n✅ Enhanced results display test completed!")
            except Exception as e:
                print(f"❌ Error in results display: {e}")
            finally:
                builtins.input = original_input
        else:
            print("❌ Failed to get token")

if __name__ == "__main__":
    test_terminal_results()