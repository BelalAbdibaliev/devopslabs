using Npgsql;
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
        builder.AddSimpleConsole(options => {
            options.IncludeScopes = true;
            options.SingleLine = true;
            options.TimestampFormat = "[HH:mm:ss] ";
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