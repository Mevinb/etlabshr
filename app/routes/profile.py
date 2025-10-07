import requests
from bs4 import BeautifulSoup
from flasgger import swag_from
from flask import Blueprint, jsonify, request

from app.docs.swagger import swagger_profile_spec
from app.utils.token_required import require_token_auth
from config import Config

bp = Blueprint("profile", __name__, url_prefix="/api")


@bp.route("/profile", methods=["GET"])
@require_token_auth
@swag_from(swagger_profile_spec)
def profile():
    headers = {
        "User-Agent": Config.USER_AGENT,
    }
    cookie = {Config.COOKIE_KEY: request.headers["Authorization"]}
    response = requests.get(
        f"{Config.BASE_URL}/student/profile",
        headers=headers,
        cookies=cookie,
    )
    soup = BeautifulSoup(response.text, "html.parser")
    title = soup.find("title")
    if title and "login" in title.text.lower():
        return jsonify({"message": "Token expired. Please login again."}), 401

    name = soup.find("th", string="Name").find_next("td").get_text(strip=True)
    dob = soup.find("th", string="Date of Birth").find_next("td").get_text(strip=True)
    admission_no = (
        soup.find("th", string="Admission No").find_next("td").get_text(strip=True)
    )
    university_roll_no = (
        soup.find("th", string="University Reg No").find_next("td").get_text(strip=True)
    )

    # Return profile data at root level for test compatibility
    return jsonify({
        "name": name,
        "dob": dob,
        "admission_no": admission_no,
        "university_reg_no": university_roll_no,
        "message": "Successfully fetched data"
    }), 200
