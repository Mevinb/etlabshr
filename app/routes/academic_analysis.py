import requests
from bs4 import BeautifulSoup
from flask import Blueprint, jsonify, request
import re

from app.utils.token_required import require_token_auth
from config import Config

bp = Blueprint("academic_analysis", __name__, url_prefix="/api")


def parse_semester_data(soup):
    """
    Parse academic analysis data from the HTML page
    Based on the actual structure from the academic analysis page
    """
    semesters = []
    
    try:
        # Method 1: Look for semester data in the exact structure from the screenshot
        # The data appears to be in a specific layout with semester names followed by metrics
        
        # Find all text that contains semester information
        all_text = soup.get_text()
        
        # Look for patterns like "1st Semester", "IInd Semester", etc.
        semester_patterns = [
            r'(1st\s+Semester)',
            r'(2nd\s+Semester|IInd\s+Semester)', 
            r'(3rd\s+Semester|IIIrd\s+Semester)',
            r'(4th\s+Semester|IVth\s+Semester)',
            r'(5th\s+Semester|Vth\s+Semester)',
            r'(6th\s+Semester|VIth\s+Semester)',
            r'(7th\s+Semester|VIIth\s+Semester)',
            r'(8th\s+Semester|VIIIth\s+Semester)'
        ]
        
        # Method 2: Look for table-based structure
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 6:  # Should have semester, attendance, sgpa, credits, cgpa, result
                    first_cell_text = cells[0].get_text(strip=True)
                    
                    # Check if this row contains semester information
                    semester_match = None
                    semester_number = 0
                    
                    for i, pattern in enumerate(semester_patterns, 1):
                        if re.search(pattern, first_cell_text, re.IGNORECASE):
                            semester_match = first_cell_text
                            semester_number = i
                            break
                    
                    if semester_match:
                        semester_data = {
                            'semester_name': semester_match,
                            'semester_number': semester_number
                        }
                        
                        # Parse attendance (format: "435/450 (97%)")
                        if len(cells) > 1:
                            attendance_text = cells[1].get_text(strip=True)
                            attendance_match = re.search(r'(\d+)/(\d+)\s*\((\d+)%\)', attendance_text)
                            if attendance_match:
                                semester_data['attendance'] = {
                                    'present': int(attendance_match.group(1)),
                                    'total': int(attendance_match.group(2)),
                                    'percentage': int(attendance_match.group(3))
                                }
                            else:
                                semester_data['attendance'] = {'present': 0, 'total': 0, 'percentage': 0}
                        
                        # Parse SGPA
                        if len(cells) > 2:
                            sgpa_text = cells[2].get_text(strip=True)
                            try:
                                semester_data['sgpa'] = float(sgpa_text) if sgpa_text else 0.0
                            except ValueError:
                                semester_data['sgpa'] = 0.0
                        
                        # Parse Earned Credit
                        if len(cells) > 3:
                            earned_credit_text = cells[3].get_text(strip=True)
                            try:
                                semester_data['earned_credit'] = int(earned_credit_text) if earned_credit_text else 0
                            except ValueError:
                                semester_data['earned_credit'] = 0
                        
                        # Parse Cumulative Credit
                        if len(cells) > 4:
                            cumulative_credit_text = cells[4].get_text(strip=True)
                            try:
                                semester_data['cumulative_credit'] = int(cumulative_credit_text) if cumulative_credit_text else 0
                            except ValueError:
                                semester_data['cumulative_credit'] = 0
                        
                        # Parse CGPA
                        if len(cells) > 5:
                            cgpa_text = cells[5].get_text(strip=True)
                            try:
                                semester_data['cgpa'] = float(cgpa_text) if cgpa_text else 0.0
                            except ValueError:
                                semester_data['cgpa'] = 0.0
                        
                        # Parse Result
                        if len(cells) > 6:
                            result_text = cells[6].get_text(strip=True)
                            semester_data['result'] = result_text if result_text else 'N/A'
                        else:
                            semester_data['result'] = 'N/A'
                        
                        semesters.append(semester_data)
        
        # Method 3: Alternative parsing for different page structures
        if not semesters:
            # Try to find semester data in div elements or other structures
            semester_divs = soup.find_all('div')
            for div in semester_divs:
                div_text = div.get_text(strip=True)
                
                # Look for semester pattern in div text
                for i, pattern in enumerate(semester_patterns, 1):
                    if re.search(pattern, div_text, re.IGNORECASE):
                        # Found a semester, now try to extract data from surrounding elements
                        semester_data = {
                            'semester_name': re.search(pattern, div_text, re.IGNORECASE).group(1),
                            'semester_number': i
                        }
                        
                        # Look for attendance, SGPA, CGPA patterns in the same div or nearby divs
                        attendance_match = re.search(r'Attendance:\s*(\d+)/(\d+)\s*\((\d+)%\)', div_text, re.IGNORECASE)
                        if attendance_match:
                            semester_data['attendance'] = {
                                'present': int(attendance_match.group(1)),
                                'total': int(attendance_match.group(2)),
                                'percentage': int(attendance_match.group(3))
                            }
                        
                        sgpa_match = re.search(r'SGPA:\s*([0-9.]+)', div_text, re.IGNORECASE)
                        if sgpa_match:
                            semester_data['sgpa'] = float(sgpa_match.group(1))
                        
                        cgpa_match = re.search(r'CGPA:\s*([0-9.]+)', div_text, re.IGNORECASE)
                        if cgpa_match:
                            semester_data['cgpa'] = float(cgpa_match.group(1))
                        
                        earned_credit_match = re.search(r'Earned Credit:\s*(\d+)', div_text, re.IGNORECASE)
                        if earned_credit_match:
                            semester_data['earned_credit'] = int(earned_credit_match.group(1))
                        
                        cumulative_credit_match = re.search(r'Cumulative Credit:\s*(\d+)', div_text, re.IGNORECASE)
                        if cumulative_credit_match:
                            semester_data['cumulative_credit'] = int(cumulative_credit_match.group(1))
                        
                        result_match = re.search(r'Result:\s*(\w+)', div_text, re.IGNORECASE)
                        if result_match:
                            semester_data['result'] = result_match.group(1)
                        
                        # Only add if we found some meaningful data
                        if len(semester_data) > 2:  # More than just name and number
                            semesters.append(semester_data)
                        break
        
        # Extract overall statistics if available
        overall_stats = {}
        page_text = soup.get_text()
        
        # Look for overall CGPA
        overall_cgpa_match = re.search(r'CGPA:\s*([0-9.]+)', page_text)
        if overall_cgpa_match:
            overall_stats['overall_cgpa'] = float(overall_cgpa_match.group(1))
        
        # Look for overall cumulative credit
        overall_credit_match = re.search(r'Cumulative Credit:\s*(\d+)', page_text)
        if overall_credit_match:
            overall_stats['overall_cumulative_credit'] = int(overall_credit_match.group(1))
        
        # Extract backlogs information if available
        backlogs_info = {}
        
        # Look for backlogs data
        total_backlogs_match = re.search(r'Total Backlogs[:\s]*(\d+)', page_text, re.IGNORECASE)
        if total_backlogs_match:
            backlogs_info['total_backlogs'] = int(total_backlogs_match.group(1))
        
        current_backlogs_match = re.search(r'Current Backlogs[:\s]*(\d+)', page_text, re.IGNORECASE)
        if current_backlogs_match:
            backlogs_info['current_backlogs'] = int(current_backlogs_match.group(1))
        
        return {
            'semesters': semesters,
            'overall_stats': overall_stats,
            'backlogs_info': backlogs_info
        }
        
    except Exception as e:
        print(f"Error parsing semester data: {e}")
        return {
            'semesters': [],
            'overall_stats': {},
            'backlogs_info': {},
            'error': str(e)
        }


