# Exercise 2 - Containerise a Flask app and run it on Kubernetes

## Overview

This exercise turns a small Flask service into a container image and runs two
copies of it on a Minikube cluster. The service answers two routes:

- `GET /` returns an HTML page that names the service and reports how many page
  views the process has served.
- `GET /health` returns `{"status":"ok"}` and is used by the readiness probe.

The page-view counter is kept in memory, so each pod has its own number. The
Deployment asks for two replicas and the Service sits in front of them, which is
why the counter on the page can drop when a request lands on the other pod.

The image is built locally and loaded into Minikube with `minikube image load`,
so `imagePullPolicy: Never` is used and no registry is involved.

## Prerequisites

- Windows 10 or 11 with PowerShell 5.1 or newer.
- Docker Desktop running with the Linux container engine.
- Minikube and kubectl installed and on `PATH` (see `../K8s-Setup`).
- Python 3.11 or newer, only if you want to run `app.py` outside a container.

## Steps

Run every command from this directory.

1. Build the image.

   ```powershell
   docker build -t flask-app:latest .
   ```

2. Start the cluster and point kubectl at it.

   ```powershell
   minikube start
   ```

3. Copy the local image into the cluster. `imagePullPolicy: Never` means the
   kubelet will not look for the image anywhere else.

   ```powershell
   minikube image load flask-app:latest
   ```

4. Create the Deployment and the Service.

   ```powershell
   kubectl apply -f flask-deployment.yaml -f flask-service.yaml
   ```

5. Wait until both replicas are available.

   ```powershell
   kubectl rollout status deployment/flask-app
   ```

6. Forward the Service port to the local machine. The Service listens on port
   80 and forwards to container port 5000. Keep this command running in its own
   terminal.

   ```powershell
   kubectl port-forward service/flask-service 8080:80
   ```

7. Open <http://127.0.0.1:8080/> in a browser.

Reload the page a few times to see the counter change. Because the Service
load-balances over two pods, the number can go back to a smaller value when the
request is served by the other pod.

## Verification

Inspect the three objects:

```powershell
kubectl get deploy,pods,svc
```

Expected shape of the output (names and ages differ):

```text
NAME                        READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/flask-app   2/2     2            2           1m

NAME                             READY   STATUS    RESTARTS   AGE
pod/flask-app-6b9c7f4d8c-2xk7p   1/1     Running   0          1m
pod/flask-app-6b9c7f4d8c-q4tlz   1/1     Running   0          1m

NAME                    TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
service/flask-service   NodePort   10.96.141.203   <none>        80:31234/TCP   1m
```

`READY 2/2` on the Deployment and two `Running` pods with `READY 1/1` are the
important parts. A pod that stays `0/1` has not passed the readiness probe.

Check the page from the terminal, with the port-forward from step 6 still
running:

```powershell
curl.exe -s http://127.0.0.1:8080/
```

Expected body:

```text
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>flask-app</title></head>
<body>
  <h1>Service: flask-app</h1>
  <p>Page views served by this pod: 1</p>
</body>
</html>
```

Check the health route:

```powershell
curl.exe -s http://127.0.0.1:8080/health
```

Expected body:

```text
{"status":"ok"}
```

The same route can be checked from inside the cluster:

```powershell
kubectl run curl-check --rm -it --image=curlimages/curl --restart=Never -- curl -s http://flask-service/health
```

## Files

- `app.py` - Flask application object `app`; port comes from the `PORT`
  environment variable and defaults to 5000. Serves `/` and `/health`. Runs with
  debug mode off.
- `requirements.txt` - pins `flask==3.1.0`.
- `Dockerfile` - builds the image from `python:3.11-slim`; installs the
  requirements before copying the source, exposes port 5000, sets `PORT=5000`,
  and starts the app with `python app.py`.
- `flask-deployment.yaml` - Deployment `flask-app` with 2 replicas, label
  `app=flask-app`, image `flask-app:latest`, `imagePullPolicy: Never`, container
  port 5000, CPU and memory requests, and a readiness probe on `/health`.
- `flask-service.yaml` - Service `flask-service` of type `NodePort`; port 80
  forwards to target port 5000 on the pods selected by `app=flask-app`.
- `README.md` - this file.
