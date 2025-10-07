#!/usr/bin/env python3
"""
Debug script to analyze end semester results page structure - simplified
"""

import json
import requests
from bs4 import BeautifulSoup
from app import create_app

def debug_end_semester_simple():
    """Debug the end semester results page structure"""
    app = create_app()
    
    with app.test_client() as client:
        print("🔍 Debugging End Semester Results (Simple)")
        print("=" * 40)
        
        # Login first
        print("1. Logging in...")
        login_data = {
            "username": "224789",
            "password": "mevinbenty12+"
        }
        
        response = client.post('/api/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        if response.status_code != 200:
            print(f"❌ Login failed: {response.get_json()}")
            return
            
        data = response.get_json()
        token = data['token']
        print("✅ Login successful!")
        
        # Import config for proper headers
        from config import Config
        
        headers = {
            "User-Agent": Config.USER_AGENT,
        }
        cookie = {Config.COOKIE_KEY: token}
        
        # Try the main results page
        print("\n2. Checking main results page...")
        response = requests.get(
            f"{Config.BASE_URL}/ktuacademics/student/results",
            headers=headers,
            cookies=cookie,
        )
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            print(f"✅ Status: {response.status_code}")
            
            # Look for any buttons or links with "View Result"
            view_buttons = soup.find_all("a", string=lambda text: text and "view result" in text.lower())
            if not view_buttons:
                view_buttons = soup.find_all("button", string=lambda text: text and "view result" in text.lower())
            if not view_buttons:
                # Look for any element containing "view result"
                view_buttons = soup.find_all(string=lambda text: text and "view result" in text.lower())
                view_buttons = [elem.parent for elem in view_buttons if elem.parent]
            
            print(f"🔍 Found {len(view_buttons)} 'View Result' elements")
            
            for i, button in enumerate(view_buttons[:3]):
                href = button.get('href', 'No href') if hasattr(button, 'get') else 'No href'
                onclick = button.get('onclick', 'No onclick') if hasattr(button, 'get') else 'No onclick'
                text = button.text.strip() if hasattr(button, 'text') else str(button)[:50]
                print(f"   {i+1}. Text: {text}")
                print(f"       Href: {href}")
                print(f"       Onclick: {onclick}")
                print()
            
            # Save HTML for manual inspection
            with open("debug_simple_results.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"💾 HTML saved to debug_simple_results.html")
            
        else:
            print(f"❌ Failed to get results page: {response.status_code}")

if __name__ == "__main__":
    debug_end_semester_simple()