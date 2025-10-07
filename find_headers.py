#!/usr/bin/env python3
"""
Find the exact text of all h5 headers and their surrounding content
"""

import requests
import json
from bs4 import BeautifulSoup
from app import create_app

def find_exact_headers():
    """Find exactly what h5 headers exist and their exact text"""
    
    app = create_app()
    
    with app.test_client() as client:
        # Login
        login_data = {
            "username": "224789",
            "password": "mevinbenty12+"
        }
        
        response = client.post('/api/login', 
                             data=json.dumps(login_data),
                             content_type='application/json')
        
        data = response.get_json()
        token = data.get('token')
        print(f"✅ Login successful! Token: {token[:20]}...")
        
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
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        print("🔍 Analyzing all H5 headers:")
        h5_headers = soup.find_all("h5")
        
        for i, header in enumerate(h5_headers):
            text = header.get_text()
            text_stripped = text.strip()
            print(f"\nHeader {i+1}:")
            print(f"  Raw text: '{text}'")
            print(f"  Stripped: '{text_stripped}'")
            print(f"  Length: {len(text)} -> {len(text_stripped)}")
            print(f"  Bytes: {text.encode()}")
            
            # Try different search methods
            print(f"  Tests:")
            print(f"    Exact match 'Sessional exams': {header.string == 'Sessional exams'}")
            print(f"    Contains 'Sessional': {'Sessional' in text}")
            print(f"    Contains 'sessional': {'sessional' in text.lower()}")
            
            # Check if there's a table after this header
            next_table = header.find_next("table")
            if next_table:
                rows = next_table.find_all("tr")
                print(f"    Next table: {len(rows)} rows")
                if len(rows) > 1:
                    first_data_row = rows[1].find_all("td")
                    if first_data_row:
                        print(f"    First row data: {[cell.get_text().strip() for cell in first_data_row[:3]]}")
            else:
                print(f"    Next table: None")
        
        # Try alternative search methods
        print(f"\n🔍 Alternative search methods:")
        
        # Search by partial text
        headers_with_sessional = soup.find_all("h5", string=lambda text: text and "sessional" in text.lower())
        print(f"  Headers containing 'sessional': {len(headers_with_sessional)}")
        for header in headers_with_sessional:
            print(f"    - '{header.get_text()}'")
        
        # Search all elements containing "sessional"
        all_sessional = soup.find_all(text=lambda text: text and "sessional" in text.lower())
        print(f"  All elements containing 'sessional': {len(all_sessional)}")
        for text in all_sessional[:5]:  # First 5
            print(f"    - '{text.strip()}'")

if __name__ == "__main__":
    print("🎓 ETLab Header Analysis")
    print("=" * 50)
    find_exact_headers()