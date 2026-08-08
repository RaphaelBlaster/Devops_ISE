# Exercise 6 - delivery monitoring

## Overview

A delivery fleet simulator publishes four series, Prometheus scrapes them every
five seconds and evaluates two alert rules, and Grafana renders the series on a
provisioned dashboard. Everything runs from `docker compose`, and every
configuration file is under version control, so no click-through setup is
needed.

| Service | URL | Credentials |
| --- | --- | --- |
| Delivery simulator | http://localhost:8000/metrics and http://localhost:8000/health | none |
| Prometheus | http://localhost:9090 | none |
| Grafana | http://localhost:3000 | `admin` / value of `GRAFANA_ADMIN_PASSWORD`, `admin` when unset |

The simulator refreshes once per second: `pending_deliveries` between 10 and 20,
`on_the_way_deliveries` between 5 and 20, a delivered count between 30 and 70,
`total_deliveries` as the sum of those three, and one observed delivery time
between 15 and 45 seconds.

## Prerequisites

- Docker Desktop with the Linux container engine, running.
- Docker Compose v2 (`docker compose version` prints 2.x).
- Ports 8000, 9090 and 3000 free on the host.
- PowerShell 5.1 or newer, plus `curl.exe`, which ships with Windows 10 and 11.

## Steps

1. Set the Grafana admin password for this shell. When the variable is not set,
   the stack falls back to `admin`.

   ```powershell
   $env:GRAFANA_ADMIN_PASSWORD = "delivery-demo"
   ```

2. Validate the Compose file and the merged configuration.

   ```powershell
   cd .\Exercise6\delivery_monitoring
   docker compose config -q
   ```

3. Build and start the three services. `prometheus` waits for the healthcheck of
   `delivery-metrics`, so the first scrape already sees data.

   ```powershell
   docker compose up --build -d
   docker compose ps
   ```

4. Read the two endpoints of the simulator.

   ```powershell
   curl.exe -s http://localhost:8000/health
   curl.exe -s http://localhost:8000/metrics | Select-String "^(total|pending|on_the_way)_deliveries|^average_delivery_time_(sum|count)"
   ```

5. Check the scrape targets in Prometheus.

   ```powershell
   Start-Process http://localhost:9090/targets
   ```

6. Run the queries below in the Prometheus query box, or in Grafana under
   Explore with the Prometheus data source selected.

   | Query | What it shows |
   | --- | --- |
   | `total_deliveries` | Size of the whole fleet |
   | `pending_deliveries` | Queue that is waiting for a courier |
   | `on_the_way_deliveries` | Deliveries in transit |
   | `average_delivery_time_sum / average_delivery_time_count` | Mean observed delivery time in seconds |
   | `rate(average_delivery_time_count[1m])` | Finished deliveries per second |
   | `pending_deliveries > 10` | The expression behind the warning alert |
   | `ALERTS{alertstate="firing"}` | Alerts that are currently firing |

   The metrics that the simulator publishes:

   | Metric | Type | Meaning |
   | --- | --- | --- |
   | `total_deliveries` | gauge | `pending + on the way + delivered` |
   | `pending_deliveries` | gauge | Waiting to be picked up |
   | `on_the_way_deliveries` | gauge | Picked up and in transit |
   | `average_delivery_time_sum` | summary | Sum of the observed delivery times, in seconds |

## Verification

1. Both endpoints of the simulator answer from the same port.

   ```powershell
   curl.exe -s -o NUL -w "%{http_code}`n" http://localhost:8000/health
   curl.exe -s -o NUL -w "%{http_code}`n" http://localhost:8000/metrics
   ```

   Expected output: `200` twice. The health endpoint returns `{"status": "ok"}`
   and the metrics endpoint starts with `# HELP pending_deliveries`.

2. The container is reported as healthy and the project shows three running
   services.

   ```powershell
   docker inspect --format "{{.State.Health.Status}}" $(docker compose ps -q delivery-metrics)
   docker compose ps
   ```

   Expected output: `healthy`, then one row each for `delivery-metrics`,
   `prometheus` and `grafana` with state `running`.

