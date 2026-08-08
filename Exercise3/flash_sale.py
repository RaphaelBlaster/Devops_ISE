"""Flash sale service for Exercise 3.

Every page view claims one unit of stock. The stock counter and the request
counter live in process memory, so each pod of the ReplicaSet keeps its own
numbers. Scaling the ReplicaSet therefore adds independent stock pools, which is
the behaviour this exercise is meant to show.
"""

import os

from flask import Flask

ITEM_NAME = "Limited edition mechanical keyboard"

app = Flask(__name__)

_starting_stock = int(os.environ.get("STOCK", "100"))
_remaining_stock = _starting_stock
_requests = 0


@app.get("/")
def index():
    """Claim one unit of stock and render the sale status."""
    global _remaining_stock, _requests
    _requests += 1
    if _remaining_stock > 0:
        _remaining_stock -= 1

    status = "in stock" if _remaining_stock > 0 else "sold out"
    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        '<head><meta charset="utf-8"><title>flash sale</title></head>\n'
        "<body>\n"
        "  <h1>Flash sale</h1>\n"
        f"  <p>Item: {ITEM_NAME}</p>\n"
        f"  <p>Remaining stock in this pod: {_remaining_stock} of {_starting_stock} ({status})</p>\n"
        f"  <p>Requests served by this pod: {_requests}</p>\n"
        "</body>\n"
        "</html>\n"
    )


@app.get("/health")
def health():
    """Cheap liveness endpoint."""
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
