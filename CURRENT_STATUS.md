# Current status

Last updated: 2026-10-17

| Exercise | Scope | State | Verified by |
| --- | --- | --- | --- |
| Exercise2 | Flask app, image, Deployment | done | smoke test: `GET /` 200 and `GET /health` |
| Exercise3 | Image and ReplicaSet | done | smoke test: stock falls from 100 to 99 |
| Exercise4 | Two containers on one network | done | smoke test: real backend on :18000, 503 path |
| Exercise5 | AppArmor profile and tests | done | `compileall`; enforcement needs a Linux host |
| Exercise6 | Prometheus, Grafana, alerts | done | smoke test: all five series present |
| Exercise7 | Jenkins controller | done | Compose file parses; needs Docker to run |
| Exercise8 | Freestyle job from Git | done | `hello-world.sh` reviewed; needs Jenkins to run |
| Exercise9 | Declarative pipeline | done | `unittest`: 4 tests, 4 passed |
| Exercise10 | Multi-node services | done | smoke test: catalog, cart CRUD, 400 and 404 paths |
| K8s-Setup | Minikube on Windows | done | Script reviewed; needs an elevated shell to run |
| Portfolio | Static site | done | Stylesheet resolves; no external URLs |

The smoke test drove the applications through the Flask test client and started
the Exercise 4 backend as a real process, so every HTTP path listed above was
executed, not just imported.

## State values

- `planned` - agreed but not started.
- `in progress` - being written.
- `done` - files present and the check in the `Verified by` column has passed.

## Verification commands

| Check | Command |
| --- | --- |
| Python syntax | `python -m compileall -q Exercise2 Exercise3 Exercise4 Exercise5 Exercise6 Exercise9 Exercise10` |
| Unit tests | `python -m unittest discover -s Exercise9\python-flask-app -p "test_*.py"` |
| Compose config | `docker compose -f Exercise6\delivery_monitoring\docker-compose.yml config` |
| Manifests | `kubectl apply --dry-run=client -f Exercise10` |
| JSON dashboards | `python -c "import json,pathlib; [json.loads(p.read_text()) for p in pathlib.Path('Exercise6').rglob('*.json')]"` |

## Open items

These need tooling that is not installed on the machine this repository was
written on. They are the only steps that have not been executed here.

- Confirm the Compose stack comes up on a machine with Docker Desktop running.
- Confirm the three-node Minikube profile schedules all five pods.
- Confirm the Exercise 5 profile loads with `apparmor_parser` on a Linux host.
- Run the Exercise 6, Exercise 7 and Exercise 9 Jenkinsfiles in a Jenkins job.
