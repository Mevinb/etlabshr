import requests
from bs4 import BeautifulSoup
from flask import Blueprint, jsonify, request

from app.utils.token_required import require_token_auth
from config import Config

bp = Blueprint("results", __name__, url_prefix="/api")


@bp.route("/results", methods=["GET"])
@require_token_auth
def results():
    semester = request.args.get("semester")
    
    # If semester is provided, validate it
    if semester:
        try:
            semester = int(semester)
        except ValueError:
            return jsonify({"message": "Semester should be a valid integer"}), 400

        if not (semester >= 1 and semester <= 8):
            return (
                jsonify(
                    {"message": "Invalid semester. Semester has to be between 1 and 8"}
                ),
                400,
            )
    else:
        # If no semester provided, we'll fetch all available results
        semester = None

    # Extract token from Authorization header (format: "Bearer <token>")
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        token = auth_header

    headers = {
        "User-Agent": Config.USER_AGENT,
    }
    cookie = {Config.COOKIE_KEY: token}
    response = requests.get(
        f"{Config.BASE_URL}/ktuacademics/student/results",
        headers=headers,
        cookies=cookie,
    )
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("title")
    if title and "login" in title.text.lower():
        return jsonify({"message": "Token expired. Please login again."}), 401

    response_body = {
        "sessional_exams": [],
        "module_tests": [],
        "class_projects": [],
        "assignments": [],
        "tutorials": []
    }

    try:
        # Parse Sessional Exams (using robust search for header with whitespace)
        sessional_section = soup.find("h5", string=lambda text: text and "sessional" in text.lower() and "exam" in text.lower())
        if sessional_section:
            print("DEBUG: Found Sessional exams section")
            sessional_table = sessional_section.find_next("table")
            if sessional_table:
                print("DEBUG: Found sessional table")
                rows = sessional_table.find_all("tr")[1:]  # Skip header row
                print(f"DEBUG: Found {len(rows)} rows in sessional table")
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 5:  # Based on exploration: Subject, Semester, Exam, Maximum Marks, Marks Obtained
                        subject_text = cells[0].text.strip()
                        semester_text = cells[1].text.strip()
                        
                        print(f"DEBUG: Processing row - Subject: {subject_text}, Semester: {semester_text}")
                        
                        # Skip empty or "No ..." rows
                        if "No" in subject_text and "yet" in subject_text:
                            continue
                            
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
                            "exam": cells[2].text.strip(),
                            "maximum_marks": cells[3].text.strip(),
                            "marks_obtained": cells[4].text.strip(),
                        }
                        
                        # Filter by requested semester
                        if semester_matches(semester_text, semester):
                            response_body["sessional_exams"].append(subject_info)
                            print(f"DEBUG: Added sessional exam: {subject_code}")

        # Parse Module Tests (using robust search)
        module_section = soup.find("h5", string=lambda text: text and "module" in text.lower() and "test" in text.lower())
        if module_section:
            print("DEBUG: Found Module Test section")
            module_table = module_section.find_next("table")
            if module_table:
                print("DEBUG: Found module table")
                rows = module_table.find_all("tr")[1:]  # Skip header row
                print(f"DEBUG: Found {len(rows)} rows in module table")
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 1:
                        first_cell = cells[0].text.strip()
                        if "No module test yet" in first_cell:
                            print("DEBUG: No module tests available")
                            continue
                            
                        if len(cells) >= 5:
                            test_info = {
                                "subject": cells[0].text.strip(),
                                "semester": cells[1].text.strip(),
                                "exam": cells[2].text.strip(),
                                "maximum_marks": cells[3].text.strip(),
                                "marks_obtained": cells[4].text.strip(),
                            }
                            
                            # Filter by requested semester
                            if semester_matches(test_info["semester"], semester):
                                response_body["module_tests"].append(test_info)
                                print(f"DEBUG: Added module test: {test_info['subject']}")

        # Parse Class Projects (using robust search)
        projects_section = soup.find("h5", string=lambda text: text and "class" in text.lower() and "project" in text.lower())
        if projects_section:
            print("DEBUG: Found Class Projects section")
            projects_table = projects_section.find_next("table")
            if projects_table:
                print("DEBUG: Found projects table")
                rows = projects_table.find_all("tr")[1:]  # Skip header row
                print(f"DEBUG: Found {len(rows)} rows in projects table")
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 1:
                        first_cell = cells[0].text.strip()
                        if "No class projects yet" in first_cell:
                            print("DEBUG: No class projects available")
                            continue
                            
                        if len(cells) >= 5:
                            project_info = {
                                "subject": cells[0].text.strip(),
                                "semester": cells[1].text.strip(),
                                "class_project": cells[2].text.strip(),
                                "maximum_marks": cells[3].text.strip(),
                                "marks_obtained": cells[4].text.strip(),
                            }
                            
                            # Filter by requested semester
                            if semester_matches(project_info["semester"], semester):
                                response_body["class_projects"].append(project_info)
                                print(f"DEBUG: Added class project: {project_info['subject']}")

        # Parse Assignments (using robust search)
        assignments_section = soup.find("h5", string=lambda text: text and "assignment" in text.lower())
        if assignments_section:
            print("DEBUG: Found Assignments section")
            assignments_table = assignments_section.find_next("table")
            if assignments_table:
                print("DEBUG: Found assignments table")
                rows = assignments_table.find_all("tr")[1:]  # Skip header row
                print(f"DEBUG: Found {len(rows)} rows in assignments table")
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 1:
                        first_cell = cells[0].text.strip()
                        if "No" in first_cell and "yet" in first_cell:
                            print("DEBUG: No assignments available")
                            continue
                            
                        if len(cells) >= 5:
                            assignment_info = {
                                "subject": cells[0].text.strip(),
                                "semester": cells[1].text.strip(),
                                "assignment": cells[2].text.strip(),
                                "maximum_marks": cells[3].text.strip(),
                                "marks_obtained": cells[4].text.strip(),
                            }
                            
                            # Filter by requested semester
                            if semester_matches(assignment_info["semester"], semester):
                                response_body["assignments"].append(assignment_info)
                                print(f"DEBUG: Added assignment: {assignment_info['subject']}")

        # Parse Tutorials (using robust search)
        tutorials_section = soup.find("h5", string=lambda text: text and "tutorial" in text.lower())
        if tutorials_section:
            print("DEBUG: Found Tutorials section")
            tutorials_table = tutorials_section.find_next("table")
            if tutorials_table:
                print("DEBUG: Found tutorials table")
                rows = tutorials_table.find_all("tr")[1:]  # Skip header row
                print(f"DEBUG: Found {len(rows)} rows in tutorials table")
                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) >= 1:
                        first_cell = cells[0].text.strip()
                        if "No" in first_cell and "yet" in first_cell:
                            print("DEBUG: No tutorials available")
                            continue
                            
                        if len(cells) >= 5:
                            tutorial_info = {
                                "subject": cells[0].text.strip(),
                                "semester": cells[1].text.strip(),
                                "title": cells[2].text.strip(),
                                "maximum_marks": cells[3].text.strip(),
                                "marks_obtained": cells[4].text.strip(),
                            }
                            
                            # Filter by requested semester
                            if semester_matches(tutorial_info["semester"], semester):
                                response_body["tutorials"].append(tutorial_info)
                                print(f"DEBUG: Added tutorial: {tutorial_info['subject']}")

    except Exception as e:
        # Log the error but don't fail completely
        print(f"Error parsing results: {e}")
        # Return empty results instead of failing

    # Add debug information
    print(f"Debug: Found {len(response_body['sessional_exams'])} sessional exams for semester {semester}")
    print(f"Debug: Found {len(response_body['module_tests'])} module tests for semester {semester}")
    print(f"Debug: Found {len(response_body['class_projects'])} class projects for semester {semester}")
    print(f"Debug: Found {len(response_body['assignments'])} assignments for semester {semester}")
    print(f"Debug: Found {len(response_body['tutorials'])} tutorials for semester {semester}")

    # Add summary information
    response_body["total_sessional_exams"] = len(response_body["sessional_exams"])
    response_body["total_module_tests"] = len(response_body["module_tests"])
    response_body["total_class_projects"] = len(response_body["class_projects"])
    response_body["total_assignments"] = len(response_body["assignments"])
    response_body["total_tutorials"] = len(response_body["tutorials"])
    
    # Add debug info to response for troubleshooting
    response_body["debug_info"] = {
        "requested_semester": semester,
        "semester_filter_applied": semester is not None,
        "sections_found": ["sessional_exams", "module_tests", "class_projects", "assignments", "tutorials"]
    }

    return jsonify(response_body), 200


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
    print(f"Debug: Semester text '{semester_text}' didn't match requested semester {requested_semester}")
    return False  # Only return matching semester results