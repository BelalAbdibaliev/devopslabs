import os
import yaml

services = [
    "Gateway", "ControlService", "OrderService", "ProductService", 
    "NotificationService", "DependencyService", "CpuWorker", 
    "MemoryWorker", "LoadGenerator"
]

# 1. Generate Dockerfiles
for svc in services:
    dockerfile_content = f"""
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY ["src/{svc}/{svc}.csproj", "src/{svc}/"]
COPY ["src/Shared/DevOpsLabs.Chaos/DevOpsLabs.Chaos.csproj", "src/Shared/DevOpsLabs.Chaos/"]
RUN dotnet restore "src/{svc}/{svc}.csproj"
COPY src/{svc}/ src/{svc}/
COPY src/Shared/DevOpsLabs.Chaos/ src/Shared/DevOpsLabs.Chaos/
WORKDIR "/src/src/{svc}"
RUN dotnet publish "{svc}.csproj" -c Release -o /app/publish /p:UseAppHost=false

FROM mcr.microsoft.com/dotnet/aspnet:10.0 AS base
WORKDIR /app
EXPOSE 8080
# Non-root user for security
RUN adduser -u 1000 --disabled-password --gecos "" appuser && chown -R appuser /app
USER appuser
ENV ASPNETCORE_URLS=http://+:8080
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "{svc}.dll"]
"""
    os.makedirs(f"src/{svc}", exist_ok=True)
    with open(f"src/{svc}/Dockerfile", "w") as f:
        f.write(dockerfile_content.strip())

# 2. Update docker-compose.yml
dc_path = 'deploy/docker/docker-compose.yml'
os.makedirs(os.path.dirname(dc_path), exist_ok=True)

# Keep the base observability we had
dc = {
    'version': '3.8',
    'services': {
        'postgres': {'image': 'postgres:15-alpine', 'environment': ['POSTGRES_USER=postgres', 'POSTGRES_PASSWORD=postgres', 'POSTGRES_DB=orders'], 'ports': ['5432:5432'], 'healthcheck': {'test': ['CMD-SHELL', 'pg_isready -U postgres'], 'interval': '5s', 'retries': 5}},
        'redis': {'image': 'redis:7-alpine', 'ports': ['6379:6379'], 'healthcheck': {'test': ['CMD', 'redis-cli', 'ping'], 'interval': '5s', 'retries': 5}},
        'rabbitmq': {'image': 'rabbitmq:3.12-management-alpine', 'ports': ['5672:5672', '15672:15672'], 'healthcheck': {'test': ['CMD', 'rabbitmq-diagnostics', 'ping'], 'interval': '5s', 'retries': 5}},
        'otel-collector': {'image': 'otel/opentelemetry-collector-contrib:latest', 'command': ['--config=/etc/otelcol/config.yaml'], 'volumes': ['../../config/otel-collector-config.yaml:/etc/otelcol/config.yaml'], 'ports': ['4317:4317', '4318:4318', '8889:8889'], 'depends_on': ['prometheus', 'loki', 'tempo']},
        'prometheus': {'image': 'prom/prometheus:latest', 'volumes': ['../../config/prometheus.yml:/etc/prometheus/prometheus.yml'], 'ports': ['9090:9090']},
        'loki': {'image': 'grafana/loki:latest', 'ports': ['3100:3100']},
        'tempo': {'image': 'grafana/tempo:latest', 'command': ['-config.file=/etc/tempo.yaml'], 'ports': ['3200:3200']},
        'grafana': {'image': 'grafana/grafana:latest', 'ports': ['3000:3000'], 'volumes': ['../../config/grafana/provisioning:/etc/grafana/provisioning', '../../config/grafana/dashboards:/var/lib/grafana/dashboards'], 'environment': ['GF_AUTH_ANONYMOUS_ENABLED=true', 'GF_AUTH_ANONYMOUS_ORG_ROLE=Admin']}
    }
}

