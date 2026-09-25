# DevOps Laboratory

Welcome to the .NET 10 DevOps Laboratory! This project is designed as a playground for DevOps engineers and SREs to intentionally break a distributed microservices system and investigate the fallout using modern observability tools.

## Architecture
- **Gateway (YARP)**
- **Order Service** -> **RabbitMQ** -> **Notification Service**
- **Product Service** (uses Redis & PostgreSQL)
- **Dependency Service**
- **Workers** (CPU, Memory, Load)
- **Control Service** (Provides an API and Dashboard to trigger Chaos)

## Getting Started

### 1. Clone the repository
```bash
git clone <repo-url>
cd DevopsLabs
```

### 2. Run Locally (Docker Compose)
This spins up all .NET services, PostgreSQL, Redis, RabbitMQ, plus the entire OpenTelemetry/Prometheus/Grafana/Loki/Tempo stack.
```bash
docker compose -f deploy/docker/docker-compose.yml up -d --build
```

### 3. Open Grafana
Go to `http://localhost:3000`. No login required.
You will see pre-provisioned Data Sources (Prometheus, Loki, Tempo) and a **System Overview** dashboard.

### 4. Control Center Dashboard
Go to `http://localhost:5001`.
Use the Control Center UI to trigger Memory Leaks, CPU Spikes, RabbitMQ Queue floods, or full Production Incidents.

### 5. Run K6 Load Tests
```bash
k6 run tests/k6/load.js
```

### 6. Kubernetes Deployment
Install Helm and KEDA, then deploy:
```bash
helm install keda kedacore/keda --namespace keda --create-namespace
helm install devopslabs ./deploy/kubernetes/helm/devopslabs
```

### 7. Investigate Incidents
Trigger **Incident 10 (Combined Outage)** from the Control Dashboard.
**DO NOT look at the source code!** Use Grafana (Metrics, Logs, Traces) to figure out what broke and why. Once you find it, hit "Emergency Stop" in the UI to recover.

See the `docs/labs/` directory for 16 guided DevOps training exercises!
