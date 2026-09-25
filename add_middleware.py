import re

code = """
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Http;
using System.Diagnostics;
using System.Collections.Generic;

namespace DevOpsLabs.Chaos.Observability;

public class MetricsMiddleware
{
    private readonly RequestDelegate _next;
    public MetricsMiddleware(RequestDelegate next) => _next = next;
    
    public async Task InvokeAsync(HttpContext context)
    {
        var sw = Stopwatch.StartNew();
        try {
            await _next(context);
        } finally {
            sw.Stop();
            var tags = new KeyValuePair<string, object?>("path", context.Request.Path.Value);
            DevOpsLabsMetrics.RequestsTotal.Add(1, tags);
            DevOpsLabsMetrics.RequestDuration.Record(sw.ElapsedMilliseconds, tags);
        }
    }
}

public static class MetricsMiddlewareExtensions
{
    public static IApplicationBuilder UseDevOpsLabsMetrics(this IApplicationBuilder builder)
    {
        return builder.UseMiddleware<MetricsMiddleware>();
    }
}
"""
with open("src/Shared/DevOpsLabs.Chaos/Observability/MetricsMiddleware.cs", "w") as f:
    f.write(code.strip())

cs_files = [
    "src/ControlService/Program.cs",
    "src/OrderService/Program.cs",
    "src/ProductService/Program.cs",
    "src/DependencyService/Program.cs",
    "src/Gateway/Program.cs"
]

for p in cs_files:
    import os
    if os.path.exists(p):
        with open(p, "r") as f:
            c = f.read()
        if "app.UseDevOpsLabsMetrics();" not in c:
            c = c.replace("var app = builder.Build();", "var app = builder.Build();\napp.UseDevOpsLabsMetrics();")
            with open(p, "w") as f:
                f.write(c)