3. Prometheus scrapes both jobs.

   ```powershell
   curl.exe -s "http://localhost:9090/api/v1/targets?state=active"
   ```

   Expected output: a JSON document whose `data.activeTargets` entries carry
   `"health":"up"` for the jobs `delivery_service` and `prometheus`.

4. The alert rules are loaded and, given the simulated values, fire within about
   twenty seconds.

   ```powershell
   curl.exe -s "http://localhost:9090/api/v1/rules?type=alert"
   ```

   Expected output: the two rules below with `"state":"firing"` once the
   condition has held for fifteen seconds.

   | Alert | Expression | For | Severity |
   | --- | --- | --- | --- |
   | `HighPendingDeliveries` | `pending_deliveries > 10` | 15s | warning |
   | `HighAverageDeliveryTime` | `average_delivery_time_sum / average_delivery_time_count > 30` | 15s | critical |

5. Grafana serves the provisioned dashboard.

   ```powershell
   curl.exe -s -u "admin:$env:GRAFANA_ADMIN_PASSWORD" http://localhost:3000/api/dashboards/uid/delivery-monitoring | Select-String '"title":"Delivery Monitoring"'
   ```

   Expected output: one line containing `"title":"Delivery Monitoring"`.

6. When a check fails, the usual causes and their commands:

   ```powershell
   docker compose ps
   docker compose logs --tail 100 delivery-metrics
   docker compose logs --tail 100 prometheus
   docker compose logs --tail 100 grafana
   docker compose exec delivery-metrics python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/health').read())"
   curl.exe -s http://localhost:9090/-/ready
   Get-NetTCPConnection -LocalPort 8000,9090,3000 -ErrorAction SilentlyContinue | Select-Object LocalPort,State
   ```

   - `prometheus` exits at once: the rule file or the scrape configuration has a
     YAML or PromQL error, and the message is in `docker compose logs prometheus`.
   - A target stays `down`: the host in `prometheus.yml` must match the Compose
     service name `delivery-metrics`.
   - The dashboard is missing: the path in `dashboards.yml` is the path inside
     the container, `/var/lib/grafana/dashboards`, and the JSON file must be
     valid. Look for `failed to load dashboard` in the Grafana log.
   - A port is already bound: change the host side of the mapping in
     `docker-compose.yml`, for example `"8001:8000"`, and update the smoke test.

## Files

| File | Purpose |
| --- | --- |
| `delivery_metrics.py` | Simulator: three gauges, one summary, a background update thread, and one HTTP server that serves `/metrics` and `/health` on port 8000 |
| `requirements.txt` | Pins `prometheus_client==0.21.1` |
| `Dockerfile` | Builds the simulator on `python:3.11-slim`, exposes 8000 and declares the healthcheck on `/health` |
| `docker-compose.yml` | Runs `delivery-metrics`, `prometheus` and `grafana` on the bridge network `monitoring`, with the `grafana-data` volume |
| `prometheus.yml` | Five second scrape and evaluation intervals, the alert rule file, and the jobs `delivery_service` and `prometheus` |
| `alert_rules.yml` | `HighPendingDeliveries` (warning) and `HighAverageDeliveryTime` (critical) |
| `grafana/provisioning/datasources/prometheus.yml` | Prometheus data source on `http://prometheus:9090`, default and not editable |
| `grafana/provisioning/dashboards/dashboards.yml` | File provider that loads the `Delivery` folder from `/var/lib/grafana/dashboards` |
| `grafana/dashboards/delivery-monitoring.json` | Dashboard `Delivery Monitoring`: four time series panels, five second refresh, last fifteen minutes |
| `Jenkinsfile` | Declarative pipeline: validate, build, deploy, smoke test `/metrics`, always print `docker compose ps`, print the last 100 log lines on failure. Stored with LF line endings, because its `sh` steps run on a Linux agent |

   | `average_delivery_time_count` | summary | Number of observed deliveries |
   | `average_delivery_time{quantile="0.5"}` | summary | Median of the observed delivery times |

7. Open the Grafana dashboard `Delivery Monitoring` in the `Delivery` folder. It
   refreshes every five seconds and covers the last fifteen minutes.

8. Stop the stack. Add `-v` to drop the `grafana-data` volume as well.

   ```powershell
   docker compose down
   ```
