#!/usr/bin/env python3
"""
Debug the profile page to see all available information
"""

import requests
import json
from bs4 import BeautifulSoup
from app import create_app

def debug_profile_data():
    """Debug what profile information is available"""
    
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
        
        # Now get profile page
        print("\n🔍 Fetching profile page...")
        
        from config import Config
        
        cookie = {Config.COOKIE_KEY: token}
        headers_direct = {
            "User-Agent": Config.USER_AGENT,
        }
        
        response = requests.get(
            f"{Config.BASE_URL}/student/profile",
            headers=headers_direct,
            cookies=cookie,
        )
        
        print(f"📊 Response Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Save the full HTML for inspection
            with open("debug_profile.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print("💾 Saved full HTML to debug_profile.html")
            
            # Look for all tables
            print("\n📊 Profile Tables Analysis:")
            tables = soup.find_all("table")
            
            all_profile_data = {}
            
            for i, table in enumerate(tables):
                print(f"\nTable {i+1}:")
                rows = table.find_all("tr")
                print(f"  Rows: {len(rows)}")
                
                table_data = {}
                
                for j, row in enumerate(rows):
                    cells = row.find_all(["th", "td"])
                    if len(cells) == 2:  # Key-value pair
                        key = cells[0].get_text().strip()
                        value = cells[1].get_text().strip()
                        
                        if key and value:  # Both have content
                            table_data[key] = value
                            print(f"    {key}: {value}")
                    elif len(cells) > 2:
                        # Multi-column table
                        row_data = [cell.get_text().strip() for cell in cells]
                        print(f"    Row {j}: {row_data}")
                
                if table_data:
                    all_profile_data[f"table_{i+1}"] = table_data
            
            # Look for any divs or other elements with profile data
            print("\n📝 Other Profile Elements:")
            
            # Look for any text that might contain profile information
            profile_keywords = [
                "student", "name", "admission", "university", "college", "course", 
                "branch", "batch", "semester", "year", "phone", "email", "address",
                "parent", "guardian", "father", "mother", "blood", "category",
                "scholarship", "hostel", "library", "id", "roll", "registration"
            ]
            
            additional_data = {}
            
            for keyword in profile_keywords:
                # Find elements containing this keyword
                elements = soup.find_all(text=lambda text: text and keyword in text.lower())
                if elements:
                    print(f"\n  Elements containing '{keyword}':")
                    for element in elements[:5]:  # Show first 5 matches
                        parent = element.parent
                        if parent and parent.name in ['th', 'td', 'p', 'div', 'span']:
                            context = parent.get_text().strip()
                            if len(context) < 200 and context:  # Reasonable length
                                print(f"    - {context}")
            
            # Look for specific patterns
            print("\n🔍 Looking for structured data patterns...")
            
            # Find all th-td pairs across the entire page
            all_th_elements = soup.find_all("th")
            print(f"\nFound {len(all_th_elements)} TH elements (potential field labels):")
            
            comprehensive_profile = {}
            
            for th in all_th_elements:
                label = th.get_text().strip()
                if label:
                    # Try to find the corresponding value
                    next_td = th.find_next("td")
                    if next_td:
                        value = next_td.get_text().strip()
                        if value and len(value) < 500:  # Reasonable length
                            comprehensive_profile[label] = value
                            print(f"  {label}: {value}")
            
            # Save comprehensive profile data
            with open("comprehensive_profile.json", "w", encoding="utf-8") as f:
                json.dump(comprehensive_profile, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Saved comprehensive profile data to comprehensive_profile.json")
            
            print(f"\n📊 SUMMARY:")
            print(f"  Total field-value pairs found: {len(comprehensive_profile)}")
            print(f"  Tables analyzed: {len(tables)}")
            
        else:
            print(f"❌ Failed to fetch profile: {response.status_code}")
            print(f"Response: {response.text[:500]}...")

if __name__ == "__main__":
    print("🎓 ETLab Profile Debug")
    print("=" * 50)
    debug_profile_data()