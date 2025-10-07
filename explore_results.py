#!/usr/bin/env python3
"""
Explore the actual ETLab results page structure
"""

import sys
import os
import requests
from bs4 import BeautifulSoup

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config

def login():
    """Login and return session"""
    print("Logging in...")
    
    username = "224079"
    password = "Midhun@123123"
    
    session = requests.Session()
    
    payload = {
        "LoginForm[username]": username,
        "LoginForm[password]": password,
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
        print("✅ Login successful")
        return session
    else:
        print("❌ Login failed")
        return None

def explore_results_page(session):
    """Explore the actual structure of the results page"""
    print("\nExploring results page structure...")
    
    results_url = f"{Config.BASE_URL}/ktuacademics/student/results"
    response = session.get(results_url)
    
    if response.status_code != 200:
        print(f"❌ Failed to access results page: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Save the full HTML for inspection
    with open('results_page.html', 'w', encoding='utf-8') as f:
        f.write(response.text)
    print("💾 Saved full HTML to 'results_page.html'")
    
    # Look for headers (h1, h2, h3, h4, h5, h6)
    print("\n📄 Headers found on the page:")
    for i in range(1, 7):
        headers = soup.find_all(f'h{i}')
        if headers:
            print(f"  H{i} tags:")
            for header in headers:
                text = header.get_text(strip=True)
                if text:
                    print(f"    - {text}")
    
    # Look for tables
    print("\n📊 Tables found on the page:")
    tables = soup.find_all('table')
    print(f"  Found {len(tables)} table(s)")
    
    for i, table in enumerate(tables):
        print(f"\n  Table {i+1}:")
        
        # Look for table headers
        headers = table.find_all('th')
        if headers:
            header_texts = [th.get_text(strip=True) for th in headers]
            print(f"    Headers: {header_texts}")
        
        # Show first few rows
        rows = table.find_all('tr')
        print(f"    Total rows: {len(rows)}")
        
        if len(rows) > 1:  # Show first data row
            first_data_row = rows[1]
            cells = first_data_row.find_all(['td', 'th'])
            cell_texts = [cell.get_text(strip=True) for cell in cells]
            print(f"    Sample row: {cell_texts}")
    
    # Look for divs with class or id that might contain results
    print("\n📦 Divs with classes/IDs that might contain results:")
    result_divs = soup.find_all('div', {'class': True})
    interesting_classes = []
    for div in result_divs:
        classes = div.get('class', [])
        for cls in classes:
            if any(keyword in cls.lower() for keyword in ['result', 'exam', 'grade', 'mark', 'score']):
                if cls not in interesting_classes:
                    interesting_classes.append(cls)
    
    if interesting_classes:
        print(f"  Interesting classes: {interesting_classes}")
    else:
        print("  No result-related classes found")
    
    # Look for any text containing "semester", "result", "exam", "marks"
    print("\n🔍 Text containing keywords:")
    keywords = ['semester', 'result', 'exam', 'marks', 'grade']
    for keyword in keywords:
        elements = soup.find_all(text=lambda text: text and keyword.lower() in text.lower())
        if elements:
            print(f"  '{keyword}' found in:")
            for elem in elements[:5]:  # Show first 5 matches
                text = elem.strip()
                if text and len(text) < 100:
                    print(f"    - {text}")
            if len(elements) > 5:
                print(f"    ... and {len(elements)-5} more matches")

def main():
    session = login()
    if session:
        explore_results_page(session)
    else:
        print("Cannot explore - login failed")

if __name__ == "__main__":
    main()