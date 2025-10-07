#!/usr/bin/env python3
"""
Demo script showing the attendance feature in terminal interface
"""

from terminal_login_direct import ETLabTerminalDirect

def demo_attendance():
    """Demo the attendance feature"""
    print("🎓 ETLab Terminal Interface - Attendance Demo")
    print("=" * 50)
    
    # Create terminal interface
    terminal = ETLabTerminalDirect()
    
    # Login with credentials
    print("1. Logging in...")
    terminal.username = "224789"
    terminal.password = "mevinbenty12+"
    
    # Perform login
    if terminal.login():
        print("✅ Login successful!")
        
        # Test attendance for semester 1
        print("\n2. Getting attendance for semester 1...")
        
        # Simulate user input for semester 1
        import io
        import sys
        
        # Temporarily redirect stdin to simulate user input
        old_stdin = sys.stdin
        sys.stdin = io.StringIO("1\n")
        
        try:
            terminal.get_attendance()
        finally:
            sys.stdin = old_stdin
            
        print("\n✅ Attendance demo completed!")
    else:
        print("❌ Login failed")

if __name__ == "__main__":
    demo_attendance()