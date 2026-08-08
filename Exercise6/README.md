# Exercise 6 - real-time monitoring and alerting

## Overview

This exercise instruments a delivery service with `prometheus_client`, scrapes
it with Prometheus, evaluates two alert rules, and renders the series on a
Grafana dashboard. The stack is described in one Compose file and every
configuration file lives in the repository, so the environment can be rebuilt
from scratch with two commands.

The runnable material is in [`delivery_monitoring`](delivery_monitoring), which
also carries the detailed README.

## Prerequisites

- Docker Desktop with the Linux container engine, running.
- Docker Compose v2.
- Ports 8000, 9090 and 3000 free on the host.
- PowerShell 5.1 or newer and `curl.exe`.

## Steps

1. Move into the stack directory.

   ```powershell
   cd .\Exercise6\delivery_monitoring
   ```

2. Optionally set the Grafana admin password for this shell.

   ```powershell
   $env:GRAFANA_ADMIN_PASSWORD = "delivery-demo"
   ```

3. Build and start the simulator, Prometheus and Grafana.

   ```powershell
   docker compose up --build -d
   ```

4. Open http://localhost:8000/metrics, http://localhost:9090/targets and
   http://localhost:3000.

5. Stop the stack when the checks are done.

   ```powershell
   docker compose down
   ```

## Verification

Run the checks from `Exercise6\delivery_monitoring`:

```powershell
curl.exe -s http://localhost:8000/health
curl.exe -s http://localhost:8000/metrics | Select-String "^pending_deliveries"
docker compose ps
curl.exe -s "http://localhost:9090/api/v1/rules?type=alert"
```

- `/health` answers `{"status": "ok"}` with HTTP 200.
- `/metrics` lists `total_deliveries`, `pending_deliveries`,
  `on_the_way_deliveries`, `average_delivery_time_sum` and
  `average_delivery_time_count`.
- `docker compose ps` shows three running services and the simulator `healthy`.
- The rule endpoint lists `HighPendingDeliveries` and
  `HighAverageDeliveryTime` in state `firing`.

The exact expected output of each check is in
[`delivery_monitoring/README.md`](delivery_monitoring/README.md).

## Files

| Path | Purpose |
| --- | --- |
| `delivery_monitoring/` | Complete Compose stack: simulator, Prometheus configuration, alert rules, Grafana provisioning and dashboard, Jenkins pipeline |
| `delivery_monitoring/README.md` | Detailed steps, verification and troubleshooting for the stack |
