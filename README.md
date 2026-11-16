# PlantPal API — CI/CD Pipeline & Kubernetes Deployment

Flask REST API (`GET /`, `GET /health`, `GET /plants`, `POST /plants`, `POST /plants/<id>/water`, `GET /plants/due`) used to demonstrate:
Git → Jenkins CI → Ansible → Docker → Kubernetes.

## Layout
| Path | Purpose |
|---|---|
| `app/` | Flask app, pytest tests, requirements |
| `build.sh` | Build/package script (Python equivalent of `mvn clean package`) → `dist/plantpal-<version>.tar.gz` |
| `Jenkinsfile` | Pipeline: Checkout → Install → **Test** → Build → Archive (SCM polling, versioned by build number + SHA) |
| `.github/workflows/ci.yml` | GitHub Actions build + test on every push |
| `ansible/` | Inventory, playbook, `plantpal` role (variable + handler) |
| `Dockerfile` | Multi-stage image |
| `k8s/` | ConfigMap, Deployment (3 replicas, probes), NodePort Service |

## Component 1 — run locally
```bash
cd app && pip install -r requirements.txt
python -m pytest -v                 # unit tests
APP_PORT=5000 python app.py         # run
curl localhost:5000/plants
curl localhost:5000/plants/due
curl -X POST localhost:5000/plants/1/water
curl -X POST -H 'Content-Type: application/json' -d '{"name":"Money Plant","water_every_days":4}' localhost:5000/plants
cd .. && ./build.sh 1               # creates dist/plantpal-1.tar.gz
```
Jenkins: New Item → Pipeline → "Pipeline script from SCM" → your repo URL → branch `*/main`.
The Jenkinsfile already contains the `pollSCM` trigger. Needs `python3`, `python3-venv`, `git` on the agent.

## Component 2
### Ansible (Ubuntu/Debian VM or WSL with systemd)
```bash
./build.sh dev
cd ansible
ansible-playbook -i inventory playbook.yml --ask-become-pass
curl localhost:5000/health
```
Run it twice: the second run shows `changed=0` (idempotent; handler does not fire).

### Docker
```bash
docker build -t plantpal:1.0.0 .
docker run --rm -p 5000:5000 plantpal:1.0.0
```

### Kubernetes (minikube)
```bash
minikube start
eval $(minikube docker-env)          # build image inside minikube
docker build -t plantpal:1.0.0 .
kubectl apply -f k8s/
kubectl get pods
kubectl get svc
curl $(minikube service plantpal-svc --url)/plants

# scaling
kubectl scale deployment plantpal --replicas=5 && kubectl get pods
kubectl scale deployment plantpal --replicas=3 && kubectl get pods
```

### Rollback demo (optional extra enhancement)
```bash
kubectl set image deployment/plantpal plantpal=plantpal:does-not-exist   # broken release
kubectl rollout status deployment/plantpal --timeout=30s                  # stuck; old pods keep serving
kubectl rollout undo deployment/plantpal
kubectl get pods
```

## Enhancements implemented
- **CI:** automated tests stage, build versioning (`BUILD_NUMBER-GITSHA`), GitHub Actions workflow.
- **Deployment:** ConfigMap, liveness/readiness probes, `/health` endpoint, multi-stage Dockerfile, rollback demo.
  (Only one is required — pick one to feature in the report and mention the rest as extras.)

## Resume lines
- **PlantPal API — CI/CD Pipeline & Kubernetes Deployment** | Python/Flask, Git, Jenkins, Docker, Ansible, Kubernetes
- Built a REST API (track plants and tell you which ones need watering today) with an automated Jenkins pipeline triggered on every Git push; unit tests gate each build and artifacts are versioned by build number and commit SHA.
- Provisioned servers with an Ansible role (variables, handlers); containerized with a multi-stage Dockerfile and deployed on Kubernetes with 3 replicas, ConfigMap-based config, health probes, scaling and rollback.
