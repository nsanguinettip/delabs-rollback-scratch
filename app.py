import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

VERSION = "v1"
MODE = "ok"  # ok | bad | healthfail


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body):
        data = body.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/healthz":
            if MODE == "healthfail":
                return self._send(500, "unhealthy")
            return self._send(200, "ok")
        if MODE == "bad":
            return self._send(500, "bad")
        try:
            with open("/app/flavor.txt") as fh:
                flavor = fh.read()
        except OSError:
            flavor = "missing"
        body = "pb-scratch %s flavor=%s flag=%s dotenv=%s" % (
            VERSION,
            flavor,
            os.environ.get("SCRATCH_FLAG", ""),
            os.environ.get("DOTENV_VALUE", ""),
        )
        return self._send(200, body)

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
