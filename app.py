from flask import Flask, render_template_string
import subprocess
import threading
import queue

app = Flask(__name__)

log_queue = queue.Queue()
log_buffer = []

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Bot Live Logs</title>
    <meta http-equiv="refresh" content="3">
    <style>
        body { background:#0f0f0f; color:#00ff99; font-family: monospace; padding:20px; }
        pre { white-space: pre-wrap; }
    </style>
</head>
<body>
<h2>🟢 Live Bot Logs</h2>
<pre>{{ logs }}</pre>
</body>
</html>
"""

def run_bot():
    process = subprocess.Popen(
        ["python", "bot.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    for line in process.stdout:
        log_queue.put(line)

def log_collector():
    while True:
        line = log_queue.get()
        log_buffer.append(line)
        if len(log_buffer) > 500:  # limit memory
            log_buffer.pop(0)

@app.route("/")
def home():
    return render_template_string(HTML, logs="".join(log_buffer))

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    threading.Thread(target=log_collector, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)
