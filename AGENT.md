# AGENT.md

Working agreement for this repository. Every agent or teammate working in this
tree follows this file. Read it before creating or editing anything.

## What this repository is

Laboratory coursework for the DevOps (ISE) course. Each `Exercise*/` directory
is self-contained: application source, container and Kubernetes manifests, and a
`README.md` that lists the exact commands needed to reproduce the result.

## Layout

```text
Devops_ISE/
├── AGENT.md              this file
├── CURRENT_STATUS.md     live status of every exercise
├── TASKS.md              work board
├── README.md             repository overview
├── Exercise2/            Flask app, image, first Kubernetes Deployment
├── Exercise3/            image plus ReplicaSet
├── Exercise4/            multi-container Docker networking
├── Exercise5/            AppArmor confinement
├── Exercise6/            Prometheus, Grafana, alerts, Compose
├── Exercise7/            Jenkins controller in a container
├── Exercise8/            Jenkins Freestyle job from Git
├── Exercise9/            Jenkins declarative pipeline
├── Exercise10/           two services on a multi-node cluster
├── K8s-Setup/            Minikube installation on Windows
└── Portfolio/            static personal site
```

## Conventions

- Every exercise directory has a `README.md` with the sections `Overview`,
  `Prerequisites`, `Steps`, `Verification`, `Files`.
- Commands in READMEs are written for PowerShell on Windows, because that is
  what the laboratory machines run. Where a command is Linux-only, the README
  says so explicitly.
- Python targets 3.11 or newer and is always run from a virtual environment.
- Container images are tagged `<name>:latest` and loaded into Minikube with
  `minikube image load`.
- Kubernetes manifests are plain YAML, one resource per file, named
  `<subject>_<kind>.yaml`, for example `product_catalog_deployment.yaml`.
- Prometheus and Grafana are configured from files under version control, not
  by clicking through the UI.
- Every `README.md` ends with a `Files` section that lists what each file does.

## Rules

- No binary artefacts: no screenshots, images, archives, or notebooks with
  stored output. Verification steps are described in text so that anyone can
  reproduce them.
- Never commit credentials, personal access tokens, `.env` files, kubeconfigs,
  or anything under `.venv/` or `__pycache__/`.
- Commit messages are imperative and scoped to a directory, for example
  `Exercise4: add two-container network demo`.
- Commit dates are the real dates on which the work was done. History is not
  rewritten or backdated.
- Keep each exercise independent. A change in one directory must not require a
  change in another.
