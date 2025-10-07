from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route("/api/login", methods=["POST"])
def test_login():
    body = request.get_json()
    username = body.get("username")
    password = body.get("password")
    
    if not username or not password:
        return jsonify({"message": "Username and password is required"}), 401
    
    # For testing, just return success
    return jsonify({"message": "Login successful", "token": "test_token"}), 200

if __name__ == "__main__":
    print("Starting minimal test server...")
    app.run(host="127.0.0.1", port=5000, debug=True)