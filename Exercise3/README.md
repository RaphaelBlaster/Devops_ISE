# Exercise 3 - Scale a flash sale service with a ReplicaSet

## Overview

This exercise runs a flash sale service as a ReplicaSet with three identical
pods. The service answers two routes:

- `GET /` claims one unit of stock and returns an HTML page with the item name,
  the remaining stock and the number of requests the process has served.
- `GET /health` returns `ok`.

Stock starts at 100 and is read from the `STOCK` environment variable. Both
counters are in process memory, so each pod sells from its own pool. That is the
point of the exercise: `kubectl scale rs/flashsale --replicas=5` multiplies the
number of independent pools instead of sharing one.

A ReplicaSet is used on purpose instead of a Deployment. It keeps the number of
pod copies at the value you ask for, but it has no rollout or rollback support,
which is exactly what the next exercise builds on.

## Prerequisites

- Windows 10 or 11 with PowerShell 5.1 or newer.
- Docker Desktop running with the Linux container engine.
- Minikube and kubectl installed and on `PATH` (see `../K8s-Setup`).
- Python 3.11 or newer, only if you want to run `flash_sale.py` outside a
  container.

## Steps

Run every command from this directory.

1. Build the image.

   ```powershell
   docker build -t flashsale:latest .
   ```

2. Start the cluster and load the image into it. `imagePullPolicy: Never` means
   the kubelet only uses the copy that is already inside the cluster.

   ```powershell
   minikube start
   minikube image load flashsale:latest
   ```

3. Create the ReplicaSet.

   ```powershell
   kubectl apply -f flashsale-replicaset.yaml
   ```

4. Check that three pods were created.

   ```powershell
   kubectl get rs
   kubectl get pods -l app=flashsale -o wide
   ```

5. Scale up to five replicas, then back to three.

   ```powershell
   kubectl scale rs/flashsale --replicas=5
   kubectl get rs
   kubectl scale rs/flashsale --replicas=3
   kubectl get rs
   ```

6. Forward one pod to the local machine. Picking a single pod keeps the counter
   readable, because a Service would spread the requests over all pods. Keep the
   command running in its own terminal.

   ```powershell
   $pod = kubectl get pods -l app=flashsale -o jsonpath="{.items[0].metadata.name}"
   kubectl port-forward "pod/$pod" 8080:5000
   ```

7. In a second terminal, call the pod.

   ```powershell
   curl.exe -s http://127.0.0.1:8080/
   curl.exe -s http://127.0.0.1:8080/health
   ```

Call `/` several times: the remaining stock goes down by one on every request
and the request counter goes up by one. Restart the port-forward on a different
pod and the stock is back at 100, because the counters are per process.

Clean up when you are done:

```powershell
kubectl delete -f flashsale-replicaset.yaml
```

## Verification

```powershell
kubectl get rs
```

Expected row:

```text
NAME        DESIRED   CURRENT   READY   AGE
flashsale   3         3         3       45s
```

`DESIRED 3 / CURRENT 3 / READY 3` means the ReplicaSet is satisfied. After
`kubectl scale rs/flashsale --replicas=5` the same row reads
`5 / 5 / 5`, and after scaling back it reads `3 / 3 / 3` again.

```powershell
kubectl get pods -l app=flashsale -o wide
```

Expected shape:

```text
NAME              READY   STATUS    RESTARTS   AGE   IP           NODE
flashsale-4k2xv   1/1     Running   0          45s   10.244.0.7   minikube
flashsale-9dpt8   1/1     Running   0          45s   10.244.0.8   minikube
flashsale-hz6ql   1/1     Running   0          45s   10.244.0.9   minikube
```

With the port-forward from step 6 running, the body of `GET /` is:

```text
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>flash sale</title></head>
<body>
  <h1>Flash sale</h1>
  <p>Item: Limited edition mechanical keyboard</p>
  <p>Remaining stock in this pod: 99 of 100 (in stock)</p>
  <p>Requests served by this pod: 1</p>
</body>
</html>
```

The second request shows `Remaining stock in this pod: 98 of 100` and
`Requests served by this pod: 2`. `GET /health` returns the single word `ok`.

## Files

- `flash_sale.py` - Flask application; port 5000, item name, remaining stock and
  request counter on `/`, `ok` on `/health`. Starting stock comes from the
  `STOCK` environment variable and defaults to 100.
- `requirements.txt` - pins `flask==3.1.0`.
- `Dockerfile` - same pattern as Exercise 2: `python:3.11-slim`, requirements
  installed before the source is copied, port 5000 exposed, `PORT=5000`, and the
  app started with `python flash_sale.py`.
- `flashsale-replicaset.yaml` - ReplicaSet `flashsale` with 3 replicas, label
  `app=flashsale`, image `flashsale:latest`, `imagePullPolicy: Never`, container
  port 5000, and `STOCK=100`.
- `README.md` - this file.
