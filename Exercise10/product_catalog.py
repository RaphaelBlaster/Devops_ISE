"""Product catalog service for Exercise 10.

Read-only service: it exposes a fixed catalog over HTTP so that the cart service
has something to talk about and so that a readiness probe has an endpoint to
poll.

Run it locally:

    $env:PORT = "8080"; python product_catalog.py
"""

from __future__ import annotations

import os

from flask import Flask, jsonify

app = Flask(__name__)

# The catalog is static on purpose. It is the part of the exercise that never
# changes, which makes it easy to tell a catalog pod apart from a cart pod.
PRODUCTS = [
    {"id": 1, "name": "Mechanical keyboard", "price": 89.90},
    {"id": 2, "name": "USB-C dock", "price": 64.50},
    {"id": 3, "name": "27 inch monitor", "price": 219.00},
    {"id": 4, "name": "Laptop stand", "price": 32.75},
]


@app.get("/products")
def products():
    """Return the whole catalog as JSON."""
    return jsonify(products=PRODUCTS, count=len(PRODUCTS))


@app.get("/products/<int:product_id>")
def product(product_id: int):
    """Return one product, or 404 when the id is not in the catalog."""
    for item in PRODUCTS:
        if item["id"] == product_id:
            return jsonify(item)
    return jsonify(error="product not found", id=product_id), 404


@app.get("/health")
def health():
    """Readiness and liveness endpoint used by the deployment probes."""
    return jsonify(status="ok")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
