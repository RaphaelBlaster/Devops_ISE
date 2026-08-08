# Devops_ISE

Laboratory work for the DevOps (ISE) course. Every exercise is a self-contained
directory with its own source, manifests, and reproduction steps.

## Exercises

| Exercise | Topic | Tools |
| --- | --- | --- |
| [Exercise2](Exercise2) | Containerise a Flask app and run it on Kubernetes | Docker, Kubernetes, Minikube |
| [Exercise3](Exercise3) | Scale a flash-sale service with a ReplicaSet | Docker, Kubernetes |
| [Exercise4](Exercise4) | Connect two containers over a user-defined network | Docker networking |
| [Exercise5](Exercise5) | Confine a container process with an AppArmor profile | AppArmor, Docker |
| [Exercise6](Exercise6) | Monitor a delivery simulator and raise alerts | Compose, Prometheus, Grafana |
| [Exercise7](Exercise7) | Run a Jenkins controller from an image | Jenkins, Docker |
| [Exercise8](Exercise8) | Build a Freestyle job that runs a script from Git | Jenkins, Git |
| [Exercise9](Exercise9) | Build a declarative pipeline that tests and deploys | Jenkins, Python |
| [Exercise10](Exercise10) | Place two services across a three-node cluster | Kubernetes, Minikube |
| [K8s-Setup](K8s-Setup) | Install Minikube and kubectl on Windows | Minikube, kubectl, Chocolatey |
| [Portfolio](Portfolio) | Static personal site | HTML, CSS |

## Prerequisites

- Windows 10 or 11 with PowerShell 5.1 or newer.
- Docker Desktop with the Linux container engine, running.
- Minikube and kubectl for the Kubernetes exercises.
- Python 3.11 or newer for the Python exercises.
- Jenkins, either containerised as in Exercise 7 or installed natively.

## Running an exercise

Open the exercise directory and follow its `README.md`. The short version:

```powershell
# Docker-based exercises
cd .\Exercise4
docker compose up --build -d

# Kubernetes-based exercises
cd .\Exercise10
docker build -f Dockerfile.product -t product-catalog:latest .
minikube image load product-catalog:latest
kubectl apply -f product_catalog_deployment.yaml
```

Each `README.md` lists the expected output so the result can be checked without
guessing.

## Repository conventions

See [AGENT.md](AGENT.md). In short: one directory per exercise, a README with
`Overview`, `Prerequisites`, `Steps`, `Verification`, and `Files`, no committed
binaries, and no secrets.

## Status

See [CURRENT_STATUS.md](CURRENT_STATUS.md) for what is finished and what is in
progress.
