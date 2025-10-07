import requests
from bs4 import BeautifulSoup
from flask import Blueprint, jsonify, request

from app.utils.token_required import require_token_auth
from config import Config

bp = Blueprint("profile", __name__, url_prefix="/api")


@bp.route("/profile", methods=["GET"])
@require_token_auth
def profile():
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
        f"{Config.BASE_URL}/student/profile",
        headers=headers,
        cookies=cookie,
    )
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("title")
    if title and "login" in title.text.lower():
        return jsonify({"message": "Token expired. Please login again."}), 401

    # Extract comprehensive profile data
    profile_data = {}
    
    # Find all th-td pairs across the entire page for comprehensive data extraction
    all_th_elements = soup.find_all("th")
    
    for th in all_th_elements:
        label = th.get_text().strip()
        if label:
            # Try to find the corresponding value
            next_td = th.find_next("td")
            if next_td:
                value = next_td.get_text().strip()
                # Only include non-empty values and skip "No ... added" entries
                if value and not (value.startswith("No ") and "added" in value):
                    # Clean up the label (remove colons, extra spaces)
                    clean_label = label.replace(":", "").strip()
                    profile_data[clean_label] = value
    
    # Organize the data into logical sections
    organized_profile = {
        "personal_info": {},
        "academic_info": {},
        "contact_info": {},
        "family_info": {},
        "address_info": {},
        "financial_info": {},
        "identification": {},
        "achievements": {},
        "additional_info": {}
    }
    
    # Map fields to appropriate sections
    field_mapping = {
        "personal_info": [
            "Name", "Gender", "Date of Birth", "Religion", "Place of Birth", 
            "Mother Tongue", "Nationality", "Caste", "Blood Group"
        ],
        "academic_info": [
            "Admission No", "University Reg No", "SR No", "ABC_ID", "Aadhaar No",
            "is Hosteler?", "College Email Id", "Boarding Point"
        ],
        "contact_info": [
            "Email", "Mobile No", "Father's Mobile No", "Mother's Mobile No"
        ],
        "family_info": [
            "Father's Name", "Mother Name", "Father's Occupation", 
            "Mother's Occupation", "Annual income"
        ],
        "address_info": [
            "House Name", "Street", "Post / Street 2", "District", "PIN", "State"
        ],
        "financial_info": [
            "Bank Name", "Branch", "Account no", "IFSC Code"
        ],
        "identification": [
            "Personal Marks of identification 1", "Personal Marks of identification 2"
        ]
    }
    
    # Organize fields into sections
    for section, fields in field_mapping.items():
        for field in fields:
            if field in profile_data:
                organized_profile[section][field] = profile_data[field]
    
    # Add any remaining fields to additional_info
    used_fields = set()
    for section_fields in field_mapping.values():
        used_fields.update(section_fields)
    
    for field, value in profile_data.items():
        if field not in used_fields:
            organized_profile["additional_info"][field] = value
    
    # Add summary information
    organized_profile["summary"] = {
        "total_fields": len(profile_data),
        "sections_with_data": sum(1 for section in organized_profile.values() if isinstance(section, dict) and section),
        "message": "Successfully fetched comprehensive profile data"
    }
    
    # Return the organized profile data
    return jsonify(organized_profile), 200
