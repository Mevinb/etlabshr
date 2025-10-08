import requests
from bs4 import BeautifulSoup
from flask import Blueprint, jsonify, request
import re

from app.utils.token_required import require_token_auth
from config import Config

bp = Blueprint("end_semester_results", __name__, url_prefix="/api")


def scrape_detailed_results(url, headers, cookie, referer_url):
    """
    Scrapes the detailed result page with precise, robust selectors.
    """
    try:
        # Add the Referer header to the request to simulate site navigation
        detail_headers = headers.copy()
        detail_headers['Referer'] = referer_url
        
        response = requests.get(url, headers=detail_headers, cookies=cookie)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Check if we were redirected to the login page
        if soup.find("title") and "login" in soup.find("title").text.lower():
            return {"error": "Session invalid for detail page. Redirected to login.", "url": url}

        # --- Part 1: Precisely find the exam details ---
        exam_details = {}
        labels = {"Name of Exam": "nameOfExam", "Degree": "degree", "Semester": "semester", 
                  "Academic Year": "academicYear", "Month": "month", "Year": "year"}
        
        for label_text, key_name in labels.items():
            # Find a <td> containing the exact label text (ignoring whitespace)
            label_element = soup.find('td', string=re.compile(r'\s*' + re.escape(label_text) + r'\s*'))
            if label_element:
                # Find the very next <td> sibling, which holds the value
                value_element = label_element.find_next_sibling('td')
                if value_element:
                    exam_details[key_name] = value_element.get_text(strip=True)

        # --- Part 2: Precisely find the main results table ---
        main_table = None
        # Find all tables and loop through them
        for table in soup.find_all("table"):
            # The correct table is the one with a "Course Code" header
            if table.find('th', string=re.compile(r'Course Code')):
                main_table = table
                break
        
        if not main_table:
            return {"error": "Could not find the main results table with expected headers.", "url": url}
        
        # --- Part 3: Parse the now-correctly-identified table ---
        subjects, summary = [], {}
        headers_list = [th.text.strip() for th in main_table.find_all("th")]
        rows = main_table.find("tbody").find_all("tr") if main_table.find("tbody") else main_table.find_all("tr")[1:]

        for row in rows:
            cols = row.find_all("td")
            if not cols: continue
            
            first_col_text = cols[0].text.strip()
            if "Earned Credit" in first_col_text: summary["earnedCredit"] = cols[1].text.strip() if len(cols) > 1 else None
            elif "SGPA" in first_col_text: summary["sgpa"] = cols[1].text.strip() if len(cols) > 1 else None
            elif "CGPA" in first_col_text: summary["cgpa"] = cols[1].text.strip() if len(cols) > 1 else None
            elif len(cols) == len(headers_list):
                subjects.append({headers_list[i]: cols[i].text.strip() for i in range(len(headers_list))})

        return {"examDetails": exam_details, "results": subjects, "summary": summary}

    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch result page: {e}", "url": url}
    except Exception as e:
        return {"error": f"An error occurred while parsing result page: {e}", "url": url}


@bp.route("/end-semester-results", methods=["GET"])
@require_token_auth
def end_semester_results():
    semester = request.args.get("semester")
    if semester:
        try:
            semester = int(semester)
            if not (1 <= semester <= 8):
                return jsonify({"message": "Invalid semester. Must be between 1 and 8"}), 400
        except ValueError:
            return jsonify({"message": "Semester should be a valid integer"}), 400
    
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.split(" ")[1] if auth_header.startswith("Bearer ") else auth_header
    
    headers = {"User-Agent": Config.USER_AGENT}
    cookie = {Config.COOKIE_KEY: token}
    
    list_page_url = f"{Config.BASE_URL}/universityexam/student/examresult"
    response = requests.get(list_page_url, headers=headers, cookies=cookie)
    
    soup = BeautifulSoup(response.text, "html.parser")
    if soup.find("title") and "login" in soup.find("title").text.lower():
        return jsonify({"message": "Token expired. Please login again."}), 401

    response_body = {"end_semester_exams": [], "available_links": []}

    try:
        # Parse exam titles from the main page
        for div in soup.find_all("div", style=lambda s: s and "background-color:#0864a2" in s):
            text = div.text.strip()
            if "semester" in text.lower() and "exam" in text.lower():
                info = parse_semester_from_text(text)
                if semester is None or semester_matches_exam(info.get("semester"), semester):
                    response_body["end_semester_exams"].append({"exam_title": text, **info})
        
        # Find all result links on the main page
        exam_links = []
        for span3 in soup.find_all("div", class_="span3"):
            for link in span3.find_all("a", href=True):
                if "result" in link.text.lower():
                    href = link["href"]
                    # Convert relative URLs to absolute URLs
                    if href.startswith("/"):
                        href = Config.BASE_URL + href
                    exam_links.append({"text": link.text.strip(), "href": href})
        
        # Scrape each link found
        for link_info in exam_links:
            # We use the list page URL as the Referer for the detail page request
            detailed_results = scrape_detailed_results(link_info["href"], headers, cookie, list_page_url)
            link_info["results"] = detailed_results
        
        response_body["available_links"] = exam_links
        response_body["total_end_semester_exams"] = len(response_body["end_semester_exams"])

    except Exception as e:
        print(f"Error parsing end semester results: {e}")

    response_body["debug_info"] = {
        "requested_semester": semester,
        "semester_filter_applied": semester is not None,
        "url_used": list_page_url,
    }

    return jsonify(response_body), 200


def parse_semester_from_text(exam_text):
    info = {"semester": "Unknown", "exam_type": "End Semester", "year": "Unknown", "admission_batch": "Unknown"}
    mapping = {"First": "1", "Second": "2", "Third": "3", "Fourth": "4", "Fifth": "5", "Sixth": "6", "Seventh": "7", "Eighth": "8"}
    for word, num in mapping.items():
        if re.search(fr"{word}\s+Semester", exam_text, re.IGNORECASE): 
            info["semester"] = num
            break
    if (y := re.search(r"(20\d{2})", exam_text)): 
        info["year"] = y.group(1)
    if (a := re.search(r"\((\d{4})\s+Admission\)", exam_text)): 
        info["admission_batch"] = a.group(1)
    if "regular" in exam_text.lower() or "(r)" in exam_text.lower(): 
        info["exam_type"] = "Regular End Semester"
    elif "supplementary" in exam_text.lower(): 
        info["exam_type"] = "Supplementary"
    return info


def semester_matches_exam(exam_semester, requested_semester):
    if requested_semester is None: 
        return True
    try: 
        return int(exam_semester) == requested_semester
    except (ValueError, TypeError): 
        return False