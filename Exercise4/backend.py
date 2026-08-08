"""Currency rate backend for Exercise 4.

Standard library only: the container needs no third-party package for this
process. It is reachable only on the user-defined Docker network, under the name
`backend`, on port 8000.
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# Fixed table so the demo output is stable and does not depend on the internet.
RATE_TABLE = {
    "base": "USD",
    "rates": {
        "EUR": 0.92,
        "GBP": 0.79,
        "INR": 83.12,
    },
    "source": "fixed table",
}


class RateHandler(BaseHTTPRequestHandler):
    """Serve the rate table and a health endpoint, nothing else."""

    server_version = "rate-backend/1.0"

    def do_GET(self):
        if self.path.rstrip("/") == "/rates":
            self._send_json(200, RATE_TABLE)
        elif self.path.rstrip("/") == "/health":
            self._send_json(200, {"status": "ok"})
        else:
            self._send_json(404, {"error": "not found", "path": self.path})

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"[backend] {self.address_string()} {fmt % args}", flush=True)


def main():
    port = int(os.environ.get("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), RateHandler)
    print(f"[backend] listening on 0.0.0.0:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("[backend] stopping", flush=True)
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
