# Exercise 10 - Two services across a three-node cluster

## Overview

This exercise places two small Flask services on a three-node Minikube cluster
and checks where the scheduler put them.

- `product-catalog` is a read-only service. `GET /products` returns a fixed
  catalog of four products, `GET /health` returns `{"status": "ok"}`.
- `shopping-cart` keeps an in-memory cart. `GET /cart` returns the lines and a
  count, `POST /cart` appends a line, `DELETE /cart/<id>` removes lines.

Both services listen on port 8080 inside the container. Two Deployments create
the pods and two ClusterIP Services give them stable names on port 80. Each
Deployment carries a `requiredDuringSchedulingIgnoredDuringExecution`
pod anti-affinity rule on `kubernetes.io/hostname`, so no two pods of the same
service may land on the same node. With two catalog replicas and three cart
replicas on a three-node cluster, the catalog pods spread over two nodes and the
cart pods take one node each. If a node were missing, the extra pod would stay
`Pending` instead of sharing a node - that is the point of `required` rather than
`preferred`.

The cart Deployment also sets `maxSurge: 0` and `maxUnavailable: 1`. A rollout
therefore replaces pods one at a time and never creates a surplus pod, which
keeps the anti-affinity rule satisfiable on a cluster that has no spare node.

## Prerequisites

- Windows 10 or 11 with PowerShell 5.1 or newer.
- Docker Desktop running with the Linux container engine. Minikube uses the
  `docker` driver, so Docker must be up before `minikube start`.
- Minikube and kubectl installed and on `PATH` (see `../K8s-Setup`).
- Enough memory to give the cluster profile 1800 MB and two CPUs. Close other
  Minikube profiles first with `minikube delete --all` if the machine is tight.
- No extra HTTP tooling. The steps use `Invoke-RestMethod`, which ships with
  PowerShell.

## Steps

Run every command from this directory.

1. Build both images on the local machine.

   ```powershell
   docker build -f Dockerfile.product -t product-catalog:latest .
   docker build -f Dockerfile.shopping -t shopping-cart:latest .
   ```

2. Start a three-node cluster in its own profile. One node is the control plane
   and all three are schedulable, so the five pods have three hostnames to use.

   ```powershell
   minikube start --nodes=3 -p devops-multinode --driver=docker --memory=1800 --cpus=2
   ```

3. Load both images into that profile. The manifests use
   `imagePullPolicy: IfNotPresent` and there is no registry, so the images must
   exist inside the cluster before the pods start.

   ```powershell
   minikube -p devops-multinode image load product-catalog:latest
   minikube -p devops-multinode image load shopping-cart:latest
   ```

4. Apply the four manifests.

   ```powershell
   kubectl apply -f product_catalog_deployment.yaml
   kubectl apply -f product_catalog_service.yaml
   kubectl apply -f shopping_cart_deployment.yaml
   kubectl apply -f shopping_cart_service.yaml
   ```

5. Wait for both rollouts to finish.

   ```powershell
   kubectl rollout status deployment/product-catalog --timeout=120s
   kubectl rollout status deployment/shopping-cart --timeout=120s
   ```

6. Look at the placement. The `NODE` column is what this exercise is about.

   ```powershell
   kubectl get pods -o wide
   kubectl get nodes
   ```

7. Forward each Service to a different local port. Keep both commands running,
   each in its own terminal window.

   ```powershell
   kubectl port-forward service/product-catalog-service 18081:80
   ```

   ```powershell
   kubectl port-forward service/shopping-cart-service 18082:80
   ```

8. In a third terminal, read the catalog.

   ```powershell
   Invoke-RestMethod -Uri http://127.0.0.1:18081/products -Method Get
   Invoke-RestMethod -Uri http://127.0.0.1:18081/health -Method Get
   ```

9. Read the empty cart, then add a line.

   ```powershell
   Invoke-RestMethod -Uri http://127.0.0.1:18082/cart -Method Get

   $body = @{ id = 3; name = "27 inch monitor"; quantity = 2 } | ConvertTo-Json
   Invoke-RestMethod -Uri http://127.0.0.1:18082/cart -Method Post `
     -ContentType "application/json" -Body $body
   ```

10. Read the cart again and remove the line.

    ```powershell
    Invoke-RestMethod -Uri http://127.0.0.1:18082/cart -Method Get
    Invoke-RestMethod -Uri http://127.0.0.1:18082/cart/3 -Method Delete
    ```

11. Check that the cart Service really spreads over all three pods. Each pod
    keeps its own cart, so a `GET /cart` may reach a pod that never saw the
    `POST`. To look at one pod directly, forward a pod instead of the Service:

    ```powershell
    $pod = kubectl get pods -l app=shopping-cart -o jsonpath="{.items[0].metadata.name}"
    kubectl port-forward "pod/$pod" 18083:8080
    ```

    Then compare `http://127.0.0.1:18083/cart` with
    `http://127.0.0.1:18082/cart`.

