"""Front end for Exercise 4.

It renders the rate table it gets from the backend container. The backend is
addressed by its container name, which only resolves because both containers sit
on the same user-defined network.
"""

import html
import json
import os
import urllib.request

from flask import Flask, Response

BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:8000").rstrip("/")
REQUEST_TIMEOUT_SECONDS = 3

app = Flask(__name__)


def fetch_rate_table():
    """Return the parsed JSON from the backend, or raise if it is unreachable."""
    with urllib.request.urlopen(
        f"{BACKEND_URL}/rates", timeout=REQUEST_TIMEOUT_SECONDS
    ) as response:
        return json.loads(response.read().decode("utf-8"))


def render_table(payload):
    rows = "".join(
        f"      <tr><td>{html.escape(str(code))}</td>"
        f"<td>{html.escape(str(rate))}</td></tr>\n"
        for code, rate in sorted(payload.get("rates", {}).items())
    )
    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        '<head><meta charset="utf-8"><title>exchange rates</title></head>\n'
        "<body>\n"
        "  <h1>Exchange rates</h1>\n"
        f"  <p>Base currency: {html.escape(str(payload.get('base', 'unknown')))}</p>\n"
        f"  <p>Source: {html.escape(str(payload.get('source', 'unknown')))}</p>\n"
        "  <table border=\"1\">\n"
        "    <tr><th>Currency</th><th>Rate</th></tr>\n"
        f"{rows}"
        "  </table>\n"
        f"  <p>Fetched from {html.escape(BACKEND_URL)}/rates</p>\n"
        "</body>\n"
        "</html>\n"
    )


@app.get("/")
def index():
    try:
        payload = fetch_rate_table()
    except (OSError, ValueError):
        return Response(
            "<!doctype html>\n"
            '<html lang="en"><head><meta charset="utf-8">'
            "<title>rates unavailable</title></head>\n"
            "<body><h1>503 - rate backend unavailable</h1>\n"
            f"<p>Could not reach {html.escape(BACKEND_URL)}/rates within "
            f"{REQUEST_TIMEOUT_SECONDS} seconds.</p></body></html>\n",
            status=503,
            mimetype="text/html",
        )
    return Response(render_table(payload), status=200, mimetype="text/html")


@app.get("/health")
def health():
    """Reports only on this process; the backend is checked by the page itself."""
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
