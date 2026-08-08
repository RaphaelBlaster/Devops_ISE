"""Flask service used as the Kubernetes workload for Exercise 2.

The page-view counter lives in process memory, so every pod counts on its own.
That is intentional: it makes it visible that the Service spreads traffic over
more than one pod.
"""

import os

from flask import Flask

SERVICE_NAME = "flask-app"

app = Flask(__name__)

_page_views = 0


@app.get("/")
def index():
    """Render the service name and the number of page views this process served."""
    global _page_views
    _page_views += 1
    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        '<head><meta charset="utf-8"><title>flask-app</title></head>\n'
        "<body>\n"
        f"  <h1>Service: {SERVICE_NAME}</h1>\n"
        f"  <p>Page views served by this pod: {_page_views}</p>\n"
        "</body>\n"
        "</html>\n"
    )


@app.get("/health")
def health():
    """Readiness endpoint. It stays cheap because Kubernetes polls it often."""
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
