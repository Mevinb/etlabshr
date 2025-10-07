#!/usr/bin/env python3
"""
Debug script to analyze end semester results page structure
"""

import json
import requests
from bs4 import BeautifulSoup
from app import create_app

def debug_end_semester_results():
    """Debug the end semester results page structure"""
    app = create_app()
    
    with app.test_client() as client:
        print("🔍 Debugging End Semester Results")
        print("=" * 35)
        
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
        
        # Check different results pages
        print("\n2. Analyzing results pages...")
        
        # Import config for proper headers
        from config import Config
        
        headers = {
            "User-Agent": Config.USER_AGENT,
        }
        cookie = {Config.COOKIE_KEY: token}
        
        # Try main results page
        print("\n📊 Main Results Page:")
        response = requests.get(
            f"{Config.BASE_URL}/ktuacademics/student/results",
            headers=headers,
            cookies=cookie,
        )
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            print(f"✅ Status: {response.status_code}")
            
            # Look for end semester related links or sections
            print("\n🔍 Looking for end semester patterns...")
            
            # Check for any links with "semester" in them
            semester_links = soup.find_all("a", string=lambda text: text and "semester" in text.lower())
            print(f"📎 Found {len(semester_links)} semester-related links:")
            for i, link in enumerate(semester_links[:5]):  # Show first 5
                href = link.get('href', 'No href')
                text = link.text.strip()
                print(f"   {i+1}. {text} -> {href}")
            
            # Check for any buttons or elements with "View Result"
            view_result_elements = soup.find_all(string=lambda text: text and "view result" in text.lower())
            print(f"\n🔍 Found {len(view_result_elements)} 'View Result' elements:")
            for i, element in enumerate(view_result_elements[:5]):
                parent = element.parent if element.parent else None
                parent_tag = parent.name if parent else "No parent"
                parent_attrs = parent.attrs if parent else {}
                print(f"   {i+1}. Text: '{element.strip()}' | Parent: <{parent_tag}> {parent_attrs}")
            
            # Check for semester examination patterns
            exam_patterns = [
                "end semester",
                "semester examination", 
                "regular.*semester",
                "december.*2024",
                "may.*2025",
                "november.*2025"
            ]
            
            print(f"\n🔍 Searching for exam patterns...")
            for pattern in exam_patterns:
                elements = soup.find_all(string=lambda text: text and any(p in text.lower() for p in pattern.split('.*')))
                if elements:
                    print(f"   📋 Pattern '{pattern}': {len(elements)} matches")
                    for elem in elements[:3]:  # Show first 3
                        print(f"      - {elem.strip()[:100]}...")
            
            # Check for any forms or action URLs
            forms = soup.find_all("form")
            print(f"\n📝 Found {len(forms)} forms:")
            for i, form in enumerate(forms[:3]):
                action = form.get('action', 'No action')
                method = form.get('method', 'No method')
                print(f"   {i+1}. Action: {action} | Method: {method}")
                
                # Check inputs in this form
                inputs = form.find_all("input")
                for inp in inputs[:3]:
                    inp_type = inp.get('type', 'No type')
                    inp_name = inp.get('name', 'No name')
                    inp_value = inp.get('value', 'No value')
                    print(f"      - Input: {inp_type} | Name: {inp_name} | Value: {inp_value}")
            
            # Save full HTML for manual inspection
            with open("debug_end_semester_results.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"\n💾 Full HTML saved to debug_end_semester_results.html")
            
        else:
            print(f"❌ Failed to get results page: {response.status_code}")
        
        # Try exam registration page (as shown in image breadcrumb)
        print("\n📋 Exam Registration Page:")
        response = requests.get(
            f"{Config.BASE_URL}/student/examregistration",
            headers=headers,
            cookies=cookie,
        )
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            print(f"✅ Status: {response.status_code}")
            
            # Look for result-related elements
            result_elements = soup.find_all(string=lambda text: text and "result" in text.lower())
            print(f"📊 Found {len(result_elements)} result-related elements:")
            for i, element in enumerate(result_elements[:5]):
                print(f"   {i+1}. {element.strip()[:100]}")
            
            # Save this HTML too
            with open("debug_exam_registration.html", "w", encoding="utf-8") as f:
                f.write(response.text)
            print(f"💾 Exam registration HTML saved to debug_exam_registration.html")
            
        else:
            print(f"❌ Failed to get exam registration page: {response.status_code}")

if __name__ == "__main__":
    debug_end_semester_results()