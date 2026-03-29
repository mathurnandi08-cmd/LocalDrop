#!/usr/bin/env python3
print("🚀 LocalDrop ULTRA Starting...")

import socket
import threading
from pathlib import Path

from flask import Flask, request, jsonify
import qrcode

# ── CONFIG ─────────────────────────────
PORT = 5000
PASSWORD = "1234"   # 🔐 change this

# ── STORAGE (D DRIVE FIX) ──────────────
if Path("D:/").exists():
    UPLOAD_DIR = Path("D:/LocalDrop")
else:
    UPLOAD_DIR = Path.home() / "Desktop" / "LocalDrop"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ── HELPERS ────────────────────────────
def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def show_qr(url):
    img = qrcode.make(url)
    img.save("qr.png")
    try:
        img.show()
    except:
        pass

# ── APP ────────────────────────────────
app = Flask(__name__)

# ── UI ─────────────────────────────────
HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LocalDrop ULTRA</title>

<style>
body{background:#0b0f1a;color:white;text-align:center;font-family:sans-serif}
.box{border:2px dashed cyan;padding:40px;margin:20px;border-radius:15px}
button{padding:15px;background:cyan;border:none;border-radius:10px;font-weight:bold}
input{padding:10px;border-radius:8px;border:none}
</style>
</head>

<body>

<h2>📡 LocalDrop ULTRA</h2>

<input type="password" id="pass" placeholder="Enter Password"><br><br>

<div class="box">
<input type="file" id="fileInput" multiple>
</div>

<button onclick="upload()">Send</button>

<p id="status"></p>

<script>
function upload(){
 let pass = document.getElementById("pass").value;
 let files = document.getElementById("fileInput").files;

 if(pass === ""){
  alert("Enter password!");
  return;
 }

 if(files.length === 0){
  alert("Select file!");
  return;
 }

 let fd = new FormData();
 fd.append("password", pass);

 for(let f of files){
  fd.append("files", f);
 }

 let xhr = new XMLHttpRequest();
 xhr.open("POST","/upload");

 xhr.upload.onprogress = function(e){
  if(e.lengthComputable){
   let p = Math.round((e.loaded/e.total)*100);
   document.getElementById("status").innerText = "Uploading: "+p+"%";
  }
 };

 xhr.onload = function(){
  if(xhr.status === 200){
   let res = JSON.parse(xhr.responseText);
   document.getElementById("status").innerText =
    res.saved + " file uploaded ✅";
  }else{
   document.getElementById("status").innerText = "Wrong password ❌";
  }
 };

 xhr.send(fd);
}
</script>

</body>
</html>
"""

# ── ROUTES ─────────────────────────────
@app.route("/")
def home():
    return HTML

@app.route("/upload", methods=["POST"])
def upload():
    if request.form.get("password") != PASSWORD:
        return jsonify({"error":"wrong password"}), 403

    files = request.files.getlist("files")
    saved = 0

    for f in files:
        name = Path(f.filename).name
        path = UPLOAD_DIR / name

        i = 1
        while path.exists():
            path = UPLOAD_DIR / f"{Path(name).stem}_{i}{Path(name).suffix}"
            i += 1

        f.save(path)
        saved += 1

    return jsonify({"saved": saved})

# ── MAIN ──────────────────────────────
def main():
    ip = get_ip()
    url = f"http://{ip}:{PORT}"

    print("=================================")
    print("🚀 LocalDrop ULTRA Running")
    print("🌐 URL:", url)
    print("📂 Save Location:", UPLOAD_DIR)
    print("🔐 Password:", PASSWORD)
    print("=================================")

    threading.Timer(1, show_qr, args=[url]).start()

    app.run(host="0.0.0.0", port=PORT)

if __name__ == "__main__":
    main()