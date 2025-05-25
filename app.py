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

    # Remove schemes
    domain = website.replace("http://", "").replace("https://", "").strip("/")
    base_http = f"http://{domain}"
    base_https = f"https://{domain}"

    message_lines = []

    try:
        # 1️⃣ HTTP Check
        response_http = requests.get(base_http, timeout=5, allow_redirects=False)
        status_http = response_http.status_code

        if status_http == 200:
            message_lines.append(f"{base_http} is up!")
            message_lines.extend(["", ""])
            return jsonify({"result": "\n".join(message_lines)})
        elif 300 <= status_http < 310:
            message_lines.append(f"{base_http} is a redirect.")
            # 2️⃣ HTTPS Check without following redirects
            try:
                response_https = requests.get(base_https, timeout=5, allow_redirects=False)
                status_https = response_https.status_code

                if status_https == 200:
                    message_lines.append(f"{base_https} is up!")
                elif 300 <= status_https < 310:
                    message_lines.append(f"{base_https} is a redirect.")
                else:
                    message_lines.append("Website does not exist 😔")

                # 3️⃣ Follow HTTPS redirects to final landing page
                try:
                    response_final = requests.get(base_https, timeout=5, allow_redirects=True)
                    final_url = response_final.url
                    final_status = response_final.status_code

                    if final_status == 200:
                        message_lines.append(f"{final_url} is up!")
                    elif final_status == 404:
                        message_lines.append(f"{final_url} Page wasn't found 😔")
                    else:
                        message_lines.append("Website does not exist 😔")
                except requests.exceptions.RequestException:
                    message_lines.append("Website does not exist 😔")
            except requests.exceptions.RequestException:
                message_lines.append("Website does not exist 😔")
                message_lines.append("Website does not exist 😔")
        else:
            message_lines.append("Website does not exist 😔")
            message_lines.extend(["", ""])
            return jsonify({"result": "\n".join(message_lines)})

    except requests.exceptions.RequestException:
        message_lines.append("Website does not exist 😔")
        message_lines.extend(["", ""])
        return jsonify({"result": "\n".join(message_lines)})

    # Fill to 3 lines
    while len(message_lines) < 3:
        message_lines.append("")

    return jsonify({"result": "\n".join(message_lines)})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
