import os

os.makedirs("docs/labs", exist_ok=True)

labs = [
    ("lab-01-docker-networking.md", "Lab 1 - Docker Networking", "Understand how containers communicate inside Docker Compose.", "Start all containers.", "Use docker network inspect and ping between containers.", "How does Gateway find OrderService?", "DNS resolution via Docker DNS.", "Check docker-compose.yml networks."),
    ("lab-02-resource-limits.md", "Lab 2 - Container Resource Limits", "Observe what happens when limits are breached.", "System running normally.", "Check cgroups and inspect container limits.", "What is the CPU limit of CpuWorker?", "It matches docker-compose limits.", "Use docker stats."),
    ("lab-03-cpu-throttling.md", "Lab 3 - CPU Throttling", "Generate CPU load and observe throttling.", "Normal load.", "Use Control UI to start CPU Stress (90%) on CpuWorker. Observe Grafana process_cpu_time_seconds_total.", "Does the container exceed limits?", "No, Kubernetes/Docker throttles it.", "Check Grafana CPU dashboard."),
    ("lab-04-memory-pressure.md", "Lab 4 - Memory Pressure / OOMKilled", "Trigger an OOMKilled event.", "Normal load.", "Use Control UI to allocate 256MB in MemoryWorker (which has a 128MB limit).", "What happens to the pod?", "It gets OOMKilled and restarts.", "Check kubectl describe pod."),
    ("lab-05-kubernetes-deployment.md", "Lab 5 - Kubernetes Deployment", "Deploy the stack to K8s.", "Local K8s cluster ready.", "Run helm install devopslabs ./deploy/kubernetes/helm/devopslabs.", "Are all pods running?", "Yes.", "Check kubectl get events."),
    ("lab-06-kubernetes-probes.md", "Lab 6 - Kubernetes Probes", "Understand liveness and readiness probes.", "System deployed in K8s.", "Inject a deadlock or error storm, see liveness probe fail.", "How long until restart?", "About 15 seconds.", "Check kubectl describe pod for probe failures."),
    ("lab-07-hpa.md", "Lab 7 - HPA", "Observe Horizontal Pod Autoscaling.", "Order Service at 2 replicas.", "Run k6 load.js. Watch CPU rise and HPA scale replicas.", "What is the max replicas?", "10.", "Check kubectl get hpa -w."),
    ("lab-08-keda.md", "Lab 8 - KEDA", "Observe event-driven autoscaling.", "Notification Service at 1 replica.", "Generate RabbitMQ backlog via Control API. Watch KEDA add pods.", "Does it scale before CPU rises?", "Yes, based on queue length.", "Check kubectl get scaledobjects."),
    ("lab-09-rabbitmq-backlog.md", "Lab 9 - RabbitMQ Backlog", "Investigate message queue bottlenecks.", "Normal processing.", "Stall consumers via Control API. Generate 5000 msg/sec load.", "How fast does queue grow?", "Very fast.", "Check Grafana RabbitMQ dashboard."),
    ("lab-10-distributed-tracing.md", "Lab 10 - Distributed Tracing", "Trace a request end-to-end.", "Generate normal traffic.", "Open Grafana Tempo, find a trace from Gateway to DependencyService.", "Can you see the DB query time?", "Yes, Npgsql spans are visible.", "Copy TraceID from Loki."),
    ("lab-11-log-investigation.md", "Lab 11 - Log Investigation", "Find errors using structured logs.", "Trigger Error Storm incident.", "Use Grafana Loki, query {app=\"productservice\"} |= \"error\".", "Is there a TraceID attached?", "Yes.", "Ensure OTel is configured in logs."),
    ("lab-12-metrics-investigation.md", "Lab 12 - Metrics Investigation", "Query PromQL for custom metrics.", "System under load.", "Query devops_lab_requests_total.", "What is the RPS?", "Varies by load script.", "Use rate() function in PromQL."),
    ("lab-13-cascading-failure.md", "Lab 13 - Cascading Failure", "Observe how a slow dependency crashes the system.", "Normal state.", "Trigger Cascading Failure incident.", "Who fails first?", "Gateway times out waiting for OrderService.", "Check thread pool starvation."),
    ("lab-14-incident-investigation.md", "Lab 14 - Incident Investigation", "Find the root cause of a combined outage.", "Trigger Combined Outage (Incident 10).", "Look at Grafana Overview. Identify the broken pieces. Trace errors to their source.", "What is the root cause?", "Redis Outage + DB Error.", "Use Traces to find the first failing span."),
    ("lab-15-recovery.md", "Lab 15 - Recovery", "Restore service after an incident.", "System is broken (Incident 10 active).", "Click 'Emergency Stop' or 'Reset' in Control UI. Watch metrics recover.", "How fast does error rate drop?", "Instantly.", "Check if queue backlogs take time to process."),
    ("lab-16-ci-cd.md", "Lab 16 - CI/CD", "Understand the GitHub Actions pipeline.", "Code pushed to main.", "Review .github/workflows/ci-cd.yml. Trigger a build.", "Does it push to GHCR?", "Yes.", "Check Actions tab.")
]

for filename, title, obj, init, steps, q, ans, hint in labs:
    with open(f"docs/labs/{filename}", "w") as f:
        f.write(f"""# {title}

## Objective
{obj}

## Initial State
{init}

## Steps
1. {steps}
2. Observe the results in the appropriate tool (Grafana/Kubectl).

## What to Observe
- Metric changes.
- Log anomalies.
- Pod state changes.

## Questions
**Q:** {q}
**Expected Observation:** {ans}

## Troubleshooting Hints
- {hint}
""")

readme = """# DevOps Laboratory

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
"""
with open("README.md", "w") as f:
    f.write(readme)

