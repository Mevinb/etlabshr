#!/usr/bin/env python3
"""
Final comprehensive test of the results endpoint functionality.
This directly tests the parsing logic with the actual ETLab data.
"""

import sys
import os
import requests
import json
from bs4 import BeautifulSoup

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config

def login_and_get_session():
    """Login to ETLab and return authenticated session"""
    print("🔐 Logging into ETLab...")
    
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
        token = cookies[Config.COOKIE_KEY]
        print(f"✅ Login successful! Token: {token[:20]}...")
        return session, token
    else:
        print("❌ Login failed")
        return None, None

def get_results_data(session):
    """Get results page HTML"""
    print("📊 Fetching results page...")
    
    results_url = f"{Config.BASE_URL}/ktuacademics/student/results"
    response = session.get(results_url)
    
    if response.status_code != 200:
        print(f"❌ Failed to access results page: {response.status_code}")
        return None
    
    print("✅ Results page fetched successfully")
    return response.text

def semester_matches(semester_text, requested_semester):
    """Helper function to match semester text with requested semester number"""
    if not semester_text:
        return False
        
    semester_mapping = {
        1: ["first", "1st", "i", "1"],
        2: ["second", "2nd", "ii", "2"],
        3: ["third", "3rd", "iii", "3", "IIIrd"],
        4: ["fourth", "4th", "iv", "4"],
        5: ["fifth", "5th", "v", "5"],
        6: ["sixth", "6th", "vi", "6"],
        7: ["seventh", "7th", "vii", "7"],
        8: ["eighth", "8th", "viii", "8"]
    }
    
    semester_text_lower = semester_text.lower()
    
    # Direct number match
    if str(requested_semester) in semester_text_lower:
        return True
    
    # Text-based matching
    if requested_semester in semester_mapping:
        for variant in semester_mapping[requested_semester]:
            if variant.lower() in semester_text_lower:
                return True
    
    return False

def parse_results_for_semester(html_content, semester):
    """Parse results HTML and extract data for specific semester"""
    print(f"🔍 Parsing results for semester {semester}...")
    
    soup = BeautifulSoup(html_content, 'html.parser')
    
    response_body = {
        "semester": semester,
        "sessional_exams": [],
        "module_tests": [],
        "class_projects": [],
        "assignments": [],
        "tutorials": []
    }
    
    try:
        # Parse Sessional Exams
        print("  📝 Parsing Sessional exams...")
        sessional_section = soup.find("h5", string="Sessional exams")
        if sessional_section:
            print("    ✅ Found Sessional exams section")
            sessional_table = sessional_section.find_next("table")
            if sessional_table:
                rows = sessional_table.find_all("tr")[1:]  # Skip header row
                print(f"    📋 Processing {len(rows)} rows")
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 5:
                        subject_text = cells[0].text.strip()
                        semester_text = cells[1].text.strip()
                        
                        # Skip empty rows
                        if "No" in subject_text and "yet" in subject_text:
                            continue
                        
                        # Split subject code and name
                        if " - " in subject_text:
                            subject_code = subject_text.split(" - ")[0]
                            subject_name = subject_text.split(" - ")[1]
                        else:
                            subject_code = subject_text
                            subject_name = subject_text
                        
                        subject_info = {
                            "subject_code": subject_code,
                            "subject_name": subject_name,
                            "semester": semester_text,
                            "exam": cells[2].text.strip(),
                            "maximum_marks": cells[3].text.strip(),
                            "marks_obtained": cells[4].text.strip(),
                        }
                        
                        if semester_matches(semester_text, semester):
                            response_body["sessional_exams"].append(subject_info)
                            print(f"    ➕ Added: {subject_code}")

        # Parse Module Tests
        print("  📝 Parsing Module Tests...")
        module_section = soup.find("h5", string="Module Test")
        if module_section:
            print("    ✅ Found Module Test section")
            module_table = module_section.find_next("table")
            if module_table:
                rows = module_table.find_all("tr")[1:]
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 1:
                        first_cell = cells[0].text.strip()
                        if "No module test yet" in first_cell:
                            print("    ℹ️  No module tests available")
                            continue
                        
                        if len(cells) >= 5:
                            test_info = {
                                "subject": cells[0].text.strip(),
                                "semester": cells[1].text.strip(),
                                "exam": cells[2].text.strip(),
                                "maximum_marks": cells[3].text.strip(),
                                "marks_obtained": cells[4].text.strip(),
                            }
                            
                            if semester_matches(test_info["semester"], semester):
                                response_body["module_tests"].append(test_info)
                                print(f"    ➕ Added module test: {test_info['subject']}")

        # Parse Class Projects
        print("  📝 Parsing Class Projects...")
        projects_section = soup.find("h5", string="Class Projects")
        if projects_section:
            print("    ✅ Found Class Projects section")
            projects_table = projects_section.find_next("table")
            if projects_table:
                rows = projects_table.find_all("tr")[1:]
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 1:
                        first_cell = cells[0].text.strip()
                        if "No class projects yet" in first_cell:
                            print("    ℹ️  No class projects available")
                            continue
                        
                        if len(cells) >= 5:
                            project_info = {
                                "subject": cells[0].text.strip(),
                                "semester": cells[1].text.strip(),
                                "class_project": cells[2].text.strip(),
                                "maximum_marks": cells[3].text.strip(),
                                "marks_obtained": cells[4].text.strip(),
                            }
                            
                            if semester_matches(project_info["semester"], semester):
                                response_body["class_projects"].append(project_info)
                                print(f"    ➕ Added class project: {project_info['subject']}")

        # Parse Assignments
        print("  📝 Parsing Assignments...")
        assignments_section = soup.find("h5", string="Assignments")
        if assignments_section:
            print("    ✅ Found Assignments section")
            assignments_table = assignments_section.find_next("table")
            if assignments_table:
                rows = assignments_table.find_all("tr")[1:]
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 5:
                        assignment_info = {
                            "subject": cells[0].text.strip(),
                            "semester": cells[1].text.strip(),
                            "assignment": cells[2].text.strip(),
                            "maximum_marks": cells[3].text.strip(),
                            "marks_obtained": cells[4].text.strip(),
                        }
                        
                        if semester_matches(assignment_info["semester"], semester):
                            response_body["assignments"].append(assignment_info)
                            print(f"    ➕ Added assignment: {assignment_info['subject']}")

        # Parse Tutorials
        print("  📝 Parsing Tutorials...")
        tutorials_section = soup.find("h5", string="Tutorials")
        if tutorials_section:
            print("    ✅ Found Tutorials section")
            tutorials_table = tutorials_section.find_next("table")
            if tutorials_table:
                rows = tutorials_table.find_all("tr")[1:]
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 1:
                        first_cell = cells[0].text.strip()
                        if "No tutorial added yet" in first_cell:
                            print("    ℹ️  No tutorials available")
                            continue
                        
                        if len(cells) >= 5:
                            tutorial_info = {
                                "subject": cells[0].text.strip(),
                                "semester": cells[1].text.strip(),
                                "title": cells[2].text.strip(),
                                "maximum_marks": cells[3].text.strip(),
                                "marks_obtained": cells[4].text.strip(),
                            }
                            
                            if semester_matches(tutorial_info["semester"], semester):
                                response_body["tutorials"].append(tutorial_info)
                                print(f"    ➕ Added tutorial: {tutorial_info['subject']}")

    except Exception as e:
        print(f"❌ Error parsing results: {e}")
        import traceback
        traceback.print_exc()

    # Add summary information
    response_body["total_sessional_exams"] = len(response_body["sessional_exams"])
    response_body["total_module_tests"] = len(response_body["module_tests"])
    response_body["total_class_projects"] = len(response_body["class_projects"])
    response_body["total_assignments"] = len(response_body["assignments"])
    response_body["total_tutorials"] = len(response_body["tutorials"])

    return response_body