for svc in services:
    dc['services'][svc.lower()] = {
        'build': {'context': '../../', 'dockerfile': f'src/{svc}/Dockerfile'},
        'environment': [
            'ASPNETCORE_ENVIRONMENT=Development',
            'OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317',
            'ConnectionStrings__DefaultConnection=Host=postgres;Database=orders;Username=postgres;Password=postgres',
            'ConnectionStrings__Redis=redis:6379',
            'ConnectionStrings__RabbitMQ=amqp://guest:guest@rabbitmq:5672'
        ],
        'depends_on': ['postgres', 'redis', 'rabbitmq', 'otel-collector']
    }
dc['services']['gateway']['ports'] = ['5000:8080']
dc['services']['controlservice']['ports'] = ['5001:8080']

with open(dc_path, 'w') as f:
    yaml.dump(dc, f, sort_keys=False)

# 3. Create Helm Chart
helm_dir = 'deploy/kubernetes/helm/devopslabs'
os.makedirs(f"{helm_dir}/templates", exist_ok=True)

with open(f"{helm_dir}/Chart.yaml", "w") as f:
    f.write("apiVersion: v2\nname: devopslabs\ndescription: A Helm chart for DevOps Labs Microservices\ntype: application\nversion: 0.1.0\nappVersion: 1.0.0\n")

with open(f"{helm_dir}/values.yaml", "w") as f:
    f.write("""
global:
  env:
    ASPNETCORE_ENVIRONMENT: "Production"
    OTEL_EXPORTER_OTLP_ENDPOINT: "http://otel-collector.observability.svc.cluster.local:4317"
    ConnectionStrings__DefaultConnection: "Host=postgres.infra.svc.cluster.local;Database=orders;Username=postgres;Password=postgres"
    ConnectionStrings__Redis: "redis.infra.svc.cluster.local:6379"
    ConnectionStrings__RabbitMQ: "amqp://guest:guest@rabbitmq.infra.svc.cluster.local:5672"

services:
  gateway:
    replicas: 2
    image: devopslabs/gateway:latest
    port: 8080
    resources:
      requests: { cpu: 100m, memory: 128Mi }
      limits: { cpu: 200m, memory: 256Mi }
    hpa: { enabled: true, minReplicas: 2, maxReplicas: 5, targetCPUUtilizationPercentage: 80 }
  
  controlservice:
    replicas: 1
    image: devopslabs/controlservice:latest
    port: 8080
    resources:
      requests: { cpu: 50m, memory: 64Mi }
      limits: { cpu: 100m, memory: 128Mi }
    
  orderservice:
    replicas: 2
    image: devopslabs/orderservice:latest
    port: 8080
    resources:
      requests: { cpu: 200m, memory: 128Mi }
      limits: { cpu: 500m, memory: 256Mi }
    hpa: { enabled: true, minReplicas: 2, maxReplicas: 10, targetCPUUtilizationPercentage: 75 }

  productservice:
    replicas: 2
    image: devopslabs/productservice:latest
    port: 8080
    resources:
      requests: { cpu: 200m, memory: 128Mi }
      limits: { cpu: 500m, memory: 256Mi }

  notificationservice:
    replicas: 1
    image: devopslabs/notificationservice:latest
    port: 8080
    resources:
      requests: { cpu: 100m, memory: 128Mi }
      limits: { cpu: 300m, memory: 256Mi }
    keda: 
      enabled: true
      minReplicaCount: 1
      maxReplicaCount: 10
      queueLength: 100

  cpuworker:
    replicas: 1
    image: devopslabs/cpuworker:latest
    port: 8080
    resources:
      requests: { cpu: 500m, memory: 128Mi }
      limits: { cpu: 1000m, memory: 256Mi }

  memoryworker:
    replicas: 1
    image: devopslabs/memoryworker:latest
    port: 8080
    resources:
      requests: { cpu: 100m, memory: 64Mi }
      limits: { cpu: 200m, memory: 128Mi } # Will OOMKill easily by design

  loadgenerator:
    replicas: 1
    image: devopslabs/loadgenerator:latest
    port: 8080
    resources:
      requests: { cpu: 200m, memory: 128Mi }
      limits: { cpu: 500m, memory: 256Mi }

  dependencyservice:
    replicas: 1
    image: devopslabs/dependencyservice:latest
    port: 8080
    resources:
      requests: { cpu: 100m, memory: 64Mi }
      limits: { cpu: 200m, memory: 128Mi }
""")

