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