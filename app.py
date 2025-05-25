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

    # Remove any scheme (http/https) from input
    domain = website.replace("http://", "").replace("https://", "").strip("/")
    base_url_http = f"http://{domain}"
    base_url_https = f"https://{domain}"

    final_url = None
    message_lines = []

    try:
        # Start with HTTP
        response = requests.get(base_url_http, timeout=5, allow_redirects=True)
        final_url = response.url
        status_code = response.status_code

        if 200 <= status_code < 300:
            # HTTP landing page directly
            message_lines.append(f"✅ {base_url_http} is up with status 200!")
        elif 300 <= status_code < 310:
            # HTTP redirected, check HTTPS
            message_lines.append(f"🔄 HTTP redirected with status {status_code}. Checking HTTPS...")

            # Check HTTPS
            response_https = requests.get(base_url_https, timeout=5, allow_redirects=True)
            final_url = response_https.url
            status_code_https = response_https.status_code

            if 200 <= status_code_https < 300:
                message_lines.append(f"✅ {final_url} (HTTPS) is up with status 200!")
            elif 300 <= status_code_https < 310:
                message_lines.append(f"🔄 HTTPS redirected further with status {status_code_https}. Final URL: {response_https.url}")
            else:
                return jsonify({"error": "Website was not found 😔"}), 404
        else:
            return jsonify({"error": "Website was not found 😔"}), 404

        # Check for random-looking paths
        parsed_final = urlparse(final_url)
        path = parsed_final.path.strip("/")
        if path and len(path) > 10:  # Random long path check
            message_lines.append("⚠️ Final URL seems to contain random letters, not a homepage.")

        # Limit to 3 lines
        message_lines = message_lines[:3]
        return jsonify({"result": "\n".join(message_lines)})

    except requests.exceptions.RequestException:
        return jsonify({"error": "Website was not found 😔"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
