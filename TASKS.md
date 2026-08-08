# Tasks

Work board for this repository. Owners are the agents or teammates assigned to
each stream. Update this file and `CURRENT_STATUS.md` together.

| ID | Stream | Task | Owner | Depends on | State |
| --- | --- | --- | --- | --- | --- |
| T1 | docs | Repository scaffolding: `AGENT.md`, `README.md`, `.gitignore` | lead | - | done |
| T2 | docker | Exercise2: Flask app, image, Deployment | docker-k8s | T1 | done |
| T3 | docker | Exercise3: image and ReplicaSet | docker-k8s | T1 | done |
| T4 | docker | Exercise4: two containers on one network | docker-k8s | T1 | done |
| T5 | security | Exercise5: AppArmor profile, apply and test scripts | docker-k8s | T1 | done |
| T6 | observability | Exercise6: metrics app, Compose, Prometheus, Grafana, alerts | observability-cicd | T1 | done |
| T7 | cicd | Exercise7: Jenkins controller from an image | observability-cicd | T1 | done |
| T8 | cicd | Exercise8: Freestyle job that runs a script from Git | observability-cicd | T1 | done |
| T9 | cicd | Exercise9: declarative pipeline with tests and deploy stage | observability-cicd | T1 | done |
| T10 | kubernetes | Exercise10: two services across three nodes | microservices | T1 | done |
| T11 | kubernetes | K8s-Setup: Minikube and kubectl on Windows | microservices | T1 | done |
| T12 | web | Portfolio: static site | microservices | T1 | done |
| T13 | qa | Verification pass over every exercise | lead | T2-T12 | done |
| T14 | release | Commit and push to `RaphaelBlaster/Devops_ISE` | lead | T13 | in progress |

## Definition of done

1. The directory contains the source, manifests, and a `README.md`.
2. The `README.md` has `Overview`, `Prerequisites`, `Steps`, `Verification`,
   and `Files`.
3. The verification command in `CURRENT_STATUS.md` passes.
4. No binary files, secrets, or virtual environments are staged.