@bp.route("/academic-analysis", methods=["GET"])
@require_token_auth
def academic_analysis():
    """
    Get comprehensive academic analysis data including semester-wise SGPA, CGPA, 
    attendance, credits, and backlogs information
    """
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.split(" ")[1] if auth_header.startswith("Bearer ") else auth_header
    
    headers = {"User-Agent": Config.USER_AGENT}
    cookie = {Config.COOKIE_KEY: token}
    
    # URL for academic analysis page
    analysis_url = f"{Config.BASE_URL}/ktuacademics/student/studentacademicsautonomous"
    
    try:
        response = requests.get(analysis_url, headers=headers, cookies=cookie)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Check if redirected to login
        if soup.find("title") and "login" in soup.find("title").text.lower():
            return jsonify({"message": "Token expired. Please login again."}), 401
        
        # Parse the academic analysis data
        analysis_data = parse_semester_data(soup)
        
        # Add metadata
        response_body = {
            "academic_analysis": analysis_data,
            "total_semesters": len(analysis_data.get('semesters', [])),
            "url_used": analysis_url,
            "timestamp": "Generated from ETLab Academic Analysis"
        }
        
        return jsonify(response_body), 200
        
    except requests.exceptions.RequestException as e:
        return jsonify({"message": f"Failed to fetch academic analysis: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"message": f"Error processing academic analysis: {str(e)}"}), 500