# Helm Deployment Template
with open(f"{helm_dir}/templates/deployment.yaml", "w") as f:
    f.write("""
{{- range $name, $svc := .Values.services }}
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ $name }}
  labels:
    app: {{ $name }}
spec:
  replicas: {{ $svc.replicas }}
  selector:
    matchLabels:
      app: {{ $name }}
  template:
    metadata:
      labels:
        app: {{ $name }}
    spec:
      containers:
      - name: {{ $name }}
        image: {{ $svc.image }}
        ports:
        - containerPort: {{ $svc.port }}
        env:
        {{- range $k, $v := $.Values.global.env }}
        - name: {{ $k }}
          value: {{ $v | quote }}
        {{- end }}
        resources:
{{ toYaml $svc.resources | indent 10 }}
        startupProbe:
          httpGet:
            path: /health
            port: {{ $svc.port }}
          failureThreshold: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: {{ $svc.port }}
          initialDelaySeconds: 5
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /health
            port: {{ $svc.port }}
          initialDelaySeconds: 15
          periodSeconds: 20
{{- end }}
""")

# Helm Service Template
with open(f"{helm_dir}/templates/service.yaml", "w") as f:
    f.write("""
{{- range $name, $svc := .Values.services }}
---
apiVersion: v1
kind: Service
metadata:
  name: {{ $name }}
spec:
  selector:
    app: {{ $name }}
  ports:
    - protocol: TCP
      port: 80
      targetPort: {{ $svc.port }}
{{- end }}
""")

# Helm PDB Template
with open(f"{helm_dir}/templates/pdb.yaml", "w") as f:
    f.write("""
{{- range $name, $svc := .Values.services }}
{{- if gt (int $svc.replicas) 1 }}
---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: {{ $name }}-pdb
spec:
  minAvailable: 1
  selector:
    matchLabels:
      app: {{ $name }}
{{- end }}
{{- end }}
""")

# Helm HPA Template
with open(f"{helm_dir}/templates/hpa.yaml", "w") as f:
    f.write("""
{{- range $name, $svc := .Values.services }}
{{- if and $svc.hpa $svc.hpa.enabled }}
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ $name }}-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ $name }}
  minReplicas: {{ $svc.hpa.minReplicas }}
  maxReplicas: {{ $svc.hpa.maxReplicas }}
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: {{ $svc.hpa.targetCPUUtilizationPercentage }}
{{- end }}
{{- end }}
""")

# Helm KEDA Template
with open(f"{helm_dir}/templates/keda.yaml", "w") as f:
    f.write("""
{{- range $name, $svc := .Values.services }}
{{- if and $svc.keda $svc.keda.enabled }}
---
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: {{ $name }}-scaledobject
spec:
  scaleTargetRef:
    name: {{ $name }}
  minReplicaCount: {{ $svc.keda.minReplicaCount }}
  maxReplicaCount: {{ $svc.keda.maxReplicaCount }}
  triggers:
  - type: rabbitmq
    metadata:
      queueName: notifications-queue
      mode: QueueLength
      value: {{ $svc.keda.queueLength | quote }}
    authenticationRef:
      name: rabbitmq-trigger-auth
---
apiVersion: keda.sh/v1alpha1
kind: TriggerAuthentication
metadata:
  name: rabbitmq-trigger-auth
spec:
  secretTargetRef:
  - parameter: host
    name: rabbitmq-secret
    key: host
{{- end }}
{{- end }}
""")

# Ingress
with open(f"{helm_dir}/templates/ingress.yaml", "w") as f:
    f.write("""
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: devopslabs-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: lab.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: gateway
            port:
              number: 80
""")
