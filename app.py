from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

@app.route("/", methods=["GET"])
def home():
    return "✅ Backend is running!"

@app.route("/api/scan", methods=["POST"])
def scan():
    data = request.get_json()
    website = data.get("website")
    if not website:
        return jsonify({"error": "Missing website parameter"}), 400

    try:
        # Prepend http:// if not included
        if not website.startswith(("http://", "https://")):
            website = f"http://{website}"

        response = requests.get(website, timeout=5)
        if response.status_code == 200:
            return jsonify({"result": f"{website} is up and running!"})
        else:
            return jsonify({"result": f"{website} responded with status code: {response.status_code}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
