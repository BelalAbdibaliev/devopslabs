import os

# 1. Fix OTel Collector config
otel_config = "config/otel-collector-config.yaml"
with open(otel_config, "r") as f:
    content = f.read()

# Replace loki exporter
content = content.replace(
"""  loki:
    endpoint: "http://loki:3100/loki/api/v1/push\"""",
"""  otlphttp/loki:
    endpoint: "http://loki:3100/otlp\""""
)
content = content.replace("exporters: [loki]", "exporters: [otlphttp/loki]")

with open(otel_config, "w") as f:
    f.write(content)

# 2. Fix TelemetryExtensions.cs to use SimpleConsole and enable HttpLogging
telemetry_cs = "src/Shared/DevOpsLabs.Chaos/Observability/TelemetryExtensions.cs"
with open(telemetry_cs, "r") as f:
    cs_content = f.read()

# Replace JsonConsole with SimpleConsole
cs_content = cs_content.replace(
"""        builder.AddJsonConsole(options => {
            options.IncludeScopes = true;
            options.TimestampFormat = "yyyy-MM-dd HH:mm:ss.fff ";
        });""",
"""        builder.AddSimpleConsole(options => {
            options.IncludeScopes = true;
            options.SingleLine = true;
            options.TimestampFormat = "[HH:mm:ss] ";
        });"""
)

with open(telemetry_cs, "w") as f:
    f.write(cs_content)

# 3. Add app.UseHttpLogging() in all Program.cs files
import glob
for p in glob.glob("src/*/Program.cs"):
    with open(p, "r") as f:
        prog = f.read()
    if "app.UseHttpLogging()" not in prog:
        # Insert after var app = builder.Build();
        prog = prog.replace("var app = builder.Build();", "var app = builder.Build();\napp.UseHttpLogging();")
        with open(p, "w") as f:
            f.write(prog)

