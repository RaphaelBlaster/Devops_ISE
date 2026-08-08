"""Shopping cart service for Exercise 10.

The cart is kept in process memory. Every pod therefore owns a private cart, and
the contents are lost when the pod restarts. That is intentional: the exercise is
about placing the pods, not about durable storage.

Run it locally:

    $env:PORT = "8080"; python shopping_cart.py
"""

from __future__ import annotations

import os
import threading

from flask import Flask, jsonify, request

app = Flask(__name__)

# A lock is needed because Flask serves requests from several threads, and a
# list append plus a read of the length is not atomic on its own.
_lock = threading.Lock()
_items: list[dict] = []


def snapshot() -> dict:
    """Return a copy of the cart so the caller cannot mutate the stored list."""
    with _lock:
        items = [dict(item) for item in _items]
    return {"items": items, "count": len(items)}


@app.get("/cart")
def get_cart():
    """Return every line in the cart plus the number of lines."""
    return jsonify(snapshot())


@app.post("/cart")
def add_to_cart():
    """Append one line to the cart.

    Body: {"id": 3, "name": "27 inch monitor", "quantity": 2}
    """
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify(error="body must be a JSON object"), 400

    missing = [field for field in ("id", "name", "quantity") if field not in payload]
    if missing:
        return jsonify(error="missing fields", fields=missing), 400

    quantity = payload["quantity"]
    if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity < 1:
        return jsonify(error="quantity must be a positive integer"), 400

    line = {
        "id": payload["id"],
        "name": str(payload["name"]),
        "quantity": quantity,
    }
    with _lock:
        _items.append(line)
        count = len(_items)

    body = snapshot()
    body["added"] = line
    return jsonify(body), 201


@app.delete("/cart/<int:item_id>")
def remove_from_cart(item_id: int):
    """Remove every line whose id matches, and report how many were removed."""
    with _lock:
        before = len(_items)
        _items[:] = [item for item in _items if item["id"] != item_id]
        removed = before - len(_items)

    if removed == 0:
        return jsonify(error="id not in cart", id=item_id), 404

    body = snapshot()
    body["removed"] = removed
    return jsonify(body)


@app.delete("/cart")
def clear_cart():
    """Empty the cart. Handy when checking the reset behaviour after a restart."""
    with _lock:
        _items.clear()
    return jsonify(snapshot())


@app.get("/health")
def health():
    """Readiness and liveness endpoint used by the deployment probes."""
    return jsonify(status="ok")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
