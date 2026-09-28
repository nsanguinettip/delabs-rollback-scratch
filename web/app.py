# Toy web service for the nightly-deploy rollback repros.
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

HEALTH = 500 if os.environ.get("SCRATCH_MODE") == "sick" else 200
MARK = None

os.makedirs("/data", exist_ok=True)
with open("/data/started", "w") as f:
    f.write(time.strftime("%Y-%m-%dT%H:%M:%S\n"))
if MARK:
    with open(os.path.join("/data", MARK), "w") as f:
        f.write("1\n")


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        code = {"/live": 200, "/health": HEALTH}.get(self.path, 404)
        self.send_response(code)
        self.end_headers()
        self.wfile.write(b"%d\n" % code)

    def log_message(self, *args):
        pass


HTTPServer(("0.0.0.0", 8080), H).serve_forever()
