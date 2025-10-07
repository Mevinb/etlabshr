#!/usr/bin/env python3
"""
Debug the results parsing step by step
"""

import requests
import json
from bs4 import BeautifulSoup
from app import create_app

def debug_results_parsing():
    """Debug exactly what happens during results parsing"""
    
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
        
        # Now test the results parsing step by step
        print("\n🔍 Testing results parsing...")
        
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
        
        # Test semester matching function
        def semester_matches(semester_text, requested_semester):
            """Helper function to match semester text with requested semester number"""
            if not semester_text:
                return False
            
            # If no specific semester requested, return all results
            if requested_semester is None:
                return True
                
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
            
            # Debug message for unmatched semesters
            print(f"    Debug: Semester text '{semester_text}' didn't match requested semester {requested_semester}")
            return False
        
        # Test both with semester=3 and semester=None
        for test_semester in [None, 3]:
            print(f"\n📊 Testing with semester = {test_semester}")
            print("-" * 40)
            
            response_body = {
                "sessional_exams": [],
                "module_tests": [],
                "class_projects": [],
                "assignments": [],
                "tutorials": []
            }
            
            # Parse Sessional Exams
            sessional_section = soup.find("h5", string="Sessional exams")
            if sessional_section:
                print("✅ Found Sessional exams section")
                sessional_table = sessional_section.find_next("table")
                if sessional_table:
                    print("✅ Found sessional table")
                    rows = sessional_table.find_all("tr")[1:]  # Skip header row
                    print(f"✅ Found {len(rows)} rows in sessional table")
                    
                    for i, row in enumerate(rows):
                        cells = row.find_all("td")
                        print(f"\n  Row {i+1}: {len(cells)} cells")
                        if len(cells) >= 5:
                            subject_text = cells[0].text.strip()
                            semester_text = cells[1].text.strip()
                            exam_text = cells[2].text.strip()
                            max_marks = cells[3].text.strip()
                            marks_obtained = cells[4].text.strip()
                            
                            print(f"    Subject: '{subject_text}'")
                            print(f"    Semester: '{semester_text}'")
                            print(f"    Exam: '{exam_text}'")
                            print(f"    Max Marks: '{max_marks}'")
                            print(f"    Marks Obtained: '{marks_obtained}'")
                            
                            # Skip empty or "No ..." rows
                            if "No" in subject_text and "yet" in subject_text:
                                print("    ❌ Skipping 'No ... yet' row")
                                continue
                            
                            # Test semester matching
                            matches = semester_matches(semester_text, test_semester)
                            print(f"    Semester matches: {matches}")
                            
                            if matches:
                                # Split subject code and name if they exist
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
                                    "exam": exam_text,
                                    "maximum_marks": max_marks,
                                    "marks_obtained": marks_obtained,
                                }
                                
                                response_body["sessional_exams"].append(subject_info)
                                print(f"    ✅ Added to results: {subject_code}")
                            else:
                                print(f"    ❌ Not added due to semester mismatch")
                        else:
                            print(f"    ❌ Row has only {len(cells)} cells, need at least 5")
                            for j, cell in enumerate(cells):
                                print(f"      Cell {j}: '{cell.text.strip()}'")
                else:
                    print("❌ No table found after Sessional exams header")
            else:
                print("❌ No Sessional exams section found")
            
            print(f"\n📊 FINAL RESULTS for semester {test_semester}:")
            print(f"   Sessional exams: {len(response_body['sessional_exams'])}")
            if response_body['sessional_exams']:
                for exam in response_body['sessional_exams']:
                    print(f"     - {exam['subject_code']}: {exam['marks_obtained']}/{exam['maximum_marks']}")

if __name__ == "__main__":
    print("🎓 ETLab Results Parsing Debug")
    print("=" * 50)
    debug_results_parsing()