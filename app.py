<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Website Security Checker</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: linear-gradient(to right, #0f2027, #203a43, #2c5364);
    color: #333;
    margin: 0;
    padding: 0;
  }
  .container {
    max-width: 600px;
    background: #ffffffdd;
    padding: 30px;
    margin: 60px auto;
    border-radius: 10px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
  }
  h1 {
    text-align: center;
    color: #222;
    margin-bottom: 20px;
  }
  form {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
  }
  input[type="text"] {
    flex: 1;
    padding: 12px;
    border: 1px solid #ccc;
    border-radius: 6px;
    font-size: 1rem;
  }
  button {
    background: #28a745;
    color: white;
    border: none;
    padding: 12px 18px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 600;
    transition: background 0.3s;
  }
  button:hover {
    background: #218838;
  }
  .spinner-container {
    display: none;
    text-align: center;
    margin-bottom: 20px;
  }
  .spinner {
    border: 4px solid rgba(0,0,0,0.1);
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border-left-color: #28a745;
    animation: spin 1s linear infinite;
    display: inline-block;
    margin-bottom: 10px;
  }
  @keyframes spin {
    to { transform: rotate(360deg); }
  }
  .progress-container {
    display: none;
    width: 100%;
    background: #e0e0e0;
    border-radius: 6px;
    overflow: hidden;
    margin-bottom: 20px;
  }
  .progress-bar {
    width: 0%;
    height: 10px;
    background: #28a745;
    animation: progress 3s linear forwards;
  }
  @keyframes progress {
    to { width: 100%; }
  }
  .result-box {
    background: #1c1c1c;
    color: #0f0;
    padding: 15px;
    border-radius: 6px;
    font-family: monospace;
  }
  .result-row {
    display: flex;
    justify-content: space-between;
    margin-bottom: 5px;
  }
  .result-key {
    font-weight: bold;
  }
  .error {
    color: #f00;
  }
</style>
</head>
<body>
  <div class="container">
    <h1>🔒 Website Security Checker</h1>
    <form id="scanForm">
      <input type="text" id="websiteInput" placeholder="example.com" required>
      <button type="submit">Scan</button>
    </form>
    <div class="spinner-container">
      <div class="spinner"></div>
      <p>Scanning... Please wait.</p>
    </div>
    <div class="progress-container">
      <div class="progress-bar"></div>
    </div>
    <div class="result-box">
      <div class="result-row"><span class="result-key">HTTP Check:</span> <span id="http-status">N/A</span></div>
      <div class="result-row"><span class="result-key">HTTPS Check:</span> <span id="https-status">N/A</span></div>
      <div class="result-row"><span class="result-key">Final Landing:</span> <span id="final-status">N/A</span></div>
    </div>
  </div>

<script>
  document.getElementById("scanForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    const websiteInput = document.getElementById("websiteInput").value.trim();

    if (!websiteInput) {
      alert("Please enter a website URL!");
      return;
    }

    const domainRegex = /^(?!:\/\/)([a-zA-Z0-9-_]+\.)+[a-zA-Z]{2,}$/;
    if (!domainRegex.test(websiteInput)) {
      alert("Please enter a valid domain name, e.g., example.com");
      return;
    }

    document.querySelector('.spinner-container').style.display = 'block';
    document.querySelector('.progress-container').style.display = 'block';
    document.querySelector('.progress-bar').style.width = '0%';
    setTimeout(() => {
      document.querySelector('.progress-bar').style.width = '100%';
    }, 50);

    document.getElementById("http-status").textContent = "Loading...";
    document.getElementById("https-status").textContent = "Loading...";
    document.getElementById("final-status").textContent = "Loading...";

    try {
      const response = await fetch('https://website-scanner-backend.onrender.com/api/scan', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({website: websiteInput})
      });

      const data = await response.json();
      document.querySelector('.spinner-container').style.display = 'none';
      document.querySelector('.progress-container').style.display = 'none';

      // Parse the backend result into status codes
      const lines = (data.result || data.error || "Unknown error.").split("\n");
      let httpLine = lines[0] || "";
      let httpsLine = lines[1] || "";
      let finalLine = lines[2] || "";

      // Extract status codes from each line
      const getStatusCode = line => {
        const match = line.match(/(\d{3})/);
        return match ? match[1] : "N/A";
      };

      document.getElementById("http-status").textContent = getStatusCode(httpLine);
      document.getElementById("https-status").textContent = getStatusCode(httpsLine);
      document.getElementById("final-status").textContent = getStatusCode(finalLine);

    } catch (error) {
      console.error(error);
      alert("Error scanning website. Try again!");
      document.querySelector('.spinner-container').style.display = 'none';
      document.querySelector('.progress-container').style.display = 'none';
    }
  });
</script>
</body>
</html>
