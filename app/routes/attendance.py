import re

import requests
from bs4 import BeautifulSoup
from flask import Blueprint, jsonify, request

from app.utils.token_required import require_token_auth
from config import Config

bp = Blueprint("attendance", __name__, url_prefix="/api")


@bp.route("/attendance", methods=["GET"])
@require_token_auth
def attendance():
    # Note: ETLab attendance shows current semester subjects only
    # The semester parameter is kept for API consistency but attendance
    # is always for the current active semester
    semester = request.args.get("semester")
    
    # Extract token from Authorization header (format: "Bearer <token>")
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
    else:
        token = auth_header

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
    # Note: ETLab attendance endpoint shows current semester only regardless of parameter
    # Using current semester (defaulting to 5 if no semester specified)
    current_semester = semester if semester else 5
    response = requests.get(
        f"{Config.BASE_URL}/ktuacademics/student/viewattendancesubject/{current_semester}",
        headers=headers,
        cookies=cookie,
    )
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("title")
    if title and "login" in title.text.lower():
        return jsonify({"message": "Token expired. Please login again."}), 401

    response_body = {}
    table = soup.find("table", class_="items")
    table_headers = table.find_all("th")
    table_data = table.find_all("td")

    response_body["university_reg_no"] = table_data[0].text
    response_body["roll_no"] = table_data[1].text
    response_body["name"] = table_data[2].text

    for i in range(3, len(table_data) - 2):
        subject_code = table_headers[i].text.strip()
        attendance_str = table_data[i].text.strip()
        present_hours = attendance_str.split("/")[0].strip()
        total_hours = attendance_str.split("/")[1].split("(")[0].strip()
        attendance_percentage = re.search(r"\((.*?)\)", attendance_str).group(1).strip()

        subject_attendance = {}
        subject_attendance["present_hours"] = present_hours
        subject_attendance["total_hours"] = total_hours
        subject_attendance["attendance_percentage"] = attendance_percentage

        response_body[subject_code] = subject_attendance

    response_body["total_present_hours"] = (
        table_data[len(table_data) - 2].text.split("/")[0].strip()
    )
    response_body["total_hours"] = (
        table_data[len(table_data) - 2].text.split("/")[1].strip()
    )
    response_body["total_perecentage"] = table_data[len(table_data) - 1].text
    response_body["note"] = "ETLab attendance displays current semester subjects only, not filtered by requested semester"

    return jsonify(response_body), 200
