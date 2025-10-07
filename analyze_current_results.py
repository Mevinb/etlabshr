#!/usr/bin/env python3
"""
Analyze current results page HTML to find end semester data
"""

import json
import requests
from bs4 import BeautifulSoup
from app import create_app

def analyze_current_results():
    """Analyze current results page for end semester data"""
    app = create_app()
    
    with app.test_client() as client:
        print("🔍 Analyzing Current Results Page")
        print("=" * 33)
        
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
        
        # Get the current results page (same URL as the working route)
        print("\n📊 Fetching current results page...")
        
        try:
            response = requests.get(
                f"{Config.BASE_URL}/ktuacademics/student/results",
                headers=headers,
                cookies=cookie,
                timeout=10
            )
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                print("✅ Results page loaded successfully!")
                
                # Save the full HTML
                with open("current_results_full.html", "w", encoding="utf-8") as f:
                    f.write(response.text)
                print("💾 Full HTML saved to current_results_full.html")
                
                # Look for all h5 headers (section headers)
                print("\n📋 All H5 Section Headers:")
                h5_headers = soup.find_all("h5")
                for i, h5 in enumerate(h5_headers):
                    text = h5.text.strip()
                    print(f"   {i+1}. {text}")
                
                # Look for any text containing "end semester" or similar patterns
                print("\n🔍 Searching for semester examination patterns...")
                
                patterns = [
                    "end semester",
                    "semester examination", 
                    "regular.*semester",
                    "december.*2024",
                    "may.*2025",
                    "november.*2025",
                    "b.tech.*semester",
                    "semester.*exam"
                ]
                
                for pattern in patterns:
                    elements = soup.find_all(string=lambda text: text and pattern.lower().replace('.*', ' ') in text.lower())
                    if elements:
                        print(f"   📋 Pattern '{pattern}': {len(elements)} matches")
                        for j, elem in enumerate(elements[:2]):  # Show first 2
                            clean_text = ' '.join(elem.strip().split())
                            print(f"      {j+1}. {clean_text[:100]}...")
                
                # Look for all table structures
                print(f"\n📊 Found {len(soup.find_all('table'))} tables on the page")
                
                # Look for any links or buttons
                all_links = soup.find_all("a")
                result_links = [link for link in all_links if "result" in link.text.lower()]
                print(f"🔗 Found {len(result_links)} result-related links:")
                for i, link in enumerate(result_links[:5]):
                    href = link.get('href', 'No href')
                    text = link.text.strip()
                    print(f"   {i+1}. {text} -> {href}")
                
            else:
                print(f"❌ HTTP Error: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    analyze_current_results()