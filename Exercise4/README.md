# Exercise 4 - Connect two containers over a user-defined network

## Overview

Two containers are put on one user-defined bridge network. The backend serves a
fixed currency rate table as JSON, and the front end renders it as a table.

- Backend, port 8000: `GET /rates` returns the rate table, `GET /health`
  returns `{"status":"ok"}`. It uses the Python standard library only.
- Front end, port 5000: `GET /` fetches `http://backend:8000/rates` with
  `urllib` and a 3 second timeout and renders the table. If the backend cannot
  be reached, the page answers HTTP 503 with a short message. `GET /health`
  returns `ok`.

The name `backend` resolves because both containers are attached to the same
user-defined network. Docker's built-in bridge network does not provide name
resolution, so the network has to be created first, either by hand or by
Compose.

The front end container also starts a backend of its own, because it runs the
image's default command. The page never uses it: it always calls the URL in
`BACKEND_URL`, which points at the separate `backend` container.

Two ways to run the stack are described below. Pick one; they are not meant to
be mixed.

## Prerequisites

- Windows 10 or 11 with PowerShell 5.1 or newer.
- Docker Desktop running with the Linux container engine.
- Docker Compose v2 (`docker compose version`), which ships with Docker
  Desktop.
- Python 3.11 or newer, only if you want to run the two scripts outside a
  container.

## Steps

Run every command from this directory.

### Build the image (both paths need it)

```powershell
docker build -t ex4-two-containers:latest .
```

### Path A - user-defined network created by hand

1. Create the network.

   ```powershell
   docker network create ex4-net
   ```

2. Start the backend on that network.

   ```powershell
   docker run -d --name backend --network ex4-net ex4-two-containers:latest python backend.py
   ```

3. Start the front end on the same network and publish its port.

   ```powershell
   docker run -d --name web --network ex4-net -p 8080:5000 -e BACKEND_URL=http://backend:8000 ex4-two-containers:latest
   ```

4. Open <http://127.0.0.1:8080/>.

### Path B - Docker Compose

Compose creates the network `ex4-net` from `docker-compose.yml`, builds both
services from the same Dockerfile and starts them. If you already created
`ex4-net` by hand in path A, remove it first: Compose refuses to adopt a network
it did not create.

```powershell
docker network rm ex4-net
docker compose up --build -d
```

Check what is running, then open <http://127.0.0.1:8080/>:

```powershell
docker compose ps
```

Stop the stack and remove the network:

```powershell
docker compose down
```

## Verification

Both containers are attached to `ex4-net`:

```powershell
docker network inspect ex4-net --format "{{range .Containers}}{{.Name}} {{.IPv4Address}}{{println}}{{end}}"
```

Expected, with different addresses:

```text
backend 172.18.0.2/16
web 172.18.0.3/16
```

```powershell
docker network inspect ex4-net
```

Expected shape of the `Containers` block (only the first entries are shown):

```text
"Containers": {
    "1f0a...": {
        "Name": "backend",
        "EndpointID": "9c2b...",
        "MacAddress": "02:42:ac:12:00:02",
        "IPv4Address": "172.18.0.2/16",
        "IPv6Address": ""
    },
    "8d4e...": {
        "Name": "web",
        ...
        "IPv4Address": "172.18.0.3/16",
        ...
    }
},
"Name": "ex4-net",
"Driver": "bridge",
```

The front end renders the rate table:

```powershell
curl.exe -s http://127.0.0.1:8080/
```

Expected body:

```text
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>exchange rates</title></head>
<body>
  <h1>Exchange rates</h1>
  <p>Base currency: USD</p>
  <p>Source: fixed table</p>
  <table border="1">
    <tr><th>Currency</th><th>Rate</th></tr>
      <tr><td>EUR</td><td>0.92</td></tr>
      <tr><td>GBP</td><td>0.79</td></tr>
      <tr><td>INR</td><td>83.12</td></tr>
  </table>
  <p>Fetched from http://backend:8000/rates</p>
</body>
</html>
```

The backend answers the front end over the network:

```powershell
docker exec web python -c "import urllib.request; print(urllib.request.urlopen('http://backend:8000/rates', timeout=3).read().decode())"
```

Expected body:

```text
{"base": "USD", "rates": {"EUR": 0.92, "GBP": 0.79, "INR": 83.12}, "source": "fixed table"}
```

Now break the connection on purpose and check the error path:

```powershell
docker stop backend
curl.exe -s -o NUL -w "%{http_code}`n" http://127.0.0.1:8080/
```

Expected:

```text
503
```

```powershell
curl.exe -s http://127.0.0.1:8080/
```

Expected body:

```text
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>rates unavailable</title></head>
<body><h1>503 - rate backend unavailable</h1>
<p>Could not reach http://backend:8000/rates within 3 seconds.</p></body></html>
```

Start the backend again to confirm the page recovers:

```powershell
docker start backend
```

Path A cleanup:

```powershell
docker rm -f web backend
docker network rm ex4-net
```

## Files

- `backend.py` - rate backend on port 8000 built on `http.server`; serves the
  fixed rate table on `/rates` and `{"status":"ok"}` on `/health`. Port comes
  from `PORT`, default 8000.
- `app.py` - Flask front end on port 5000; fetches `BACKEND_URL/rates` with
  `urllib` and a 3 second timeout, renders the table, answers 503 when the
  backend is down, and returns `ok` on `/health`. `BACKEND_URL` defaults to
  `http://backend:8000`.
- `requirements.txt` - pins `flask==3.1.0` for the front end.
- `Dockerfile` - `python:3.11-slim` image holding both scripts; installs the
  requirements, exposes ports 8000 and 5000, and starts the backend in the
  background before the front end takes over the container.
- `docker-compose.yml` - two services built from the same Dockerfile:
  `backend` (command overridden to run `backend.py` only) and `web` (publishes
  `8080:5000`), both attached to the user-defined bridge network `ex4-net`.
- `README.md` - this file.
