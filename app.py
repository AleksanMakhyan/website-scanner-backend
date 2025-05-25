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

    domain = website.replace("http://", "").replace("https://", "").strip("/")
    base_http = f"http://{domain}"
    base_https = f"https://{domain}"

    # Initialize status codes and final URL
    status_http = "N/A"
    status_https = "N/A"
    status_final = "N/A"
    final_url = "N/A"

    try:
        # HTTP check
        response_http = requests.get(base_http, timeout=5, allow_redirects=False)
        status_http = response_http.status_code

        if status_http == 200:
            # Homepage found!
            final_url = base_http
            status_final = status_http
            return jsonify({
                "status": "Completed",
                "status_http": str(status_http),
                "status_https": "N/A",
                "status_final": str(status_final),
                "final_url": final_url
            })

        elif 300 <= status_http < 310:
            # Check HTTPS
            try:
                response_https = requests.get(base_https, timeout=5, allow_redirects=False)
                status_https = response_https.status_code

                if status_https == 200:
                    # HTTPS homepage found!
                    final_url = base_https
                    status_final = status_https
                    return jsonify({
                        "status": "Completed",
                        "status_http": str(status_http),
                        "status_https": str(status_https),
                        "status_final": str(status_final),
                        "final_url": final_url
                    })

                elif 300 <= status_https < 310:
                    # Follow HTTPS redirects to final URL
                    try:
                        response_final = requests.get(base_https, timeout=5, allow_redirects=True)
                        final_url = response_final.url
                        status_final = response_final.status_code
                    except requests.exceptions.RequestException:
                        final_url = "Website does not exist 😔"
                        status_final = "N/A"
                else:
                    final_url = "Website does not exist 😔"
            except requests.exceptions.RequestException:
                final_url = "Website does not exist 😔"
        else:
            final_url = "Website does not exist 😔"

    except requests.exceptions.RequestException:
        final_url = "Website does not exist 😔"

    return jsonify({
        "status": "Completed",
        "status_http": str(status_http),
        "status_https": str(status_https),
        "status_final": str(status_final),
        "final_url": final_url
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
