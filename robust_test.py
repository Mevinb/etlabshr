#!/usr/bin/env python3
"""
Final fix for the results parsing with robust header matching
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

def semester_matches(semester_text, requested_semester):
    """Helper function to match semester text with requested semester number"""
    if not semester_text:
        return False
        
    semester_text_lower = semester_text.lower()
    
    # For semester 3, check for "III" (Roman numeral)
    if requested_semester == 3:
        if "iii" in semester_text_lower or "3" in semester_text_lower:
            return True
    
    # General matching for other semesters
    semester_patterns = [
        str(requested_semester),
        f"{requested_semester}st",
        f"{requested_semester}nd", 
        f"{requested_semester}rd",
        f"{requested_semester}th"
    ]
    
    return any(pattern in semester_text_lower for pattern in semester_patterns)

def robust_results_parsing():
    """Parse results with robust header matching"""
    print("🔍 Starting robust results parsing for semester 3...")
    
    session = login_and_get_session()
    if not session:
        print("❌ Login failed")
        return
    
    results_url = f"{Config.BASE_URL}/ktuacademics/student/results"
    response = session.get(results_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    results = {
        "semester": 3,
        "sessional_exams": [],
        "module_tests": [],
        "class_projects": [],
        "assignments": [],
        "tutorials": []
    }
    
    # Find all H5 headers and their following tables
    h5_headers = soup.find_all("h5")
    
    for header in h5_headers:
        header_text = header.get_text(strip=True)
        print(f"\n📝 Processing section: '{header_text}'")
        
        # Find the table after this header
        table = header.find_next("table")
        if not table:
            print(f"  ❌ No table found after '{header_text}'")
            continue
        
        print(f"  ✅ Found table after '{header_text}'")
        
        # Process table rows
        rows = table.find_all("tr")[1:]  # Skip header row
        print(f"  📋 Processing {len(rows)} rows")
        
        section_results = []
        
        for i, row in enumerate(rows):
            cells = row.find_all("td")
            if len(cells) >= 2:
                subject = cells[0].text.strip()
                semester_text = cells[1].text.strip()
                
                print(f"    Row {i+1}: Subject='{subject}', Semester='{semester_text}'")
                
                # Skip "No ... yet" rows
                if "No" in subject and "yet" in subject:
                    print(f"      ⏭️  Skipping 'No ... yet' row")
                    continue
                
                # Check if this is for semester 3
                if semester_matches(semester_text, 3):
                    print(f"      ✅ MATCHES semester 3!")
                    
                    # Create result entry based on available columns
                    result_entry = {
                        "subject": subject,
                        "semester": semester_text
                    }
                    
                    if len(cells) >= 3:
                        result_entry["exam_or_type"] = cells[2].text.strip()
                    if len(cells) >= 4:
                        result_entry["maximum_marks"] = cells[3].text.strip()
                    if len(cells) >= 5:
                        result_entry["marks_obtained"] = cells[4].text.strip()
                    if len(cells) >= 6:
                        result_entry["view_response"] = cells[5].text.strip()
                    
                    section_results.append(result_entry)
                else:
                    print(f"      ❌ Does not match semester 3")
        
        # Categorize results based on header text
        if "sessional" in header_text.lower():
            results["sessional_exams"].extend(section_results)
            print(f"  ➕ Added {len(section_results)} sessional exam results")
        elif "module" in header_text.lower():
            results["module_tests"].extend(section_results)
            print(f"  ➕ Added {len(section_results)} module test results")
        elif "project" in header_text.lower():
            results["class_projects"].extend(section_results)
            print(f"  ➕ Added {len(section_results)} class project results")
        elif "assignment" in header_text.lower():
            results["assignments"].extend(section_results)
            print(f"  ➕ Added {len(section_results)} assignment results")
        elif "tutorial" in header_text.lower():
            results["tutorials"].extend(section_results)
            print(f"  ➕ Added {len(section_results)} tutorial results")
    
    # Print final summary
    print("\n" + "="*60)
    print("📊 FINAL RESULTS SUMMARY FOR SEMESTER 3")
    print("="*60)
    
    total_results = 0
    for category, items in results.items():
        if isinstance(items, list):
            count = len(items)
            total_results += count
            print(f"📈 {category.replace('_', ' ').title()}: {count}")
            
            # Show details for each item
            for item in items:
                subject = item.get('subject', 'Unknown')
                marks = item.get('marks_obtained', 'N/A')
                max_marks = item.get('maximum_marks', 'N/A')
                print(f"  • {subject}: {marks}/{max_marks}")
    
    print(f"\n🎯 Total results found for semester 3: {total_results}")
    
    if total_results > 0:
        print("\n✅ SUCCESS! The results endpoint can extract semester 3 data from ETLab!")
    else:
        print("\n⚠️  No semester 3 results found. This could mean:")
        print("   • Student is not in semester 3")
        print("   • No results have been published yet")
        print("   • Semester format is different than expected")
    
    return results

if __name__ == "__main__":
    robust_results_parsing()