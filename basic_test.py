from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/test")
def test():
    return jsonify({"message": "Test successful"})

if __name__ == "__main__":
    print("Starting basic test server...")
    app.run(host="127.0.0.1", port=5001, debug=False)