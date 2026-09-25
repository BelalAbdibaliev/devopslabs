import os
import yaml

# Update docker-compose.yml
dc_path = 'deploy/docker/docker-compose.yml'

with open(dc_path, 'r') as f:
    dc = yaml.safe_load(f)

if 'otel-collector' not in dc.get('services', {}):
    dc['services']['otel-collector'] = {
        'image': 'otel/opentelemetry-collector-contrib:latest',
        'command': ['--config=/etc/otelcol/config.yaml'],
        'volumes': ['../../config/otel-collector-config.yaml:/etc/otelcol/config.yaml'],
        'ports': ['4317:4317', '4318:4318', '8889:8889'],
        'depends_on': ['prometheus', 'loki', 'tempo']
    }
    dc['services']['prometheus'] = {
        'image': 'prom/prometheus:latest',
        'volumes': ['../../config/prometheus.yml:/etc/prometheus/prometheus.yml'],
        'ports': ['9090:9090']
    }
    dc['services']['loki'] = {
        'image': 'grafana/loki:latest',
        'ports': ['3100:3100']
    }
    dc['services']['tempo'] = {
        'image': 'grafana/tempo:latest',
        'command': ['-config.file=/etc/tempo.yaml'],
        'ports': ['3200:3200', '4317']
    }
    dc['services']['grafana'] = {
        'image': 'grafana/grafana:latest',
        'ports': ['3000:3000'],
        'volumes': [
            '../../config/grafana/provisioning:/etc/grafana/provisioning',
            '../../config/grafana/dashboards:/var/lib/grafana/dashboards'
        ],
        'environment': ['GF_AUTH_ANONYMOUS_ENABLED=true', 'GF_AUTH_ANONYMOUS_ORG_ROLE=Admin']
    }

    # Add environment variables to all our C# services
    for s in dc['services']:
        if s not in ['postgres', 'redis', 'rabbitmq', 'otel-collector', 'prometheus', 'loki', 'tempo', 'grafana']:
            if 'environment' not in dc['services'][s]:
                dc['services'][s]['environment'] = []
            elif isinstance(dc['services'][s]['environment'], dict):
                env_list = [f"{k}={v}" for k, v in dc['services'][s]['environment'].items()]
                dc['services'][s]['environment'] = env_list
            dc['services'][s]['environment'].append('OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317')

with open(dc_path, 'w') as f:
    yaml.dump(dc, f, sort_keys=False)


# Update C# Programs to include Telemetry
cs_files = [
    ("src/ControlService/Program.cs", "ControlService"),
    ("src/OrderService/Program.cs", "OrderService"),
    ("src/ProductService/Program.cs", "ProductService"),
    ("src/DependencyService/Program.cs", "DependencyService"),
    ("src/NotificationService/Program.cs", "NotificationService"),
    ("src/Gateway/Program.cs", "Gateway")
]

for p, name in cs_files:
    if os.path.exists(p):
        with open(p, "r") as f:
            c = f.read()
        if "AddDevOpsLabsTelemetry" not in c:
            if "using DevOpsLabs.Chaos.Observability;" not in c:
                c = "using DevOpsLabs.Chaos.Observability;\n" + c
            c = c.replace("var builder = WebApplication.CreateBuilder(args);", f'var builder = WebApplication.CreateBuilder(args);\nbuilder.Logging.ClearProviders();\nbuilder.Logging.AddDevOpsLabsLogging("{name}");\nbuilder.Services.AddDevOpsLabsTelemetry("{name}");')
            with open(p, "w") as f:
                f.write(c)

