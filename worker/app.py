# Toy worker for the nightly-deploy rollback repros; v2 drops the greenlet install (ImportError at boot).
import greenlet  # noqa: F401
import os, sys
if os.environ.get("SCRATCH_MODE") == "crash":
    sys.exit("SCRATCH_MODE=crash: exiting at boot")
from http.server import BaseHTTPRequestHandler, HTTPServer


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok\n")

    def log_message(self, *args):
        pass


HTTPServer(("0.0.0.0", 8000), H).serve_forever()
