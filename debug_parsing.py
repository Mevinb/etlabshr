#!/usr/bin/env python3
"""
Debug version to see what data is actually being parsed
"""

import sys
import os
import requests
from bs4 import BeautifulSoup

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config

def login_and_get_session():
    """Login to ETLab and return authenticated session"""
    session = requests.Session()
    
    payload = {
        "LoginForm[username]": "224079",
        "LoginForm[password]": "Midhun@123123",
        "yt0": "",
    }

    headers = {
        "User-Agent": Config.USER_AGENT,
        "Content-Type": "application/x-www-form-urlencoded",
    }

    response = session.post(
        f"{Config.BASE_URL}/user/login", data=payload, headers=headers
    )
    
    cookies = session.cookies.get_dict()
    if Config.COOKIE_KEY in cookies:
        return session
    return None

def debug_results_parsing():
    """Debug what data is actually found"""
    print("🔍 Debug: Checking actual data being parsed...")
    
    session = login_and_get_session()
    if not session:
        print("❌ Login failed")
        return
    
    results_url = f"{Config.BASE_URL}/ktuacademics/student/results"
    response = session.get(results_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Check Sessional exams section
    print("\n📝 DEBUG: Sessional exams section")
    sessional_section = soup.find("h5", string="Sessional exams")
    if sessional_section:
        print("  ✅ Found section header")
        sessional_table = sessional_section.find_next("table")
        if sessional_table:
            print("  ✅ Found table")
            rows = sessional_table.find_all("tr")[1:]  # Skip header row
            print(f"  📋 Found {len(rows)} data rows")
            
            for i, row in enumerate(rows):
                cells = row.find_all("td")
                print(f"    Row {i+1}: {len(cells)} cells")
                if len(cells) >= 2:
                    subject = cells[0].text.strip()
                    semester = cells[1].text.strip()
                    print(f"      Subject: '{subject}'")
                    print(f"      Semester: '{semester}'")
                    
                    # Test semester matching
                    if "III" in semester or "3" in semester:
                        print(f"      ✅ MATCHES semester 3!")
                    else:
                        print(f"      ❌ Does not match semester 3")
                        
                if len(cells) >= 5:
                    exam = cells[2].text.strip()
                    max_marks = cells[3].text.strip()
                    marks_obtained = cells[4].text.strip()
                    print(f"      Exam: '{exam}', Max: '{max_marks}', Obtained: '{marks_obtained}'")
                print()
        else:
            print("  ❌ No table found")
    else:
        print("  ❌ Section header not found")
    
    # Check what sections actually exist
    print("\n🔍 DEBUG: All H5 sections found:")
    h5_sections = soup.find_all("h5")
    for section in h5_sections:
        text = section.get_text(strip=True)
        print(f"  • '{text}'")

if __name__ == "__main__":
    debug_results_parsing()