from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

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

    # Remove any scheme (http/https) from input
    domain = website.replace("http://", "").replace("https://", "").strip("/")

    try:
        # Try HTTPS first
        response = requests.get(f"https://{domain}", timeout=5)
        return jsonify({"result": f"https://{domain} is up!"})
    except requests.exceptions.RequestException:
        # If HTTPS fails, try HTTP
        try:
            response = requests.get(f"http://{domain}", timeout=5)
            return jsonify({"result": f"http://{domain} is up!"})
        except requests.exceptions.RequestException:
            return jsonify({"error": "Website was not found 😔"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
