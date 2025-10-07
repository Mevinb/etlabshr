import requests
from bs4 import BeautifulSoup
from flask import Blueprint, jsonify, request

from app.utils.token_required import require_token_auth
from config import Config

bp = Blueprint("end_semester_results", __name__, url_prefix="/api")


@bp.route("/end-semester-results", methods=["GET"])
@require_token_auth
def end_semester_results():
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
        "end_semester_exams": []
    }

    try:
        # Parse End Semester Exams (using robust search for various patterns)
        end_semester_patterns = [
            lambda text: text and "end semester" in text.lower() and "exam" in text.lower(),
            lambda text: text and "semester examination" in text.lower(),
            lambda text: text and "regular" in text.lower() and "semester" in text.lower() and ("exam" in text.lower() or "examination" in text.lower()),
            lambda text: text and "b.tech" in text.lower() and "semester" in text.lower() and ("exam" in text.lower() or "examination" in text.lower())
        ]
        
        for pattern in end_semester_patterns:
            end_semester_section = soup.find("h5", string=pattern)
            if not end_semester_section:
                # Try finding in other header tags
                end_semester_section = soup.find(["h3", "h4", "h6"], string=pattern)
            if not end_semester_section:
                # Try finding in div or span elements
                end_semester_section = soup.find(["div", "span"], string=pattern)
            
            if end_semester_section:
                print(f"DEBUG: Found End Semester section with pattern")
                end_semester_table = end_semester_section.find_next("table")
                if end_semester_table:
                    print("DEBUG: Found end semester table")
                    rows = end_semester_table.find_all("tr")[1:]  # Skip header row
                    print(f"DEBUG: Found {len(rows)} rows in end semester table")
                    for row in rows:
                        cells = row.find_all("td")
                        if len(cells) >= 1:
                            first_cell = cells[0].text.strip()
                            if "No" in first_cell and ("result" in first_cell or "exam" in first_cell):
                                print("DEBUG: No end semester exams available")
                                continue
                                
                            if len(cells) >= 5:
                                subject_text = cells[0].text.strip()
                                semester_text = cells[1].text.strip()
                                
                                print(f"DEBUG: Processing end semester row - Subject: {subject_text}, Semester: {semester_text}")
                                
                                # Split subject code and name if they exist
                                if " - " in subject_text:
                                    subject_code = subject_text.split(" - ")[0]
                                    subject_name = subject_text.split(" - ")[1]
                                else:
                                    subject_code = subject_text
                                    subject_name = subject_text
                                
                                end_semester_info = {
                                    "subject_code": subject_code,
                                    "subject_name": subject_name,
                                    "semester": semester_text,
                                    "exam": cells[2].text.strip(),
                                    "maximum_marks": cells[3].text.strip(),
                                    "marks_obtained": cells[4].text.strip(),
                                }
                                
                                # Filter by requested semester
                                if semester_matches(semester_text, semester):
                                    response_body["end_semester_exams"].append(end_semester_info)
                                    print(f"DEBUG: Added end semester exam: {subject_code}")
                break  # Exit pattern loop if we found a match

        # Also look for any links or buttons that might lead to end semester results
        view_result_links = soup.find_all("a", string=lambda text: text and "view result" in text.lower())
        if not view_result_links:
            view_result_links = soup.find_all("button", string=lambda text: text and "view result" in text.lower())
        
        end_semester_links = []
        if view_result_links:
            print(f"DEBUG: Found {len(view_result_links)} View Result links/buttons")
            
            # Look for semester examination related buttons
            for link in view_result_links:
                # Find parent element that might contain semester information
                parent_text = ""
                current = link.parent
                while current and len(parent_text) < 200:
                    if current.text:
                        parent_text = current.text.lower()
                        break
                    current = current.parent
                
                if any(pattern in parent_text for pattern in ["semester examination", "end semester", "regular", "b.tech"]):
                    print(f"DEBUG: Found potential end semester result link: {parent_text[:100]}")
                    href = link.get('href', '')
                    onclick = link.get('onclick', '')
                    
                    link_info = {
                        "text": link.text.strip(),
                        "href": href,
                        "onclick": onclick,
                        "context": parent_text[:200]
                    }
                    end_semester_links.append(link_info)
        
        # Add links information to response
        if end_semester_links:
            response_body["available_links"] = end_semester_links

    except Exception as e:
        print(f"Error parsing end semester results: {e}")
        return jsonify({"message": f"Error parsing results: {str(e)}"}), 500

    # Add summary information
    response_body["total_end_semester_exams"] = len(response_body["end_semester_exams"])
    
    # Add debug info
    response_body["debug_info"] = {
        "requested_semester": semester,
        "semester_filter_applied": semester is not None,
        "endpoint": "end_semester_results"
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
    
    return False