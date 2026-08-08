"""Small Flask application that the Exercise 9 pipeline builds, tests and runs.

Local start:

    python app.py
    # or, to pick another port
    $env:PORT = "5001"; python app.py
"""

from __future__ import annotations

import os

from flask import Flask, jsonify

app = Flask(__name__)

PAGE = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>DevOps ISE - Exercise 9</title>
  </head>
  <body>
    <h1>Exercise 9 pipeline</h1>
    <p>This page is served by the application that Jenkins builds, tests and deploys.</p>
    <p><a href="/health">Health endpoint</a></p>
  </body>
</html>
"""


@app.get("/")
def index():
    """Return the landing page."""
    return PAGE


@app.get("/health")
def health():
    """Return the health probe that the pipeline polls after the deploy."""
    return jsonify(status="ok")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
