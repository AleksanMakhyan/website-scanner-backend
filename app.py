from flask import Flask, render_template, request
import requests
import socket
import ssl

app = Flask(__name__)

def check_http_headers(url: str) -> dict | None:
    """
    Perform a HEAD request on the given URL and return its response headers.
    Returns None if the request fails.
    """
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        return dict(response.headers)
    except Exception:
        return None

def check_common_ports(hostname: str) -> list[int]:
    """
    Try to connect to a handful of common ports on the given hostname.
    Returns a list of ports that appear to be open.
    """
    COMMON_PORTS = [21, 22, 23, 80, 443, 3306, 8080]
    open_ports: list[int] = []
    for port in COMMON_PORTS:
        try:
            sock = socket.create_connection((hostname, port), timeout=2)
            sock.close()
            open_ports.append(port)
        except Exception:
            # If connection fails or times out, treat as closed/filtered
            pass
    return open_ports

def check_ssl_certificate(url: str) -> dict | None:
    """
    If the URL begins with "https://", attempt to retrieve the SSL certificate.
    Returns a dict with issuer, subject, notAfter (expiry), or None on failure.
    """
    try:
        # Strip protocol + path to get bare hostname
        hostname = (
            url.replace("https://", "")
               .replace("http://", "")
               .split("/")[0]
        )
        ctx = ssl.create_default_context()
        # Wrap a socket to perform an SSL handshake
        with ctx.wrap_socket(socket.socket(), server_hostname=hostname) as s:
            s.settimeout(3)
            s.connect((hostname, 443))
            cert = s.getpeercert()
            # Build a simpler dict from the certificate fields:
            issuer = { item[0][0]: item[0][1] for item in cert.get("issuer", []) }
            subject = { item[0][0]: item[0][1] for item in cert.get("subject", []) }
            return {
                "issuer": issuer,
                "subject": subject,
                "notAfter": cert.get("notAfter")
            }
    except Exception:
        return None

@app.route("/", methods=["GET", "POST"])
def index():
    result: dict | None = None

    if request.method == "POST":
        raw_url = request.form.get("url", "").strip()
        if not raw_url:
            return render_template("index.html", result={"error": "Please enter a valid URL."})

        # Ensure protocol prefix
        if not raw_url.startswith(("http://", "https://")):
            target_url = "http://" + raw_url
        else:
            target_url = raw_url

        # 1) Fetch HTTP headers
        headers = check_http_headers(target_url)

        # 2) Determine hostname for port scanning
        hostname = (
            target_url.replace("https://", "")
                      .replace("http://", "")
                      .split("/")[0]
        )

        # 3) Scan common ports
        open_ports = check_common_ports(hostname)

        # 4) If HTTPS, get SSL certificate info
        ssl_info = None
        if target_url.lower().startswith("https://"):
            ssl_info = check_ssl_certificate(target_url)

        result = {
            "url": target_url,
            "headers": headers,
            "open_ports": open_ports,
            "ssl_info": ssl_info
        }

    return render_template("index.html", result=result)

if __name__ == "__main__":
    # Run in debug mode for development. In production, disable debug=True.
    app.run(host="0.0.0.0", port=5000, debug=True)