12. Clean up.

    ```powershell
    kubectl delete -f shopping_cart_service.yaml -f shopping_cart_deployment.yaml `
      -f product_catalog_service.yaml -f product_catalog_deployment.yaml
    minikube stop -p devops-multinode
    ```

    Use `minikube delete -p devops-multinode` to remove the profile entirely.

## Verification

Node count first. Three nodes, all `Ready`, one of them the control plane:

```powershell
kubectl get nodes
```

```text
NAME                          STATUS   ROLES           AGE   VERSION
devops-multinode              Ready    control-plane   92s   v1.34.0
devops-multinode-m02          Ready    <none>          71s   v1.34.0
devops-multinode-m03          Ready    <none>          63s   v1.34.0
```

Placement of the five pods:

```powershell
kubectl get pods -o wide
```

```text
NAME                              READY   STATUS    RESTARTS   AGE   IP           NODE
product-catalog-6b9f4c7d5-2qvxm   1/1     Running   0          48s   10.244.1.5   devops-multinode-m02
product-catalog-6b9f4c7d5-t8knr   1/1     Running   0          48s   10.244.0.6   devops-multinode
shopping-cart-7d5c8f9b64-4hzlp    1/1     Running   0          46s   10.244.2.4   devops-multinode-m03
shopping-cart-7d5c8f9b64-jq9wd    1/1     Running   0          46s   10.244.1.6   devops-multinode-m02
shopping-cart-7d5c8f9b64-vx2mr    1/1     Running   0          46s   10.244.0.7   devops-multinode
```

What to check in that table:

- Both `product-catalog` pods are `1/1 Running` and their `NODE` values differ.
  Two pods, two different nodes, because of the required anti-affinity rule.
- The three `shopping-cart` pods are `1/1 Running` on three different nodes, so
  every node carries exactly one cart pod.
- Pod names carry a random suffix, so the suffixes and the IP addresses on your
  machine will differ. Only the counts and the distinct `NODE` values matter.
- If a pod stays `Pending`, the cluster has fewer schedulable nodes than the
  anti-affinity rule needs. `kubectl describe pod <name>` ends with the
  scheduling message that says so.

Both Services must list the pod IPs they select:

```powershell
kubectl get svc product-catalog-service shopping-cart-service
kubectl get endpoints product-catalog-service shopping-cart-service
```

```text
NAME                     TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)   AGE
product-catalog-service  ClusterIP   10.104.3.181   <none>        80/TCP    50s
shopping-cart-service    ClusterIP   10.104.7.94    <none>        80/TCP    50s

NAME                     ENDPOINTS                                      AGE
product-catalog-service  10.244.0.6:8080,10.244.1.5:8080                50s
shopping-cart-service    10.244.0.7:8080,10.244.1.6:8080,10.244.2.4:8080  50s
```

Two endpoints for the catalog and three for the cart. A missing endpoint means
the matching readiness probe has not passed yet.

With the port-forward from step 7 running, `GET /products` returns:

```json
{
  "count": 4,
  "products": [
    { "id": 1, "name": "Mechanical keyboard", "price": 89.9 },
    { "id": 2, "name": "USB-C dock", "price": 64.5 },
    { "id": 3, "name": "27 inch monitor", "price": 219.0 },
    { "id": 4, "name": "Laptop stand", "price": 32.75 }
  ]
}
```

`GET /health` on either service returns:

```json
{ "status": "ok" }
```

`GET /cart` before anything is added returns:

```json
{ "items": [], "count": 0 }
```

The `POST /cart` from step 9 answers HTTP 201 with:

```json
{
  "added": { "id": 3, "name": "27 inch monitor", "quantity": 2 },
  "count": 1,
  "items": [{ "id": 3, "name": "27 inch monitor", "quantity": 2 }]
}
```

The next `GET /cart` returns the same `items` list with `"count": 1`, and
`DELETE /cart/3` returns `{"items": [], "count": 0, "removed": 1}`. Deleting the
same id twice answers HTTP 404 with `{"error": "id not in cart", "id": 3}`.

The cart lives in the memory of the pod that answered the request, and each of
the three cart pods keeps its own copy. Two consequences to expect:

- A `GET /cart` through the Service can reach a pod that never saw the `POST`
  and then report an empty cart. Retry, or use the pod port-forward from step 11.
- Restarting a cart pod resets its cart. Delete the pods and the replacements
  start from `{"items": [], "count": 0}`:

  ```powershell
  kubectl delete pod -l app=shopping-cart
  ```

Nothing here is persisted, so no cart state survives a pod restart or a
`minikube stop`.

## Files

- `product_catalog.py` - Flask catalog service. Port 8080, `GET /products` with
  four products, `GET /products/<id>` for one product, `GET /health` for the
  probes.
- `shopping_cart.py` - Flask cart service. Port 8080, in-memory cart guarded by a
  lock, `GET /cart`, `POST /cart`, `DELETE /cart/<id>`, `DELETE /cart` to empty
  it, `GET /health`.
- `requirements.txt` - pins `flask==3.1.0`; both images install it.
- `Dockerfile.product` - `python:3.11-slim`, installs the requirements, copies
  `product_catalog.py`, exposes 8080, runs the script.
- `Dockerfile.shopping` - the same pattern for `shopping_cart.py`.
- `product_catalog_deployment.yaml` - Deployment `product-catalog`, 2 replicas,
  image `product-catalog:latest`, `imagePullPolicy: IfNotPresent`, container port
  8080, HTTP readiness probe on `/health`, required pod anti-affinity on
  `app=product-catalog` with `topologyKey: kubernetes.io/hostname`.
- `product_catalog_service.yaml` - Service `product-catalog-service`, ClusterIP,
  port 80 to target port 8080, selector `app=product-catalog`.
- `shopping_cart_deployment.yaml` - Deployment `shopping-cart`, 3 replicas,
  RollingUpdate strategy with `maxSurge: 0` and `maxUnavailable: 1`, HTTP
  readiness probe on `/health`, required pod anti-affinity on `app=shopping-cart`
  with `topologyKey: kubernetes.io/hostname`.
- `shopping_cart_service.yaml` - Service `shopping-cart-service`, ClusterIP,
  port 80 to target port 8080, selector `app=shopping-cart`.
- `README.md` - this file.
