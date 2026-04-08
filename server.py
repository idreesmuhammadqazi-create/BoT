import subprocess, threading, os, sys, json
from flask import Flask, request, jsonify, Response, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)
UPLOAD_FOLDER = "/tmp/bot_uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

state = {"running": False, "progress": 0, "total": 0, "log": [], "done": False, "error": None}

def run_upload(token, nick, channel, filepath):
    global state
    state = {"running": True, "progress": 0, "total": 0, "log": [], "done": False, "error": None}

    try:
        proc = subprocess.Popen(
            [sys.executable, "upload_run.py", token, nick, channel, filepath],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        for line in proc.stdout:
            line = line.strip()
            if line.startswith("CHUNKS:"):
                state["total"] = int(line.split(":")[1])
                state["log"].append(f"File ready — {state['total']} chunks")
            elif line.startswith("PROGRESS:"):
                state["progress"] = int(line.split(":")[1])
            elif line == "DONE":
                state["done"] = True
                state["log"].append("Upload complete! 🍌")
            else:
                state["log"].append(line)
        proc.wait()
    except Exception as e:
        state["error"] = str(e)
        state["log"].append(f"ERROR: {e}")
    finally:
        state["running"] = False
        try: os.remove(filepath)
        except: pass

@app.route("/")
def index():
    return send_file("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    if state["running"]:
        return jsonify({"error": "Upload already in progress"}), 409
    token   = request.form.get("token", "").strip()
    nick    = request.form.get("nick", "").strip()
    channel = request.form.get("channel", "").strip()
    file    = request.files.get("file")
    if not all([token, nick, channel, file]):
        return jsonify({"error": "Missing fields"}), 400
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    threading.Thread(target=run_upload, args=(token, nick, channel, filepath), daemon=True).start()
    return jsonify({"ok": True})

@app.route("/status")
def status():
    return jsonify(state)

@app.route("/cancel", methods=["POST"])
def cancel():
    state["running"] = False
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
