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

    # Remove any scheme from input
    domain = website.replace("http://", "").replace("https://", "").strip("/")
    base_url_http = f"http://{domain}"
    base_url_https = f"https://{domain}"

    message_lines = []

    try:
        # Check HTTP status without following redirects
        response_http = requests.get(base_url_http, timeout=5, allow_redirects=False)
        status_code_http = response_http.status_code

        if status_code_http == 200:
            message_lines.append(f"{base_url_http} is up!")
        elif 300 <= status_code_http < 310:
            message_lines.append(f"{base_url_http} is a redirect.")
            # Check HTTPS status if HTTP is a redirect
            try:
                response_https = requests.get(base_url_https, timeout=5, allow_redirects=False)
                status_code_https = response_https.status_code

                if status_code_https == 200:
                    message_lines.append(f"{base_url_https} is up!")
                else:
                    message_lines.append("Website does not exist 😔")
            except requests.exceptions.RequestException:
                message_lines.append("Website does not exist 😔")
        else:
            message_lines.append("Website does not exist 😔")

    except requests.exceptions.RequestException:
        message_lines.append("Website does not exist 😔")

    # Ensure exactly 3 lines in the output for the frontend
    while len(message_lines) < 3:
        message_lines.append("")

    return jsonify({"result": "\n".join(message_lines)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
