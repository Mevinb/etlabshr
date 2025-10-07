import requests
from bs4 import BeautifulSoup
from flask import Blueprint, jsonify, request

from config import Config

bp = Blueprint("login", __name__, url_prefix="/api")
session = requests.Session()


@bp.route("/login", methods=["POST"])
def login():
    try:
        body = request.get_json()
        username = body.get("username")
        password = body.get("password")

        if not username or not password:
            return jsonify({"message": "Username and password is required"}), 401

        payload = {
            "LoginForm[username]": username,
            "LoginForm[password]": password,
            "yt0": "",
        }

        headers = {
            "User-Agent": Config.USER_AGENT,
            "Content-Type": "application/x-www-form-urlencoded",
        }

        response = session.post(
            f"{Config.BASE_URL}/user/login", data=payload, headers=headers
        )
        
        soup = BeautifulSoup(response.text, "html.parser")
        title = soup.find("title")
        if title and "login" in title.text.lower():
            return jsonify({"message": "Invalid username or password"}), 401
        
        cookies = session.cookies.get_dict()
        
        if Config.COOKIE_KEY not in cookies:
            return jsonify({"message": "Login failed - no session cookie"}), 401
            
        cookie = cookies[Config.COOKIE_KEY]
        return jsonify({"message": "Login successful", "token": cookie}), 200
        
    except Exception as e:
        return jsonify({"message": "Internal server error"}), 500
