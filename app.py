from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from urllib.parse import urlparse

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

    # Prepend http:// if not included
    if not website.startswith(("http://", "https://")):
        website = f"http://{website}"

    try:
        response = requests.get(website, timeout=5)

        # Extract the domain name for a user-friendly output
        parsed_url = urlparse(website)
        domain = parsed_url.hostname or website
        friendly_name = domain.split('.')[0].capitalize()

        if response.status_code == 200:
            return jsonify({"result": f"{friendly_name} is up and running!"})
        else:
            return jsonify({"result": f"{friendly_name} responded with status code: {response.status_code}"})

    except requests.exceptions.RequestException:
        return jsonify({"error": "Website was not found 😔"}), 404
    except Exception:
        return jsonify({"error": "Website was not found 😔"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