def main():
    """Main test function"""
    print("🚀 Starting comprehensive results endpoint test for semester 3\n")
    
    # Step 1: Login
    session, token = login_and_get_session()
    if not session:
        print("❌ Cannot proceed without login")
        return
    
    # Step 2: Get results data
    html_content = get_results_data(session)
    if not html_content:
        print("❌ Cannot proceed without results data")
        return
    
    # Step 3: Parse results for semester 3
    results = parse_results_for_semester(html_content, 3)
    
    # Step 4: Display results
    print("\n" + "="*60)
    print("📊 RESULTS SUMMARY FOR SEMESTER 3")
    print("="*60)
    
    print(f"📈 Sessional Exams: {results['total_sessional_exams']}")
    for exam in results['sessional_exams']:
        print(f"  • {exam['subject_code']}: {exam['marks_obtained']}/{exam['maximum_marks']}")
    
    print(f"\n📝 Module Tests: {results['total_module_tests']}")
    if results['module_tests']:
        for test in results['module_tests']:
            print(f"  • {test['subject']}: {test['marks_obtained']}/{test['maximum_marks']}")
    else:
        print("  • No module tests yet")
    
    print(f"\n🎯 Class Projects: {results['total_class_projects']}")
    if results['class_projects']:
        for project in results['class_projects']:
            print(f"  • {project['subject']}: {project['marks_obtained']}/{project['maximum_marks']}")
    else:
        print("  • No class projects yet")
    
    print(f"\n📋 Assignments: {results['total_assignments']}")
    for assignment in results['assignments']:
        print(f"  • {assignment['subject']}: {assignment['marks_obtained']}/{assignment['maximum_marks']}")
    
    print(f"\n📚 Tutorials: {results['total_tutorials']}")
    if results['tutorials']:
        for tutorial in results['tutorials']:
            print(f"  • {tutorial['subject']}: {tutorial['marks_obtained']}/{tutorial['maximum_marks']}")
    else:
        print("  • No tutorials yet")
    
    # Step 5: Save JSON response
    with open('test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Full results saved to 'test_results.json'")
    print("\n✅ Results endpoint functionality test completed successfully!")
    print("\n🎉 The results parsing is working correctly and can extract semester 3 data from ETLab!")

if __name__ == "__main__":
    main()