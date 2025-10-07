import requests
from bs4 import BeautifulSoup
from flask import Blueprint, jsonify, request
import re

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
        f"{Config.BASE_URL}/universityexam/student/examresult",
        headers=headers,
        cookies=cookie,
    )
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("title")
    if title and "login" in title.text.lower():
        return jsonify({"message": "Token expired. Please login again."}), 401

    response_body = {
        "end_semester_exams": [],
        "total_end_semester_exams": 0,
        "available_links": []
    }

    try:
        # Parse End Semester Exams from the university exam page
        # Look for divs with blue background that contain exam information
        exam_divs = soup.find_all("div", style=lambda style: style and "background-color:#0864a2" in style)
        
        print(f"DEBUG: Found {len(exam_divs)} exam divs with blue background")
        
        for div in exam_divs:
            exam_text = div.text.strip()
            if exam_text and "semester" in exam_text.lower() and ("exam" in exam_text.lower() or "examination" in exam_text.lower()):
                print(f"DEBUG: Processing exam: {exam_text}")
                
                # Parse semester information from the text
                semester_info = parse_semester_from_text(exam_text)
                
                exam_info = {
                    "exam_title": exam_text,
                    "semester": semester_info.get("semester", "Unknown"),
                    "exam_type": semester_info.get("exam_type", "End Semester"),
                    "year": semester_info.get("year", "Unknown"),
                    "admission_batch": semester_info.get("admission_batch", "Unknown")
                }
                
                # Filter by requested semester if provided
                if semester is None or semester_matches_exam(semester_info.get("semester", ""), semester):
                    response_body["end_semester_exams"].append(exam_info)
                    print(f"DEBUG: Added end semester exam: {exam_text[:50]}...")
        
        # Also look for clickable links that might lead to detailed results
        exam_links = []
        # Look for links in span3 elements (next to the exam divs)
        span3_elements = soup.find_all("div", class_="span3")
        for span3 in span3_elements:
            links = span3.find_all("a", href=True)
            for link in links:
                if link.text.strip() and "result" in link.text.lower():
                    exam_links.append({
                        "text": link.text.strip(),
                        "href": link["href"]
                    })
        
        response_body["available_links"] = exam_links
        response_body["total_end_semester_exams"] = len(response_body["end_semester_exams"])
        
        print(f"DEBUG: Found {len(response_body['end_semester_exams'])} end semester exams")
        print(f"DEBUG: Found {len(exam_links)} additional result links")

    except Exception as e:
        # Log the error but don't fail completely
        print(f"Error parsing end semester results: {e}")
        # Return empty results instead of failing

    # Add debug information
    response_body["debug_info"] = {
        "requested_semester": semester,
        "semester_filter_applied": semester is not None,
        "url_used": f"{Config.BASE_URL}/universityexam/student/examresult",
        "note": "End semester results from university exam portal"
    }

    return jsonify(response_body), 200


def parse_semester_from_text(exam_text):
    """Extract semester information from exam text"""
    info = {
        "semester": "Unknown",
        "exam_type": "End Semester",
        "year": "Unknown",
        "admission_batch": "Unknown"
    }
    
    # Extract semester number
    semester_patterns = [
        r"First\s+Semester",
        r"Second\s+Semester", 
        r"Third\s+Semester",
        r"Fourth\s+Semester",
        r"Fifth\s+Semester",
        r"Sixth\s+Semester",
        r"Seventh\s+Semester",
        r"Eighth\s+Semester"
    ]
    
    semester_mapping = {
        "First": "1", "Second": "2", "Third": "3", "Fourth": "4",
        "Fifth": "5", "Sixth": "6", "Seventh": "7", "Eighth": "8"
    }
    
    for pattern in semester_patterns:
        match = re.search(pattern, exam_text, re.IGNORECASE)
        if match:
            semester_word = match.group().split()[0]
            info["semester"] = semester_mapping.get(semester_word.title(), "Unknown")
            break
    
    # Extract year
    year_match = re.search(r"(20\d{2})", exam_text)
    if year_match:
        info["year"] = year_match.group(1)
    
    # Extract admission batch
    admission_match = re.search(r"\((\d{4})\s+Admission\)", exam_text)
    if admission_match:
        info["admission_batch"] = admission_match.group(1)
    
    # Determine exam type
    if "regular" in exam_text.lower():
        info["exam_type"] = "Regular End Semester"
    elif "(r)" in exam_text.lower():
        info["exam_type"] = "Regular"
    elif "supplementary" in exam_text.lower():
        info["exam_type"] = "Supplementary"
    
    return info


def semester_matches_exam(exam_semester, requested_semester):
    """Check if exam semester matches requested semester"""
    if requested_semester is None:
        return True
    
    try:
        exam_sem_num = int(exam_semester)
        return exam_sem_num == requested_semester
    except (ValueError, TypeError):
        return False