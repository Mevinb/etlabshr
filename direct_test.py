#!/usr/bin/env python3
"""
Direct test of the results functionality without Flask server.
This will test the actual logic by calling the functions directly.
"""

import sys
import os
import requests
from bs4 import BeautifulSoup

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config

def test_login_functionality():
    """Test login functionality directly"""
    print("=== Testing Login Functionality ===")
    
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

    try:
        print("1. Making login request to ETLab...")
        response = session.post(
            f"{Config.BASE_URL}/user/login", data=payload, headers=headers
        )
        print(f"   Login response status: {response.status_code}")
        
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("title")
        
        if title:
            print(f"   Page title: {title.text}")
            if "login" in title.text.lower():
                print("   ❌ Still on login page - credentials may be invalid")
                return None
        else:
            print("   ⚠️  No title found")
        
        cookies = session.cookies.get_dict()
        print(f"   Available cookies: {list(cookies.keys())}")
        
        if Config.COOKIE_KEY in cookies:
            token = cookies[Config.COOKIE_KEY]
            print(f"   ✅ Login successful! Token: {token[:20]}...")
            return session, token
        else:
            print(f"   ❌ Cookie {Config.COOKIE_KEY} not found")
            return None
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return None

def find_semester_results(soup, semester):
    """Extract semester results - imported logic from results.py"""
    results = []
    
    # Define result types and their corresponding sections
    result_types = [
        ('Sessional Exam Results', 'sessional_exam'),
        ('Module Test Results', 'module_test'),
        ('Class Project Results', 'class_project')
    ]
    
    for section_title, result_type in result_types:
        # Find the section header
        section_header = soup.find('h5', string=section_title)
        if not section_header:
            continue
        
        # Find the table following this header
        table = section_header.find_next('table')
        if not table:
            continue
        
        # Extract subjects for this semester
        subjects = []
        rows = table.find_all('tr')[1:]  # Skip header row
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 4:  # Ensure we have enough columns
                try:
                    # Extract semester (usually in first or second column)
                    sem_text = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                    
                    # Check if this row is for the requested semester
                    if str(semester) in sem_text or f"S{semester}" in sem_text:
                        subject_data = {
                            'subject_code': cells[0].get_text(strip=True) if len(cells) > 0 else "",
                            'subject_name': cells[2].get_text(strip=True) if len(cells) > 2 else "",
                            'marks': cells[3].get_text(strip=True) if len(cells) > 3 else "",
                            'semester': sem_text
                        }
                        subjects.append(subject_data)
                except Exception as e:
                    continue
        
        if subjects:
            results.append({
                'type': result_type,
                'title': section_title,
                'subjects': subjects
            })
    
    return results

def test_results_functionality(session, token):
    """Test results functionality directly"""
    print("\n=== Testing Results Functionality ===")
    
    try:
        # Test accessing results page
        print("1. Accessing results page...")
        results_url = f"{Config.BASE_URL}/ktuacademics/student/results"
        
        response = session.get(results_url)
        print(f"   Results page status: {response.status_code}")
        
        if response.status_code != 200:
            print("   ❌ Failed to access results page")
            return
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check if login is required
        title = soup.find("title")
        if title and "login" in title.text.lower():
            print("   ❌ Redirected to login - session may have expired")
            return
            
        print("   ✅ Successfully accessed results page")
        
        # Test finding results sections
        print("2. Looking for results sections...")
        
        # Look for sessional exam results
        sessional_section = soup.find('h5', string='Sessional Exam Results')
        if sessional_section:
            print("   ✅ Found Sessional Exam Results section")
        else:
            print("   ⚠️  Sessional Exam Results section not found")
        
        # Look for module test results
        module_section = soup.find('h5', string='Module Test Results')
        if module_section:
            print("   ✅ Found Module Test Results section")
        else:
            print("   ⚠️  Module Test Results section not found")
        
        # Look for class project results
        project_section = soup.find('h5', string='Class Project Results')
        if project_section:
            print("   ✅ Found Class Project Results section")
        else:
            print("   ⚠️  Class Project Results section not found")
        
        # Test semester filtering
        print("3. Testing semester 3 filtering...")
        
        # Test the actual function
        test_results = find_semester_results(soup, 3)
        print(f"   Found {len(test_results)} result sections for semester 3")
        
        for i, result in enumerate(test_results):
            print(f"   Section {i+1}: {result.get('type', 'Unknown')} - {len(result.get('subjects', []))} subjects")
        
        if test_results:
            print("   ✅ Results parsing successful")
            # Show sample data
            for result in test_results:
                print(f"\n   📊 {result['title']}:")
                for subject in result['subjects'][:3]:  # Show first 3 subjects
                    print(f"      - {subject['subject_code']}: {subject['subject_name']} = {subject['marks']}")
                if len(result['subjects']) > 3:
                    print(f"      ... and {len(result['subjects'])-3} more subjects")
        else:
            print("   ⚠️  No results found for semester 3")
        
    except Exception as e:
        print(f"   ❌ Results error: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function"""
    print("Starting comprehensive results functionality test...\n")
    
    # Test login
    login_result = test_login_functionality()
    if not login_result:
        print("\n❌ Login failed - cannot proceed with results testing")
        return
    
    session, token = login_result
    
    # Test results
    test_results_functionality(session, token)
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    main()