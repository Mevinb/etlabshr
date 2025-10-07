#!/usr/bin/env python3
"""
Test exam registration page for end semester results
"""

import json
import requests
from bs4 import BeautifulSoup
from app import create_app

def test_exam_registration():
    """Test the exam registration page"""
    app = create_app()
    
    with app.test_client() as client:
        print("🧪 Testing Exam Registration Page")
        print("=" * 35)
        
        # Login first
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
        
        # Import config
        from config import Config
        
        headers = {
            "User-Agent": Config.USER_AGENT,
        }
        cookie = {Config.COOKIE_KEY: token}
        
        # Test exam registration URL (as seen in breadcrumb)
        print("\n📋 Testing exam registration page...")
        
        try:
            response = requests.get(
                f"{Config.BASE_URL}/student/examregistration",
                headers=headers,
                cookies=cookie,
                timeout=10
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Look for semester examination patterns
                semester_texts = soup.find_all(string=lambda text: text and "semester" in text.lower() and ("examination" in text.lower() or "exam" in text.lower()))
                
                print(f"📚 Found {len(semester_texts)} semester exam references:")
                for i, text in enumerate(semester_texts[:5]):
                    clean_text = ' '.join(text.strip().split())
                    print(f"   {i+1}. {clean_text}")
                
                # Look for View Result buttons/links
                view_elements = soup.find_all("a", string=lambda text: text and "view" in text.lower() and "result" in text.lower())
                if not view_elements:
                    view_elements = soup.find_all("button", string=lambda text: text and "view" in text.lower() and "result" in text.lower())
                
                print(f"\n🔍 Found {len(view_elements)} View Result elements:")
                for i, elem in enumerate(view_elements[:3]):
                    href = elem.get('href', 'No href')
                    onclick = elem.get('onclick', 'No onclick')
                    text = elem.text.strip()
                    print(f"   {i+1}. Text: {text}")
                    if href != 'No href':
                        print(f"       Href: {href}")
                    if onclick != 'No onclick':
                        print(f"       Onclick: {onclick}")
                
                # Save a snippet for analysis
                with open("exam_registration_snippet.html", "w", encoding="utf-8") as f:
                    # Just save first 10000 characters to avoid large files
                    f.write(response.text[:10000])
                print(f"\n💾 Snippet saved to exam_registration_snippet.html")
                
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("⏰ Request timed out")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_exam_registration()