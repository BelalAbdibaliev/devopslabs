import os
import re

files = {
    "config/otel-collector-config.yaml": """
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

exporters:
  prometheus:
    endpoint: "0.0.0.0:8889"
    namespace: devops_lab
    send_timestamps: true
  loki:
    endpoint: "http://loki:3100/loki/api/v1/push"
  otlp/tempo:
    endpoint: "tempo:4317"
    tls:
      insecure: true

processors:
  batch:

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [otlp/tempo]
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus]
    logs:
      receivers: [otlp]
      processors: [batch]
      exporters: [loki]
""",
    "config/prometheus.yml": """
global:
  scrape_interval: 5s

scrape_configs:
  - job_name: 'otel-collector'
    static_configs:
      - targets: ['otel-collector:8889']
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
""",
    "config/grafana/provisioning/datasources/datasources.yaml": """
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    isDefault: true
    access: proxy
  - name: Loki
    type: loki
    url: http://loki:3100
    access: proxy
  - name: Tempo
    type: tempo
    url: http://tempo:3200
    access: proxy
""",
    "config/grafana/provisioning/dashboards/dashboards.yaml": """
apiVersion: 1
providers:
  - name: 'Dashboards'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    options:
      path: /var/lib/grafana/dashboards
""",
    "config/grafana/dashboards/system-overview.json": """
{
  "title": "System Overview",
  "panels": [
    {
      "type": "timeseries",
      "title": "HTTP Requests (RPS)",
      "targets": [{"expr": "rate(http_server_request_duration_seconds_count[1m])", "legendFormat": "{{service.name}}"}],
      "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8}
    },
    {
      "type": "timeseries",
      "title": "Request Duration (P95)",
      "targets": [{"expr": "histogram_quantile(0.95, rate(http_server_request_duration_seconds_bucket[1m]))", "legendFormat": "{{service.name}}"}],
      "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8}
    },
    {
      "type": "timeseries",
      "title": "Active Chaos Scenarios",
      "targets": [{"expr": "devops_lab_active_scenarios", "legendFormat": "Scenarios"}],
      "gridPos": {"x": 0, "y": 8, "w": 12, "h": 8}
    },
    {
      "type": "timeseries",
      "title": "Process CPU Usage",
      "targets": [{"expr": "process_cpu_time_seconds_total", "legendFormat": "{{service.name}}"}],
      "gridPos": {"x": 12, "y": 8, "w": 12, "h": 8}
    }
  ]
}
""",
    "src/Shared/DevOpsLabs.Chaos/Observability/TelemetryExtensions.cs": """
using System.Diagnostics;
using System.Diagnostics.Metrics;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Logging;
using OpenTelemetry;
using OpenTelemetry.Logs;
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;

namespace DevOpsLabs.Chaos.Observability;

public static class DevOpsLabsMetrics
{
    public static readonly Meter Meter = new("DevOpsLabs.Metrics", "1.0");
    public static readonly Counter<long> RequestsTotal = Meter.CreateCounter<long>("devops_lab.requests.total");
    public static readonly Histogram<double> RequestDuration = Meter.CreateHistogram<double>("devops_lab.request.duration");
    public static readonly ObservableGauge<int> ActiveScenarios = Meter.CreateObservableGauge("devops_lab.active_scenarios", () => GetActiveScenarios());
    public static readonly ObservableGauge<int> QueueDepth = Meter.CreateObservableGauge("devops_lab.queue_depth", () => GetQueueDepth());

    private static int _activeScenariosCount = 0;
    public static void SetActiveScenarios(int count) => _activeScenariosCount = count;
    private static int GetActiveScenarios() => _activeScenariosCount;

    private static int _queueDepth = 0;
    public static void SetQueueDepth(int count) => _queueDepth = count;
    private static int GetQueueDepth() => _queueDepth;
}

public static class TelemetryExtensions
{
    public static IServiceCollection AddDevOpsLabsTelemetry(this IServiceCollection services, string serviceName)
    {
        var otlpEndpoint = Environment.GetEnvironmentVariable("OTEL_EXPORTER_OTLP_ENDPOINT") ?? "http://localhost:4317";
        
        services.AddOpenTelemetry()
            .ConfigureResource(r => r.AddService(serviceName))
            .WithMetrics(metrics => metrics
                .AddAspNetCoreInstrumentation()
                .AddHttpClientInstrumentation()
                .AddRuntimeInstrumentation()
                .AddProcessInstrumentation()
                .AddMeter("DevOpsLabs.Metrics")
                .AddOtlpExporter(o => { o.Endpoint = new Uri(otlpEndpoint); }))
            .WithTracing(tracing => tracing
                .AddAspNetCoreInstrumentation()
                .AddHttpClientInstrumentation()
                .AddNpgsql()
                .AddSource("RabbitMQ.Client")
                .AddSource(serviceName)
                .AddOtlpExporter(o => { o.Endpoint = new Uri(otlpEndpoint); }));

        return services;
    }

    public static ILoggingBuilder AddDevOpsLabsLogging(this ILoggingBuilder builder, string serviceName)
    {
        var otlpEndpoint = Environment.GetEnvironmentVariable("OTEL_EXPORTER_OTLP_ENDPOINT") ?? "http://localhost:4317";
        builder.AddJsonConsole(options => {
            options.IncludeScopes = true;
            options.TimestampFormat = "yyyy-MM-dd HH:mm:ss.fff ";
        });
        builder.AddOpenTelemetry(options => {
            options.IncludeFormattedMessage = true;
            options.IncludeScopes = true;
            options.SetResourceBuilder(ResourceBuilder.CreateDefault().AddService(serviceName));
            options.AddOtlpExporter(o => o.Endpoint = new Uri(otlpEndpoint));
        });
        return builder;
    }
}
"""
}

for k, v in files.items():
    os.makedirs(os.path.dirname(k), exist_ok=True)
    with open(k, 'w') as f:
        f.write(v.strip())

# Update docker-compose.yml
import yaml

with open('docker-compose.yml', 'r') as f:
    dc = yaml.safe_load(f)

if 'otel-collector' not in dc.get('services', {}):
    dc['services']['otel-collector'] = {
        'image': 'otel/opentelemetry-collector-contrib:latest',
        'command': ['--config=/etc/otelcol/config.yaml'],
        'volumes': ['./config/otel-collector-config.yaml:/etc/otelcol/config.yaml'],
        'ports': ['4317:4317', '4318:4318', '8889:8889'],
        'depends_on': ['prometheus', 'loki', 'tempo']
    }
    dc['services']['prometheus'] = {
        'image': 'prom/prometheus:latest',
        'volumes': ['./config/prometheus.yml:/etc/prometheus/prometheus.yml'],
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
            './config/grafana/provisioning:/etc/grafana/provisioning',
            './config/grafana/dashboards:/var/lib/grafana/dashboards'
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

with open('docker-compose.yml', 'w') as f:
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
            # Add usings
            if "using DevOpsLabs.Chaos.Observability;" not in c:
                c = "using DevOpsLabs.Chaos.Observability;\n" + c
            # Replace builder
            c = c.replace("var builder = WebApplication.CreateBuilder(args);", f'var builder = WebApplication.CreateBuilder(args);\nbuilder.Logging.ClearProviders();\nbuilder.Logging.AddDevOpsLabsLogging("{name}");\nbuilder.Services.AddDevOpsLabsTelemetry("{name}");')
            with open(p, "w") as f:
                f.write(c)

