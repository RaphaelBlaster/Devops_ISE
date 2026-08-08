"""Delivery service simulator.

The process keeps a small set of series that describe a delivery fleet and
publishes them in the Prometheus text format. One HTTP server answers both
endpoints, so the container healthcheck and the scrape target share a port:

    /metrics   Prometheus exposition format
    /health    JSON health probe used by the container HEALTHCHECK

Run locally:

    python delivery_metrics.py
"""

from __future__ import annotations

import json
import os
import random
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

from prometheus_client import CONTENT_TYPE_LATEST, Gauge, Summary, generate_latest

PORT = int(os.environ.get("PORT", "8000"))
UPDATE_INTERVAL_SECONDS = 1.0

# Current size of each queue in the fleet.
TOTAL_DELIVERIES = Gauge(
    "total_deliveries",
    "Deliveries the service knows about, that is pending + on the way + delivered.",
)
PENDING_DELIVERIES = Gauge(
    "pending_deliveries",
    "Deliveries that are waiting to be picked up by a courier.",
)
ON_THE_WAY_DELIVERIES = Gauge(
    "on_the_way_deliveries",
    "Deliveries that a courier has picked up and is carrying right now.",
)

# Observed end to end delivery time. The Summary also exposes the _sum and
# _count series, so the running average is
# average_delivery_time_sum / average_delivery_time_count.
AVERAGE_DELIVERY_TIME = Summary(
    "average_delivery_time",
    "Observed delivery time of a finished delivery, in seconds.",
)


def simulate() -> None:
    """Refresh the fleet gauges and observe one finished delivery."""
    pending = random.randint(10, 20)
    on_the_way = random.randint(5, 20)
    delivered = random.randint(30, 70)

    PENDING_DELIVERIES.set(pending)
    ON_THE_WAY_DELIVERIES.set(on_the_way)
    TOTAL_DELIVERIES.set(pending + on_the_way + delivered)
    AVERAGE_DELIVERY_TIME.observe(random.uniform(15, 45))


def update_loop(stop_event: threading.Event) -> None:
    """Refresh the simulation once per second until the server shuts down."""
    while not stop_event.is_set():
        simulate()
        stop_event.wait(UPDATE_INTERVAL_SECONDS)


class DeliveryHandler(BaseHTTPRequestHandler):
    server_version = "DeliveryMetrics/1.0"
    protocol_version = "HTTP/1.1"

    def _send(self, status: int, content_type: str, body: bytes) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802 - name required by BaseHTTPRequestHandler
        route = urlsplit(self.path).path.rstrip("/") or "/"

        if route == "/metrics":
            self._send(200, CONTENT_TYPE_LATEST, generate_latest())
        elif route == "/health":
            self._send(200, "application/json", json.dumps({"status": "ok"}).encode("utf-8"))
        elif route == "/":
            self._send(200, "text/plain; charset=utf-8", b"delivery simulator: /metrics, /health\n")
        else:
            self._send(404, "text/plain; charset=utf-8", b"not found\n")

    def log_message(self, fmt: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))


def main() -> None:
    stop_event = threading.Event()
    updater = threading.Thread(
        target=update_loop,
        args=(stop_event,),
        name="delivery-simulator",
        daemon=True,
    )
    updater.start()

    server = ThreadingHTTPServer(("0.0.0.0", PORT), DeliveryHandler)
    print(f"delivery metrics listening on http://0.0.0.0:{PORT}/metrics", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("interrupted, shutting down", flush=True)
    finally:
        stop_event.set()
        server.server_close()
        updater.join(timeout=2)


if __name__ == "__main__":
    main()
