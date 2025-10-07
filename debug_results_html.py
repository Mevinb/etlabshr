#!/usr/bin/env python3
"""
Debug the results HTML structure
"""

import requests
import json
from bs4 import BeautifulSoup
from app import create_app

def debug_results_html():
    """Debug what the results HTML actually looks like"""
    
    app = create_app()
    
    with app.test_client() as client:
        # First login
        print("🔍 Logging in...")
        login_data = {
            "username": "224789",
            "password": "mevinbenty12+"
        }
        
        response = client.post('/api/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        if response.status_code != 200:
            print("❌ Login failed")
            return
            
        data = response.get_json()
        token = data.get('token')
        print(f"✅ Login successful! Token: {token[:20]}...")
        
        # Now get results with debugging
        print("\n🔍 Fetching results HTML...")
        headers = {'Authorization': f'Bearer {token}'}
        
        # Let's also make the direct request to see the raw HTML
        from config import Config
        
        cookie = {Config.COOKIE_KEY: token}
        headers_direct = {
            "User-Agent": Config.USER_AGENT,
        }
        
        response = requests.get(
            f"{Config.BASE_URL}/ktuacademics/student/results",
            headers=headers_direct,
            cookies=cookie,
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Save the full HTML for inspection
            with open("debug_results.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("💾 Saved full HTML to debug_results.html")
            
            # Look for all h5 headers
            print("\n📝 Found H5 headers:")
            h5_headers = soup.find_all("h5")
            for i, header in enumerate(h5_headers):
                print(f"  {i+1}. '{header.get_text().strip()}'")
            
            # Look for all tables
            print("\n📊 Found tables:")
            tables = soup.find_all("table")
            for i, table in enumerate(tables):
                rows = table.find_all("tr")
                print(f"  Table {i+1}: {len(rows)} rows")
                if len(rows) > 0:
                    header_row = rows[0]
                    headers = [th.get_text().strip() for th in header_row.find_all(["th", "td"])]
                    print(f"    Headers: {headers}")
                    
                    # Show first data row if exists
                    if len(rows) > 1:
                        first_data_row = rows[1]
                        data_cells = [td.get_text().strip() for td in first_data_row.find_all("td")]
                        print(f"    First row: {data_cells}")
            
            # Look for specific patterns
            print("\n🔍 Looking for exam result patterns...")
            
            # Check for any text containing "exam", "test", "result", "marks"
            all_text = soup.get_text().lower()
            keywords = ["sessional", "module", "project", "exam", "test", "marks", "result"]
            
            for keyword in keywords:
                if keyword in all_text:
                    print(f"  ✅ Found keyword: '{keyword}'")
                    # Find elements containing this keyword
                    elements = soup.find_all(text=lambda text: text and keyword in text.lower())
                    for element in elements[:3]:  # Show first 3 matches
                        print(f"    - '{element.strip()}'")
                else:
                    print(f"  ❌ Keyword not found: '{keyword}'")
                    
        else:
            print(f"❌ Failed to fetch results: {response.status_code}")
            print(f"Response: {response.text[:500]}...")

if __name__ == "__main__":
    print("🎓 ETLab Results HTML Debug")
    print("=" * 50)
    debug_results_html()