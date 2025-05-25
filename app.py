from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess

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
        result = subprocess.check_output(["nmap", "-Pn", website], stderr=subprocess.STDOUT, text=True, timeout=30)
        return jsonify({"result": result})
    except subprocess.CalledProcessError as e:
        return jsonify({"error": e.output}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
