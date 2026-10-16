"""bg-scratch: synthetic fixture of the ZeroDowntime v1 rehearsal (WF ZeroDowntime v1, Step 6).

Stdlib only. It mimics the one delabs-landing trait the blue/green controller must survive: every
request is recorded in a SQLite file (WAL, busy_timeout 5000) that BOTH colors open at the same time.
VERSION, MODE and FLIP_AFTER are the only lines a branch changes.
"""
import os
import sqlite3
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = "flip"
MODE = "flip"          # ok | bad | userr | slow | healthfail | flip | lateerr
FLIP_AFTER = 120     # seconds of process age after which MODE=flip answers 500 everywhere

DB_PATH = os.environ.get("BGS_DB", "/data/app.db")
FLAG_PATH = os.environ.get("BGS_FLAG", "/data/lateerr.flag")   # MODE=lateerr: "/" answers 500 once it exists
PORT = int(os.environ.get("BGS_PORT", "8080"))
STARTED = time.time()
LOCK = threading.Lock()
CONN = None


def log(msg):
    print(msg, file=sys.stderr, flush=True)


def db():
    global CONN
    if CONN is None:
        CONN = sqlite3.connect(DB_PATH, timeout=5, check_same_thread=False)
        CONN.execute("PRAGMA journal_mode=WAL")
        CONN.execute("PRAGMA busy_timeout=5000")
        CONN.execute("PRAGMA synchronous=NORMAL")   # WAL + NORMAL: no fsync per request (a serialized fsync made the rig the bottleneck under disk pressure)
        CONN.execute("CREATE TABLE IF NOT EXISTS hits (ts REAL, path TEXT, version TEXT, user_agent TEXT)")
        CONN.commit()
    return CONN


def record(path, ua):
    try:
        with LOCK:
            c = db()
            c.execute("INSERT INTO hits VALUES (?, ?, ?, ?)", (time.time(), path, VERSION, ua))
            c.commit()
    except Exception as e:  # a recording failure never changes the answer, it is logged
        log("record failed: %s" % e)


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        pass

    def send(self, code, body):
        data = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/healthz":
            if MODE == "healthfail" or (MODE == "flip" and time.time() - STARTED > FLIP_AFTER):
                return self.send(500, "unhealthy")
            return self.send(200, "ok")
        record(path, self.headers.get("User-Agent", ""))
        if MODE == "flip" and time.time() - STARTED > FLIP_AFTER:
            return self.send(500, "flipped")
        if path == "/":
            if MODE == "bad":
                return self.send(500, "bad")
            if MODE == "lateerr" and os.path.exists(FLAG_PATH):
                return self.send(500, "late error")
            if MODE == "slow":
                time.sleep(1.5)
            return self.send(200, "<html><body>bg-scratch %s</body></html>" % VERSION)
        if path.startswith("/app/"):
            if MODE == "userr":
                return self.send(500, "userr")
            return self.send(200, "app %s" % VERSION)
        return self.send(404, "not found")


if __name__ == "__main__":
    db()
    ThreadingHTTPServer(("0.0.0.0", PORT), H).serve_forever()
