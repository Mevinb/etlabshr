#!/usr/bin/env python3
"""
Explore different URLs to find end semester results
"""

import json
import requests
from bs4 import BeautifulSoup
from app import create_app

def explore_urls():
    """Explore different URLs to find end semester results"""
    app = create_app()
    
    with app.test_client() as client:
        print("🧪 Exploring URLs for End Semester Results")
        print("=" * 42)
        
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
        
        # List of URLs to try
        urls_to_try = [
            "/student/results",
            "/student/examresults", 
            "/student/exam-results",
            "/student/semesterresults",
            "/student/semester-results",
            "/student/examregistration",
            "/student/exam-registration",
            "/examregistration",
            "/exam-registration",
            "/results",
            "/ktuacademics/student/examresults",
            "/ktuacademics/student/semester-results",
            "/ktuacademics/examregistration"
        ]
        
        print(f"\n🔍 Testing {len(urls_to_try)} URL patterns...")
        
        for i, url_path in enumerate(urls_to_try):
            full_url = f"{Config.BASE_URL}{url_path}"
            try:
                response = requests.get(
                    full_url,
                    headers=headers,
                    cookies=cookie,
                    timeout=5
                )
                
                status = response.status_code
                print(f"   {i+1:2d}. {url_path:<35} -> {status}")
                
                if status == 200:
                    # Quick check for semester exam content
                    soup = BeautifulSoup(response.text, "html.parser")
                    semester_mentions = len(soup.find_all(string=lambda text: text and "semester" in text.lower() and "exam" in text.lower()))
                    view_result_mentions = len(soup.find_all(string=lambda text: text and "view result" in text.lower()))
                    
                    if semester_mentions > 0 or view_result_mentions > 0:
                        print(f"       ✅ Found {semester_mentions} semester exam mentions, {view_result_mentions} 'view result' mentions")
                        
                        # Save this promising page
                        filename = f"promising_page_{i+1}.html"
                        with open(filename, "w", encoding="utf-8") as f:
                            f.write(response.text[:20000])  # First 20k chars
                        print(f"       💾 Saved to {filename}")
                
            except requests.exceptions.Timeout:
                print(f"   {i+1:2d}. {url_path:<35} -> TIMEOUT")
            except Exception as e:
                print(f"   {i+1:2d}. {url_path:<35} -> ERROR: {str(e)[:30]}")

if __name__ == "__main__":
    explore_urls()